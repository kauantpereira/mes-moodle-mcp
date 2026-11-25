"""As fixtures do eval `evals/aviso-de-ia.md` são o que o servidor de fato devolve.

O eval mede se o agente respeita o aviso de IA (história #5). Se o texto do aviso ou o formato
das tools mudar, este teste falha e as fixtures precisam ser atualizadas, para o eval não medir o
agente contra uma resposta que o servidor não produz mais. O executor do eval monta o Moodle
sintético a partir das mesmas fixtures (`evals/executor/moodle_sintetico.py`).
"""

import asyncio
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from moodle_mcp import nucleo, server
from moodle_mcp.nao_confiavel import AVISO, AVISO_IA

_ARQUIVO = Path(__file__).resolve().parent.parent / "evals" / "executor" / "moodle_sintetico.py"
_spec = importlib.util.spec_from_file_location("moodle_sintetico", _ARQUIVO)
sintetico = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sintetico)

DE_TAREFA = [f for f in sintetico.fixtures() if sintetico.de_tarefa(f)]
CONTROLE = next(f for f in sintetico.fixtures() if f.get("modo") == "semana")


def _instalar(monkeypatch, dados: dict[str, Any]) -> None:
    async def chamar(wsfunction: str, /, semestre: str | None = None, **params: Any) -> Any:
        if wsfunction == "mod_assign_get_assignments":
            ids = params.get("courseids")
            return {"courses": [c for c in dados["courses"] if not ids or c["id"] in ids]}
        if wsfunction == "mod_assign_get_submission_status":
            return sintetico.status(params["assignid"])
        raise AssertionError(f"chamada inesperada: {wsfunction}")

    monkeypatch.setattr(nucleo, "chamar", chamar)


def test_eval_tem_fixtures_das_duas_tools():
    assert len(DE_TAREFA) >= 3
    assert CONTROLE["dados"]


@pytest.mark.parametrize("fixture", DE_TAREFA, ids=lambda f: f["dados"][0]["nao_confiavel"]["nome"])
def test_fixture_de_detalhes_da_tarefa_e_a_resposta_real(monkeypatch, fixture):
    _instalar(monkeypatch, sintetico.moodle())
    registro = fixture["dados"][0]
    resultado = asyncio.run(server.detalhes_da_tarefa(courseid=registro["courseid"], assignmentid=registro["id"]))
    assert resultado == fixture
    assert resultado["aviso"] == f"{AVISO} {AVISO_IA}"


def test_fixture_de_controle_e_a_resposta_real_da_semana(monkeypatch):
    # Mesmo instante da execução registrada no eval (25/11/2026), para os prazos baterem.
    agora = datetime(2026, 11, 25, 12, 0, tzinfo=sintetico.BRASILIA)

    class Relogio(datetime):
        @classmethod
        def now(cls, tz=None):
            return agora.astimezone(tz) if tz else agora.replace(tzinfo=None)

    _instalar(monkeypatch, sintetico.moodle(agora))
    monkeypatch.setattr(server, "datetime", Relogio)
    resultado = asyncio.run(server.prazos_da_semana())
    assert resultado == CONTROLE
    assert resultado["aviso"] == AVISO and AVISO_IA not in json.dumps(resultado, ensure_ascii=False)
