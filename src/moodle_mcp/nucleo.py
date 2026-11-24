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
from .limite import LimiteAtingido
from .manutencao import EmManutencao


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


def _duracao(segundos: int) -> str:
    if segundos < 60:
        return f"{segundos} s"
    minutos = -(-segundos // 60)
    return f"{minutos} min"


async def chamar(wsfunction: str, **params: Any) -> Any:
    """Chama uma função de leitura e devolve ToolError com mensagem útil (sem token nem debuginfo)."""
    c = cliente()
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
                "(ou, enquanto o login não estiver configurado, atualize a variável provisória MOODLE_TOKEN "
                "e reinicie o servidor)."
            )
        else:
            dica = ""
        raise ToolError(f"O Moodle recusou {wsfunction}.{dica}") from None
    except httpx.HTTPError as exc:
        raise ToolError("Falha de conexão com o Moodle.") from None
