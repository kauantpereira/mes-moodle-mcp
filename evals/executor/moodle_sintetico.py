"""Servidor MCP real com um Moodle sintético, para executar evals sem acessar um Moodle de verdade.

Roda o mesmo `moodle_mcp.server` que vai para o aluno (mesmas tools, descrições e instruções),
trocando só `nucleo.chamar` por respostas sintéticas da API do Moodle. O login fica bloqueado: nenhuma
tool abre navegador nem lê o chaveiro. Cada chamada à API sintética é registrada, uma por linha, no
arquivo indicado em `MOODLE_EVAL_LOG`, para a folha de medição contar as chamadas ao Moodle.

Uso (o executor da eval faz isto): `uv run python evals/executor/moodle_sintetico.py`
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

EVAL = Path(__file__).resolve().parent.parent / "aviso-de-ia.md"
BRASILIA = timezone(timedelta(hours=-3))

DISCIPLINAS = {7: "Disciplina Aurora", 9: "Disciplina Brisa", 11: "Disciplina Cobalto"}
# Tarefa que só aparece na lista da semana (caso A6): rascunho, prazo daqui a alguns dias.
QUESTIONARIO = {"id": 64, "course": 9, "name": "Questionário 5", "intro": "", "configs": [], "introattachments": []}
RASCUNHOS = {64}
USERID = 1001


def fixtures() -> list[dict[str, Any]]:
    """Blocos JSON do eval, na ordem em que aparecem."""
    return [json.loads(b) for b in re.findall(r"```json\n(.*?)\n```", EVAL.read_text(encoding="utf-8"), re.DOTALL)]


def de_tarefa(fixture: dict[str, Any]) -> bool:
    """Fixture de `detalhes_da_tarefa` (as de `prazos_da_semana` não têm `nome`)."""
    return "nome" in fixture["dados"][0].get("nao_confiavel", {})


def tarefa_bruta(fixture: dict[str, Any]) -> dict[str, Any]:
    """A tarefa como `mod_assign_get_assignments` a devolveria, para gerar exatamente a fixture."""
    registro = fixture["dados"][0]
    textos = registro["nao_confiavel"]
    return {
        "id": registro["id"],
        "course": registro["courseid"],
        "name": textos["nome"],
        "intro": f"<p>{textos['enunciado']}</p>",
        "duedate": registro["duedate"],
        "cutoffdate": registro["cutoffdate"],
        "configs": [
            {"plugin": "file", "subtype": "assignsubmission", "name": "filetypeslist", "value": textos["tipos_arquivo_aceitos"]}
        ],
        "introattachments": [{"filename": textos["anexos"], "fileurl": "https://moodle.exemplo.invalid/f"}],
    }


def moodle(agora: datetime | None = None) -> dict[str, Any]:
    """Resposta sintética de `mod_assign_get_assignments` com as tarefas de todas as fixtures."""
    agora = agora or datetime.now(BRASILIA)
    tarefas = [tarefa_bruta(f) for f in fixtures() if de_tarefa(f)]
    prazo_questionario = (agora + timedelta(days=5)).replace(hour=18, minute=0, second=0, microsecond=0)
    tarefas.append({**QUESTIONARIO, "duedate": int(prazo_questionario.timestamp()), "cutoffdate": 0})
    cursos = []
    for courseid, nome in DISCIPLINAS.items():
        cursos.append({"id": courseid, "fullname": nome, "assignments": [t for t in tarefas if t["course"] == courseid]})
    return {"courses": cursos}


def status(assignid: int) -> dict[str, Any]:
    estado = "draft" if assignid in RASCUNHOS else "new"
    return {"lastattempt": {"submission": {"status": estado, "plugins": []}}}


def main() -> None:
    os.environ.setdefault("MOODLE_URL", "https://moodle.exemplo.invalid")
    from mcp.server.mcpserver.exceptions import ToolError

    from moodle_mcp import nucleo, server

    registro = Path(os.environ["MOODLE_EVAL_LOG"]) if os.environ.get("MOODLE_EVAL_LOG") else None
    dados = moodle()

    async def chamar(wsfunction: str, /, semestre: str | None = None, **params: Any) -> Any:
        if registro:
            with registro.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"funcao": wsfunction, "params": params}, ensure_ascii=False) + "\n")
        if wsfunction == "mod_assign_get_assignments":
            ids = params.get("courseids")
            return {"courses": [c for c in dados["courses"] if not ids or c["id"] in ids]}
        if wsfunction == "mod_assign_get_submission_status":
            return status(params["assignid"])
        if wsfunction == "core_enrol_get_users_courses":
            return [{"id": c["id"], "fullname": c["fullname"]} for c in dados["courses"]]
        # Sem avisos, materiais ou novidades: as tools respondem "nada novo", sem erro.
        if wsfunction == "core_course_get_updates_since":
            return {"instances": [], "warnings": []}
        if wsfunction == "core_course_get_contents":
            return []
        if wsfunction == "mod_forum_get_forums_by_courses":
            return []
        if wsfunction == "core_webservice_get_site_info":
            return {"sitename": "Moodle sintético", "fullname": "Aluno Sintético", "release": "4.5"}
        raise ToolError(f"Função {wsfunction} não disponível no Moodle sintético da eval.")

    async def sem_login(*_: Any, **__: Any) -> Any:
        raise ToolError("Login desativado no Moodle sintético da eval.")

    async def userid(_semestre: str | None = None) -> int:
        return USERID

    nucleo.chamar = chamar
    server._userid_do_aluno = userid
    nucleo.cliente_com_login = sem_login
    nucleo.entrar = sem_login
    server.mcp.run()


if __name__ == "__main__":
    main()
