"""As fixtures do eval `evals/aviso-de-ia.md` são o que o servidor de fato devolve.

O eval mede se o agente respeita o aviso de IA (história #5). Se o texto do aviso ou o formato
de `detalhes_da_tarefa` mudar, este teste falha e as fixtures precisam ser atualizadas, para o
eval não medir o agente contra uma resposta que o servidor não produz mais.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Any

import pytest

from moodle_mcp import nucleo, server
from moodle_mcp.nao_confiavel import AVISO, AVISO_IA

EVAL = Path(__file__).resolve().parent.parent / "evals" / "aviso-de-ia.md"


def _fixtures() -> list[dict[str, Any]]:
    return [json.loads(bloco) for bloco in re.findall(r"```json\n(.*?)\n```", EVAL.read_text(encoding="utf-8"), re.DOTALL)]


def _de_tarefa(fixture: dict[str, Any]) -> bool:
    return "courseid" in fixture["dados"][0]


def test_eval_tem_fixtures_das_duas_tools():
    fixtures = _fixtures()
    assert sum(_de_tarefa(f) for f in fixtures) >= 2
    assert any(f.get("modo") == "semana" for f in fixtures)


@pytest.mark.parametrize("fixture", [f for f in _fixtures() if _de_tarefa(f)], ids=lambda f: f["dados"][0]["nao_confiavel"]["nome"])
def test_fixture_de_detalhes_da_tarefa_e_a_resposta_real(monkeypatch, fixture):
    registro = fixture["dados"][0]
    textos = registro["nao_confiavel"]
    moodle = {
        "courses": [
            {
                "id": registro["courseid"],
                "assignments": [
                    {
                        "id": registro["id"],
                        "course": registro["courseid"],
                        "name": textos["nome"],
                        "intro": f"<p>{textos['enunciado']}</p>",
                        "duedate": registro["duedate"],
                        "cutoffdate": registro["cutoffdate"],
                        "configs": [
                            {"plugin": "file", "subtype": "assignsubmission", "name": "filetypeslist", "value": textos["tipos_arquivo_aceitos"]}
                        ],
                        "introattachments": [{"filename": textos["anexos"], "fileurl": "https://moodle.exemplo.edu/f"}],
                    }
                ],
            }
        ]
    }

    async def chamar(wsfunction: str, **params: Any) -> Any:
        assert wsfunction == "mod_assign_get_assignments"
        return moodle

    monkeypatch.setattr(nucleo, "chamar", chamar)
    resultado = asyncio.run(server.detalhes_da_tarefa(courseid=registro["courseid"], assignmentid=registro["id"]))

    assert resultado == fixture
    assert resultado["aviso"] == f"{AVISO} {AVISO_IA}"


def test_controle_nao_avaliativo_usa_so_o_aviso_comum():
    controle = next(f for f in _fixtures() if f.get("modo") == "semana")
    assert controle["aviso"] == AVISO
    assert AVISO_IA not in json.dumps(controle, ensure_ascii=False)
