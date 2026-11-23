"""Cliente da API REST de Web Services do Moodle.

Núcleo agnóstico de instituição (ADR-0009): recebe só URL + token. Login, chaveiro e
URLs por semestre ficam fora daqui (perfis e #22/#23).

Garantias deste módulo:
- só chama funções da lista FUNCOES_PERMITIDAS, todas de leitura (regra 1);
- o token vai no corpo do POST, nunca na URL, e não aparece em mensagens de erro;
- token só trafega por HTTPS (HTTP apenas para um Moodle local, em localhost);
- downloads só do host do próprio Moodle, inclusive nos redirecionamentos.
"""

from typing import Any
from urllib.parse import urlsplit

import httpx

TIMEOUT = httpx.Timeout(30.0)
HOSTS_LOCAIS = {"localhost", "127.0.0.1", "::1"}

# Regra 1 (só leitura): toda função nova entra aqui junto com a tool que a usa, no mesmo PR.
FUNCOES_PERMITIDAS = frozenset(
    {
        "core_webservice_get_site_info",
        "core_enrol_get_users_courses",
        "core_course_get_contents",
        "core_course_get_updates_since",
        "core_calendar_get_action_events_by_timesort",
        "mod_assign_get_assignments",
        "mod_assign_get_submission_status",
        "gradereport_user_get_grade_items",
    }
)


class MoodleError(Exception):
    """Erro devolvido pelo Moodle (token inválido, permissão negada etc.)."""

    def __init__(self, errorcode: str, message: str):
        super().__init__(message)
        self.errorcode = errorcode


class FuncaoNaoPermitida(ValueError):
    """Função fora da lista de leitura: barrada antes de qualquer requisição."""


def _achatar(params: dict[str, Any], prefixo: str = "") -> dict[str, str]:
    """Converte listas/dicts no formato que o Moodle espera: courseids[0]=1, options[0][name]=..."""
    saida: dict[str, str] = {}
    for chave, valor in params.items():
        nome = f"{prefixo}[{chave}]" if prefixo else str(chave)
        if isinstance(valor, dict):
            saida.update(_achatar(valor, nome))
        elif isinstance(valor, (list, tuple)):
            saida.update(_achatar(dict(enumerate(valor)), nome))
        elif isinstance(valor, bool):
            saida[nome] = "1" if valor else "0"
        elif valor is not None:
            saida[nome] = str(valor)
    return saida


def _checar_erro(dados: Any) -> None:
    # Mensagens do servidor também são externas e podem conter dados sensíveis.
    if isinstance(dados, dict) and ("exception" in dados or "errorcode" in dados):
        codigo = dados.get("errorcode")
        if not isinstance(codigo, str) or not codigo.isascii() or not codigo.replace("_", "").isalnum():
            codigo = "erro"
        raise MoodleError(codigo, "resposta de erro do Moodle")


def _url_segura(url: str) -> bool:
    partes = urlsplit(url)
    return (partes.scheme == "https" or (partes.scheme == "http" and partes.hostname in HOSTS_LOCAIS)) and not (partes.username or partes.password or partes.query or partes.fragment)


class MoodleClient:
    def __init__(self, base_url: str, token: str, transport: httpx.AsyncBaseTransport | None = None):
        if not token:
            raise ValueError("token vazio")
        self.base_url = base_url.rstrip("/")
        if not _url_segura(self.base_url):
            raise ValueError("o Moodle precisa ser HTTPS (HTTP só em localhost)")
        self._token = token
        self._http = httpx.AsyncClient(timeout=TIMEOUT, transport=transport)
        self._site_info: dict[str, Any] | None = None

    def __repr__(self) -> str:  # nunca expor o token
        return f"MoodleClient({self.base_url!r})"

    async def call(self, wsfunction: str, **params: Any) -> Any:
        if wsfunction not in FUNCOES_PERMITIDAS:
            raise FuncaoNaoPermitida(f"{wsfunction} não está na lista de funções de leitura")
        resp = await self._http.post(
            f"{self.base_url}/webservice/rest/server.php",
            params={"moodlewsrestformat": "json", "wsfunction": wsfunction},
            data={"wstoken": self._token, **_achatar(params)},
        )
        resp.raise_for_status()
        dados = resp.json()
        _checar_erro(dados)
        return dados

    async def site_info(self) -> dict[str, Any]:
        if self._site_info is None:
            self._site_info = await self.call("core_webservice_get_site_info")
        return self._site_info

    async def userid(self) -> int:
        return (await self.site_info())["userid"]

    async def baixar(self, fileurl: str, limite_bytes: int) -> bytes:
        """Baixa um arquivo do próprio Moodle. O token é anexado aqui e nunca sai deste método.

        Só aceita URLs do mesmo host do Moodle (inclusive nos redirecionamentos).
        Levanta ValueError (mensagem sem URL) se o host for outro ou o arquivo passar do limite.
        """
        base = urlsplit(self.base_url)
        url = fileurl
        try:
            for _ in range(4):
                partes = urlsplit(url)
                if partes.scheme != base.scheme or partes.netloc != base.netloc or partes.username or partes.password:
                    raise ValueError("o arquivo está fora do host do Moodle")
                async with self._http.stream("GET", url, params={"token": self._token}, follow_redirects=False) as resp:
                    if resp.is_redirect:
                        url = str(resp.url.join(resp.headers.get("location", "")))
                        url = url.split("?token=")[0].split("&token=")[0]
                        continue
                    if resp.is_error:
                        raise ValueError("o Moodle recusou o download")
                    if int(resp.headers.get("content-length") or 0) > limite_bytes:
                        raise ValueError("arquivo grande demais")
                    dados = bytearray()
                    async for pedaco in resp.aiter_bytes():
                        dados += pedaco
                        if len(dados) > limite_bytes:
                            raise ValueError("arquivo grande demais")
                    return bytes(dados)
        except httpx.HTTPError as exc:
            raise ValueError("falha de transporte ao baixar arquivo") from None
        raise ValueError("redirecionamentos demais")

    async def aclose(self) -> None:
        await self._http.aclose()
