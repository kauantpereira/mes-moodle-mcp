"""Acesso ao Moodle para as tools: um cliente por processo e erros já traduzidos para o agente.

O núcleo recebe só URL + token (ADR-0009):
- URL: variável MOODLE_URL (preenchida pelo plugin a partir de `moodle_url`).
- Token: por enquanto a variável MOODLE_TOKEN. O chaveiro do sistema e o login
  (ADR-0002) entram nas tarefas de login; elas só trocam `obter_token`.
"""

import os
from collections.abc import Callable
from typing import Any

import httpx
from mcp.server.mcpserver.exceptions import ToolError

from .client import FuncaoNaoPermitida, MoodleClient, MoodleError


def _token_do_ambiente(base_url: str) -> str | None:
    return os.environ.get("MOODLE_TOKEN")


obter_token: Callable[[str], str | None] = _token_do_ambiente
_cliente: MoodleClient | None = None


def cliente() -> MoodleClient:
    global _cliente
    if _cliente is None:
        url = os.environ.get("MOODLE_URL", "").strip()
        if not url:
            raise ToolError("MOODLE_URL não configurada: informe o endereço do Moodle na instalação do plugin.")
        token = obter_token(url.rstrip("/"))
        if not token:
            raise ToolError("Sem token do Moodle. Faça o login antes de usar as tools.")
        try:
            _cliente = MoodleClient(url, token)
        except ValueError as exc:
            raise ToolError(f"Configuração do Moodle inválida: {exc}.") from exc
    return _cliente


def _reiniciar() -> None:
    """Só para testes: esquece o cliente atual."""
    global _cliente
    _cliente = None


async def chamar(wsfunction: str, **params: Any) -> Any:
    """Chama uma função de leitura e devolve ToolError com mensagem útil (sem token nem debuginfo)."""
    c = cliente()
    try:
        return await c.call(wsfunction, **params)
    except FuncaoNaoPermitida as exc:
        raise ToolError(f"Função bloqueada pela regra de só leitura: {exc}.") from exc
    except MoodleError as exc:
        dica = " O token expirou ou foi revogado; faça o login de novo." if exc.errorcode == "invalidtoken" else ""
        raise ToolError(f"O Moodle recusou {wsfunction}: {exc} ({exc.errorcode}).{dica}") from exc
    except httpx.HTTPError as exc:
        raise ToolError(f"Falha de conexão com {c.base_url}: {type(exc).__name__}.") from exc
