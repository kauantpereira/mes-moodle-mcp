"""Login genérico no Moodle (ADR-0002, ADR-0016). Só API padrão do Moodle, nada de instituição.

Dois caminhos, ambos com o serviço `moodle_mobile_app` (o do app oficial):
- **senha**: `login/token.php` com usuário e senha, para Moodle sem SSO (ex.: Moodle local).
  A senha só existe durante a requisição: nunca é guardada nem registrada.
- **fluxo do app** (`admin/tool/mobile/launch.php`): o aluno entra no navegador (inclusive por
  SSO) e o Moodle devolve `moodlemobile://token=...`. No genérico, o aluno cola esse link num
  formulário (login manual); um perfil de instituição pode automatizar a captura (ex.: navegador).

A conversa com o aluno passa por uma `Interacao`: formulário do cliente MCP (elicitation) ou
terminal (`moodle-mcp entrar`). Senha, link e token nunca passam pelo chat nem pelo modelo.

Contrato do login de um perfil (`Perfil.login`): `async (base_url, interacao) -> token`,
levantando `LoginFalhou` com mensagem segura (sem senha, token nem texto cru do Moodle).
"""

import base64
import binascii
import hashlib
import re
import secrets
from collections.abc import Awaitable, Callable
from typing import Any, Literal, Protocol
from urllib.parse import urlencode

import httpx
from mcp.shared.exceptions import NoBackChannelError
from pydantic import BaseModel, Field

from .client import _url_segura

SERVICO_APP = "moodle_mobile_app"
ESQUEMA_APP = "moodlemobile"
TIMEOUT = httpx.Timeout(30.0)
# Só para testes: transporte simulado do login por senha.
transporte: httpx.AsyncBaseTransport | None = None

_RE_TOKEN = re.compile(r"[A-Za-z0-9_-]{8,256}")


class LoginFalhou(Exception):
    """Falha de login com mensagem pronta para o aluno (sem dado sensível)."""


class Interacao(Protocol):
    """Como o login conversa com o aluno. Cada método devolve None se o aluno cancelar."""

    pode_perguntar: bool

    async def avisar(self, mensagem: str) -> None: ...

    async def escolher_metodo(self, mensagem: str) -> Literal["senha", "app"] | None: ...

    async def pedir_credenciais(self, mensagem: str) -> tuple[str, str] | None: ...

    async def pedir_link(self, mensagem: str) -> str | None: ...


Login = Callable[[str, Interacao], Awaitable[str]]


# ---------- fluxo do app (launch.php) ----------


def novo_passport() -> str:
    return secrets.token_hex(8)


def url_de_lancamento(base_url: str, passport: str) -> str:
    """URL que o app oficial abre no navegador para o login (inclusive SSO)."""
    query = urlencode({"service": SERVICO_APP, "passport": passport, "urlscheme": ESQUEMA_APP})
    return f"{base_url.rstrip('/')}/admin/tool/mobile/launch.php?{query}"


def decodificar_token_do_app(base_url: str, passport: str, link: str) -> str:
    """Extrai e confere o token de `moodlemobile://token=<base64>`.

    O conteúdo é base64("<assinatura>:::<token>[:::<token privado>]"), com assinatura =
    md5(wwwroot + passport). O md5 é só o formato do Moodle para provar que a resposta é
    deste login (o passport é aleatório e novo a cada tentativa), não um hash de senha.
    """
    valor = (link or "").strip()
    if "token=" in valor:
        valor = valor.split("token=", 1)[1]
    valor = valor.split("#", 1)[0].strip()
    try:
        partes = base64.b64decode(valor + "=" * (-len(valor) % 4), validate=False).decode().split(":::")
    except (binascii.Error, UnicodeDecodeError, ValueError):
        raise LoginFalhou("O link não é um moodlemobile://token=... válido.") from None
    if len(partes) < 2:
        raise LoginFalhou("O link não é um moodlemobile://token=... válido.")
    esperado = hashlib.md5((base_url.rstrip("/") + passport).encode()).hexdigest()
    if not secrets.compare_digest(partes[0].encode(), esperado.encode()):
        raise LoginFalhou("O link não corresponde a este login (assinatura diferente). Gere um novo.")
    if not _RE_TOKEN.fullmatch(partes[1]):
        raise LoginFalhou("O link não trouxe um token válido.")
    return partes[1]


_INSTRUCOES_MANUAIS = (
    "1. No navegador, abra as ferramentas de desenvolvedor (F12), aba Rede/Network, e marque "
    "\"Preservar log\"/\"Preserve log\".\n"
    "2. Na mesma aba, abra o link abaixo e faça o login normalmente:\n   {url}\n"
    "3. Na última requisição launch.php, copie o valor de Location (moodlemobile://token=...); "
    "se não houver, procure moodlemobile://token= no Console.\n"
    "4. Cole o link aqui. Ele vai direto para o servidor, não para o chat."
)


async def login_manual(base_url: str, interacao: Interacao) -> str:
    """Fluxo do app com o link colado pelo aluno (reserva de qualquer login por navegador)."""
    passport = novo_passport()
    link = await interacao.pedir_link(_INSTRUCOES_MANUAIS.format(url=url_de_lancamento(base_url, passport)))
    if not link:
        raise LoginFalhou("Login cancelado.")
    return decodificar_token_do_app(base_url, passport, link)


# ---------- senha (login/token.php) ----------

_ERROS_TOKEN_PHP = {
    "invalidlogin": "Usuário ou senha incorretos.",
    "enablewsdescription": "Este Moodle não libera o acesso pelo app (web services desativados). Fale com o suporte da instituição.",
    "servicenotavailable": "Este Moodle não libera o serviço do app (moodle_mobile_app). Fale com o suporte da instituição.",
    "sitemaintenance": "O Moodle está em manutenção. Tente mais tarde.",
    "usernotfullysetup": "Sua conta no Moodle tem cadastro pendente: entre uma vez pelo navegador e complete-o.",
}


async def login_senha(base_url: str, usuario: str, senha: str) -> str:
    """Token por `login/token.php` (não é função de web service; não entra em FUNCOES_PERMITIDAS).

    Mesmas garantias do cliente: só HTTPS (HTTP só em localhost), sem seguir redirecionamentos,
    e nenhuma mensagem com senha, token, URL ou texto cru do Moodle.
    """
    base = base_url.rstrip("/")
    if not _url_segura(base):
        raise LoginFalhou("O Moodle precisa ser HTTPS (HTTP só em localhost) para enviar a senha.")
    if not usuario or not senha:
        raise LoginFalhou("Informe usuário e senha.")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, transport=transporte, follow_redirects=False) as http:
            resp = await http.post(
                f"{base}/login/token.php",
                data={"username": usuario, "password": senha, "service": SERVICO_APP},
            )
        if resp.is_redirect or resp.is_error:
            raise LoginFalhou("O Moodle recusou o login por senha (o site pode usar só SSO).")
        dados: Any = resp.json()
    except httpx.HTTPError:
        raise LoginFalhou("Falha de conexão com o Moodle.") from None
    except ValueError:
        raise LoginFalhou("Resposta inesperada do Moodle ao login.") from None
    if not isinstance(dados, dict):
        raise LoginFalhou("Resposta inesperada do Moodle ao login.")
    token = dados.get("token")
    if isinstance(token, str) and _RE_TOKEN.fullmatch(token):
        return token
    codigo = dados.get("errorcode")
    raise LoginFalhou(_ERROS_TOKEN_PHP.get(codigo, "O Moodle recusou o login por senha.") if isinstance(codigo, str) else "O Moodle recusou o login por senha.")


async def login_por_senha(base_url: str, interacao: Interacao) -> str:
    credenciais = await interacao.pedir_credenciais(
        f"Entrar no Moodle {base_url} com usuário e senha. "
        "A senha vai direto para o Moodle (login/token.php): não é guardada, registrada nem enviada ao chat."
    )
    if not credenciais:
        raise LoginFalhou("Login cancelado.")
    usuario, senha = credenciais
    return await login_senha(base_url, usuario.strip(), senha)


# ---------- genérico ----------


async def login_generico(base_url: str, interacao: Interacao) -> str:
    """Login de um Moodle sem perfil: o aluno escolhe senha ou fluxo do app (manual).

    O genérico não adivinha o tipo de login do site: o aluno sabe se entra com usuário e senha
    do Moodle ou pelo login da instituição (SSO). Ver ADR-0016.
    """
    if not interacao.pode_perguntar:
        raise LoginFalhou(SEM_FORMULARIO)
    metodo = await interacao.escolher_metodo(
        f"Como você entra no Moodle {base_url}? "
        "\"senha\": usuário e senha do próprio Moodle. "
        "\"app\": login da instituição (SSO) no navegador, colando o link que o Moodle devolve."
    )
    if metodo == "senha":
        return await login_por_senha(base_url, interacao)
    if metodo == "app":
        return await login_manual(base_url, interacao)
    raise LoginFalhou("Login cancelado.")


COMANDO_TERMINAL = "uvx --from git+https://github.com/kauantpereira/mes-moodle-mcp moodle-mcp entrar --url <endereço do Moodle>"
SEM_FORMULARIO = (
    "Este cliente MCP não mostra formulários de login no meio da tool (elicitation), então o login não pode ser feito por aqui. "
    f"Entre pelo terminal: `{COMANDO_TERMINAL}`. O token fica no chaveiro do sistema e o servidor passa a usá-lo."
)


# ---------- interação pelo cliente MCP (elicitation de formulário) ----------


class _Metodo(BaseModel):
    metodo: Literal["senha", "app"] = Field(title="Forma de login", description="senha = usuário e senha do Moodle; app = login da instituição no navegador")


class _Credenciais(BaseModel):
    usuario: str = Field(title="Usuário do Moodle")
    senha: str = Field(title="Senha", description="Enviada só ao Moodle; nunca guardada")


class _Link(BaseModel):
    link: str = Field(title="Link moodlemobile://token=...")


class InteracaoMCP:
    """Interação pelo cliente MCP: formulário (elicitation) e notificações de progresso.

    Sem contexto de requisição ou sem suporte do cliente a elicitation, `pode_perguntar` é False.
    """

    def __init__(self, ctx: Any | None):
        self._ctx = ctx
        self.pode_perguntar = self._suporta_formulario()

    def _suporta_formulario(self) -> bool:
        """Formulário no meio da tool: cliente com elicitation e protocolo até 2025-11-25.

        A partir de 2026-07-28 o MCP não manda pedidos do servidor no meio da tool: a pergunta
        vira `InputRequiredResult` e a tool é chamada de novo com as respostas (e o estado volta
        do cliente a cada rodada). Login com senha e espera longa não cabem nisso; nesses
        clientes o login vai pelo terminal (ADR-0016).
        """
        if self._ctx is None:
            return False
        try:
            from mcp_types import ClientCapabilities, ElicitationCapability
            from mcp_types.version import is_version_at_least

            versao = self._ctx.protocol_version
            if versao is None or is_version_at_least(versao, "2026-07-28"):
                return False
            sessao = self._ctx.request_context.session
            return bool(sessao.check_client_capability(ClientCapabilities(elicitation=ElicitationCapability())))
        except Exception:
            return False

    async def avisar(self, mensagem: str) -> None:
        if self._ctx is None:
            return
        try:
            await self._ctx.report_progress(0, None, mensagem)
        except Exception:
            pass

    async def _pedir(self, mensagem: str, modelo: type[BaseModel]) -> BaseModel | None:
        if not self.pode_perguntar:
            raise LoginFalhou(SEM_FORMULARIO)
        try:
            resultado = await self._ctx.elicit(mensagem, modelo)
        except NoBackChannelError:
            raise LoginFalhou(SEM_FORMULARIO) from None
        except ValueError:  # cliente aceitou com conteúdo fora do formato
            raise LoginFalhou("O formulário voltou incompleto. Tente de novo.") from None
        return resultado.data if resultado.action == "accept" else None

    async def escolher_metodo(self, mensagem: str) -> Literal["senha", "app"] | None:
        dados = await self._pedir(mensagem, _Metodo)
        return dados.metodo if dados else None  # type: ignore[attr-defined]

    async def pedir_credenciais(self, mensagem: str) -> tuple[str, str] | None:
        dados = await self._pedir(mensagem, _Credenciais)
        return (dados.usuario, dados.senha) if dados else None  # type: ignore[attr-defined]

    async def pedir_link(self, mensagem: str) -> str | None:
        dados = await self._pedir(mensagem, _Link)
        return dados.link if dados else None  # type: ignore[attr-defined]
