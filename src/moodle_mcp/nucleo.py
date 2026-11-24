"""Acesso ao Moodle para as tools: um cliente por Moodle, login sob demanda e erros já traduzidos.

O núcleo recebe só URL + token (ADR-0009, ADR-0017):
- URL (`url_do_moodle`): a variável MOODLE_URL, se definida; senão o perfil padrão da instituição
  (`perfis.padrao()`) monta o endereço do semestre atual. Instituições com um Moodle por semestre
  aceitam o parâmetro `semestre` nas tools e a tool `usar_semestre` (vale até o servidor reiniciar);
  o formato do semestre é decidido pelo perfil.
- Token (`obter_token`): MOODLE_TOKEN, se definida (provisório, tem prioridade); senão o
  chaveiro do sistema, com a URL base como chave (ADR-0002, ADR-0016). Cada semestre é um Moodle
  separado, com token próprio.
- Sem token, a primeira tool chamada faz o login e continua a resposta (`chamar`); a tool
  `entrar` refaz o login (troca de conta ou token expirado). O método vem do perfil da
  instituição (`perfil_para(url).login`) ou do login genérico (`login.login_generico`).
  Pelo chat, só o login que abre o navegador funciona; senha e link colado ficam no terminal.
- O limite de chamadas (ADR-0005) é um só para o processo, somando todos os Moodles.
"""

import asyncio
import os
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

import httpx
from mcp.server.mcpserver.exceptions import ToolError

from . import chaveiro, login, perfis
from .client import FuncaoNaoPermitida, MoodleClient, MoodleError, _url_segura
from .limite import LimiteAtingido, Limitador
from .manutencao import EmManutencao
from .perfis import perfil_para


def _token_guardado(base_url: str) -> str | None:
    return os.environ.get("MOODLE_TOKEN") or chaveiro.ler(base_url)


obter_token: Callable[[str], str | None] = _token_guardado
_clientes: dict[str, MoodleClient] = {}  # um por Moodle (URL base)
_tokens: dict[str, str] = {}  # token de cada cliente, para notar um login feito no terminal
_travas: dict[str, asyncio.Lock] = {}
_limitador: Limitador | None = None  # compartilhado por todos os clientes (ADR-0005)
_url_da_sessao: str | None = None  # escolhida com `usar_semestre`; vale até o servidor reiniciar
# Contexto MCP da tool em execução (posto pelo servidor), para o login sob demanda mandar avisos de progresso.
_contexto: ContextVar[Any] = ContextVar("moodle_mcp_contexto", default=None)
# Só para testes: transporte simulado dos clientes criados pelo login.
_transporte: httpx.AsyncBaseTransport | None = None

SEM_ENDERECO = (
    "Endereço do Moodle não configurado: defina a variável MOODLE_URL com o endereço do seu Moodle "
    "(veja docs/referencia/configuracao.md)."
)


@contextmanager
def contexto_da_chamada(ctx: Any) -> Iterator[None]:
    marca = _contexto.set(ctx)
    try:
        yield
    finally:
        _contexto.reset(marca)


def _url_configurada() -> str | None:
    url = os.environ.get("MOODLE_URL", "").strip().rstrip("/")
    return url or None


def url_do_moodle(semestre: str | None = None) -> str:
    """URL base do Moodle a usar: a do `semestre` pedido, a da sessão, a configurada ou a padrão do perfil."""
    configurada = _url_configurada()
    if semestre is None:
        if _url_da_sessao is not None:
            return _url_da_sessao
        if configurada is not None:
            return configurada
    perfil = perfil_para(configurada) if configurada else perfis.padrao()
    if perfil is None or perfil.url_do_semestre is None:
        if semestre is None:
            raise ToolError(SEM_ENDERECO)
        raise ToolError("Este Moodle não separa as disciplinas por semestre: consulte sem o parâmetro `semestre`.")
    try:
        return perfil.url_do_semestre(semestre).rstrip("/")
    except ValueError as exc:
        raise ToolError(f"Semestre inválido: {exc}") from None


def _novo_cliente(url: str, token: str) -> MoodleClient:
    global _limitador
    try:
        novo = MoodleClient(url, token, transport=_transporte, limitador=_limitador)
    except ValueError as exc:
        raise ToolError(f"Configuração do Moodle inválida: {exc}.") from exc
    _limitador = novo.limitador  # trocar de conta ou de semestre não zera o limite (ADR-0005)
    return novo


def cliente(semestre: str | None = None) -> MoodleClient:
    """Cliente do Moodle do `semestre` (ou o da sessão), sem fazer login."""
    url = url_do_moodle(semestre)
    if url not in _clientes:
        token = obter_token(url)
        if not token:
            raise ToolError("Sem token do Moodle. Use a tool `entrar` para fazer login.")
        _clientes[url], _tokens[url] = _novo_cliente(url, token), token
    return _clientes[url]


def metodo_de_login(base_url: str) -> login.Login:
    """Login do perfil da instituição, se houver; senão o genérico (senha ou fluxo do app)."""
    return perfil_para(base_url).login or login.login_generico


async def _trocar(url: str, novo: MoodleClient, token: str) -> None:
    antigo = _clientes.get(url)
    _clientes[url], _tokens[url] = novo, token
    if antigo is not None and antigo is not novo:
        await antigo.aclose()


async def entrar(
    interacao: login.Interacao | None = None, manual: bool = False, semestre: str | None = None
) -> dict[str, Any]:
    """Faz o login, confere o token no Moodle e guarda no chaveiro. Troca o cliente daquele Moodle.

    `manual`: força o fluxo do app com o link colado (`moodle-mcp entrar --manual`).
    """
    url = url_do_moodle(semestre)
    if os.environ.get("MOODLE_TOKEN"):
        raise ToolError("MOODLE_TOKEN está definida no ambiente e tem prioridade: remova-a para entrar pelo login.")
    if not _url_segura(url):
        raise ToolError("Configuração do Moodle inválida: o Moodle precisa ser HTTPS (HTTP só em localhost).")
    if interacao is None:
        interacao = login.InteracaoMCP(_contexto.get())
    try:
        metodo = login.login_manual if manual else metodo_de_login(url)
        token = await metodo(url, interacao)
    except login.LoginFalhou as exc:
        raise ToolError(str(exc)) from None
    novo = _novo_cliente(url, token)
    try:
        await novo.site_info()  # só guarda um token que o Moodle aceita
    except LimiteAtingido as exc:
        await novo.aclose()
        raise ToolError(f"Limite de chamadas ao Moodle atingido. Tente de novo em {_duracao(exc.espera_s)}.") from None
    except (MoodleError, httpx.HTTPError, ValueError, KeyError):
        await novo.aclose()
        raise ToolError("O Moodle não aceitou o token do login. Tente entrar de novo.") from None
    guardado = chaveiro.salvar(url, token)
    await _trocar(url, novo, token)
    return {"conectado": True, "token_no_chaveiro": guardado}


async def cliente_com_login(semestre: str | None = None) -> MoodleClient:
    """O cliente do Moodle do `semestre`; sem token, faz o login primeiro (uma vez, mesmo com tools em paralelo)."""
    url = url_do_moodle(semestre)
    atual = _clientes.get(url)
    if atual is not None:
        if url in _tokens and not os.environ.get("MOODLE_TOKEN"):
            guardado = chaveiro.ler(url)
            if guardado and guardado != _tokens[url]:
                # Login feito no terminal (`moodle-mcp entrar`) com o servidor rodando: usa o token novo.
                await _trocar(url, _novo_cliente(url, guardado), guardado)
        return _clientes[url]
    if obter_token(url):
        return cliente(semestre)
    trava = _travas.setdefault(url, asyncio.Lock())
    async with trava:
        if url not in _clientes:
            await entrar(semestre=semestre)
    return cliente(semestre)


def usar_semestre(semestre: str) -> str:
    """Passa a usar o Moodle do `semestre` em todas as tools, até o servidor reiniciar. Devolve a URL."""
    global _url_da_sessao
    _url_da_sessao = url_do_moodle(semestre)  # com `semestre`, não depende da escolha anterior
    return _url_da_sessao


def _usar_cliente(c: MoodleClient) -> None:
    """Só para testes: usa um cliente pronto como o Moodle da sessão."""
    global _url_da_sessao
    _clientes[c.base_url] = c
    _url_da_sessao = c.base_url


def _reiniciar() -> None:
    """Só para testes: esquece clientes, tokens e o semestre escolhido."""
    global _limitador, _url_da_sessao
    _clientes.clear()
    _tokens.clear()
    _travas.clear()
    _limitador = None
    _url_da_sessao = None


def _duracao(segundos: int) -> str:
    if segundos < 60:
        return f"{segundos} s"
    minutos = -(-segundos // 60)
    return f"{minutos} min"


async def chamar(wsfunction: str, /, semestre: str | None = None, **params: Any) -> Any:
    """Chama uma função de leitura e devolve ToolError com mensagem útil (sem token nem debuginfo).

    `semestre`: consulta o Moodle de outro semestre só nesta chamada (perfis com Moodle por semestre).
    """
    c = await cliente_com_login(semestre)
    try:
        return await c.call(wsfunction, **params)
    except FuncaoNaoPermitida as exc:
        raise ToolError(f"Função bloqueada pela regra de só leitura: {exc}.") from exc
    except LimiteAtingido as exc:
        raise ToolError(
            f"Limite de {exc.maximo} chamadas ao Moodle a cada {_duracao(exc.janela_s)} atingido "
            f"(proteção da infraestrutura da instituição). Tente de novo em {_duracao(exc.espera_s)}."
        ) from None
    except EmManutencao as exc:
        raise ToolError(
            f"O Moodle está em manutenção das {exc.inicio:%H:%M} às {exc.fim:%H:%M} (horário {exc.fuso}). "
            f"Tente de novo a partir das {exc.fim:%H:%M}."
        ) from None
    except MoodleError as exc:
        if exc.errorcode == "invalidtoken":
            dica = (
                " O token expirou ou foi revogado. Entre de novo usando a tool `entrar` "
                "(se usa a variável provisória MOODLE_TOKEN, atualize-a e reinicie o servidor)."
            )
        else:
            dica = ""
        raise ToolError(f"O Moodle recusou {wsfunction}.{dica}") from None
    except httpx.HTTPError as exc:
        raise ToolError("Falha de conexão com o Moodle.") from None
