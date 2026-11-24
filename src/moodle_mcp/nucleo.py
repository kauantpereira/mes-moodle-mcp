"""Acesso ao Moodle para as tools: um cliente por processo, login sob demanda e erros já traduzidos.

O núcleo recebe só URL + token (ADR-0009):
- URL: variável MOODLE_URL (preenchida pelo plugin a partir de `moodle_url`).
- Token (`obter_token`): MOODLE_TOKEN, se definida (provisório, tem prioridade); senão o
  chaveiro do sistema, com a URL base como chave (ADR-0002, ADR-0016).
- Sem token, a primeira tool chamada faz o login e continua a resposta (`chamar`); a tool
  `entrar` refaz o login (troca de conta ou token expirado). O método vem do perfil da
  instituição (`perfil_para(url).login`) ou do login genérico (`login.login_generico`).
  Pelo chat, só o login que abre o navegador funciona; senha e link colado ficam no terminal.
"""

import asyncio
import os
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

import httpx
from mcp.server.mcpserver.exceptions import ToolError

from . import chaveiro, login
from .client import FuncaoNaoPermitida, MoodleClient, MoodleError, _url_segura
from .limite import LimiteAtingido
from .manutencao import EmManutencao
from .perfis import perfil_para


def _token_guardado(base_url: str) -> str | None:
    return os.environ.get("MOODLE_TOKEN") or chaveiro.ler(base_url)


obter_token: Callable[[str], str | None] = _token_guardado
_cliente: MoodleClient | None = None
_token_atual: str | None = None  # token do `_cliente`, para notar um login feito no terminal
_trava: asyncio.Lock | None = None
# Contexto MCP da tool em execução (posto pelo servidor), para o login sob demanda mandar avisos de progresso.
_contexto: ContextVar[Any] = ContextVar("moodle_mcp_contexto", default=None)
# Só para testes: transporte simulado dos clientes criados pelo login.
_transporte: httpx.AsyncBaseTransport | None = None


@contextmanager
def contexto_da_chamada(ctx: Any) -> Iterator[None]:
    marca = _contexto.set(ctx)
    try:
        yield
    finally:
        _contexto.reset(marca)


def _url() -> str:
    url = os.environ.get("MOODLE_URL", "").strip()
    if not url:
        raise ToolError("MOODLE_URL não configurada: informe o endereço do Moodle na instalação do plugin.")
    return url.rstrip("/")


def _novo_cliente(url: str, token: str) -> MoodleClient:
    # Trocar de conta não zera o limite de chamadas do processo (ADR-0005).
    limitador = _cliente.limitador if _cliente is not None else None
    try:
        return MoodleClient(url, token, transport=_transporte, limitador=limitador)
    except ValueError as exc:
        raise ToolError(f"Configuração do Moodle inválida: {exc}.") from exc


def cliente() -> MoodleClient:
    global _cliente, _token_atual
    if _cliente is None:
        url = _url()
        token = obter_token(url)
        if not token:
            raise ToolError("Sem token do Moodle. Use a tool `entrar` para fazer login.")
        _cliente, _token_atual = _novo_cliente(url, token), token
    return _cliente


def metodo_de_login(base_url: str) -> login.Login:
    """Login do perfil da instituição, se houver; senão o genérico (senha ou fluxo do app)."""
    return perfil_para(base_url).login or login.login_generico


async def _trocar(novo: MoodleClient, token: str) -> None:
    global _cliente, _token_atual
    antigo, _cliente, _token_atual = _cliente, novo, token
    if antigo is not None:
        await antigo.aclose()


async def entrar(interacao: login.Interacao | None = None, manual: bool = False) -> dict[str, Any]:
    """Faz o login, confere o token no Moodle e guarda no chaveiro. Troca o cliente atual.

    `manual`: força o fluxo do app com o link colado (`moodle-mcp entrar --manual`).
    """
    url = _url()
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
    await _trocar(novo, token)
    return {"conectado": True, "token_no_chaveiro": guardado}


async def _cliente_com_login() -> MoodleClient:
    """O cliente atual; sem token, faz o login primeiro (uma vez, mesmo com tools em paralelo)."""
    global _trava
    if _cliente is not None:
        if _token_atual is not None and not os.environ.get("MOODLE_TOKEN"):
            guardado = chaveiro.ler(_cliente.base_url)
            if guardado and guardado != _token_atual:
                # Login feito no terminal (`moodle-mcp entrar`) com o servidor rodando: usa o token novo.
                await _trocar(_novo_cliente(_cliente.base_url, guardado), guardado)
        return _cliente
    if obter_token(_url()):
        return cliente()
    if _trava is None:
        _trava = asyncio.Lock()
    async with _trava:
        if _cliente is None:
            await entrar()
    return cliente()


def _reiniciar() -> None:
    """Só para testes: esquece o cliente atual."""
    global _cliente, _token_atual, _trava
    _cliente = None
    _token_atual = None
    _trava = None


def _duracao(segundos: int) -> str:
    if segundos < 60:
        return f"{segundos} s"
    minutos = -(-segundos // 60)
    return f"{minutos} min"


async def chamar(wsfunction: str, **params: Any) -> Any:
    """Chama uma função de leitura e devolve ToolError com mensagem útil (sem token nem debuginfo)."""
    c = await _cliente_com_login()
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
