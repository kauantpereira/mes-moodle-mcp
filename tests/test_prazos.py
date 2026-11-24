"""Tool de prazos: respostas simuladas e chamadas de Web Service interceptadas."""

import asyncio
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from moodle_mcp import server

AGORA = 1_800_000_000


class RelogioFixo(datetime):
    @classmethod
    def now(cls, tz=None):
        instante = datetime.fromtimestamp(AGORA, UTC)
        return instante if tz else instante.replace(tzinfo=None)


@pytest.fixture(autouse=True)
def relogio(monkeypatch):
    monkeypatch.setattr(server, "datetime", RelogioFixo)


def executar(coro):
    return asyncio.run(coro)


def dados(*atividades):
    return {"courses": [{"id": 1, "fullname": "Disciplina <script>ruim</script>", "assignments": list(atividades)}]}


def atividade(id_, nome, prazo, **extra):
    return {"id": id_, "name": nome, "duedate": prazo, **extra}


def envio(estado, **extra):
    return {"lastattempt": {"submission": {"status": estado, "timemodified": AGORA + 60, **extra}}}


def instalar(monkeypatch, assignments, statuses=None):
    chamadas = []
    statuses = statuses or {}

    async def chamar(funcao, **params):
        chamadas.append((funcao, params))
        if funcao == "mod_assign_get_assignments":
            return assignments
        if params["assignid"] in statuses:
            resultado = statuses[params["assignid"]]
            if isinstance(resultado, Exception):
                raise resultado
            return resultado
        return {"lastattempt": {"submission": {"status": "new"}}}

    monkeypatch.setattr(server.nucleo, "chamar", chamar)
    return chamadas


def test_listagem_omite_enviada_e_mantem_rascunho_e_sem_submissao(monkeypatch):
    chamadas = instalar(
        monkeypatch,
        dados(atividade(1, "Enviada", AGORA + 100), atividade(2, "Rascunho", AGORA + 200), atividade(3, "Nova", AGORA + 300)),
        {1: envio("submitted"), 2: envio("draft"), 3: {"lastattempt": {"submission": {"status": "new"}}}},
    )
    resultado = executar(server.prazos_da_semana(fuso_horario="America/Sao_Paulo"))
    assert [x["nao_confiavel"]["atividade"] for x in resultado["dados"]] == ["Rascunho", "Nova"]
    assert [x["status_envio"] for x in resultado["dados"]] == ["rascunho", "sem_submissao"]
    assert resultado["dados"][0]["prazo"].endswith("-03:00")
    assert resultado["dados"][0]["timemodified"]
    assert [c for c in chamadas if c[0] == "mod_assign_get_submission_status"] == [
        ("mod_assign_get_submission_status", {"assignid": 1}),
        ("mod_assign_get_submission_status", {"assignid": 2}),
        ("mod_assign_get_submission_status", {"assignid": 3}),
    ]
    assert all("userid" not in params for _, params in chamadas)
    assert resultado["aviso_prazos"].find("PDFs") >= 0
    assert "ruim" not in str(resultado)


def test_nosubmissions_mantem_prazo_sem_chamar_status(monkeypatch):
    chamadas = instalar(monkeypatch, dados(atividade(1, "Prova presencial", AGORA + 100, nosubmissions=1)))
    resultado = executar(server.prazos_da_semana())
    assert resultado["dados"][0]["status_envio"] == "sem_entrega_pelo_moodle"
    assert resultado["dados"][0]["entrega_pelo_moodle"] is False
    assert resultado["dados"][0]["prazo"] == datetime.fromtimestamp(AGORA + 100, UTC).astimezone(ZoneInfo("America/Sao_Paulo")).isoformat(timespec="minutes")
    assert not any(nome == "mod_assign_get_submission_status" for nome, _ in chamadas)


def test_ignora_sem_prazo_inclui_limites_ordena_e_aplica_extensao(monkeypatch):
    inicio, fim = AGORA, AGORA + 7 * 86400
    chamadas = instalar(
        monkeypatch,
        dados(
            atividade(1, "Sem prazo", 0),
            atividade(2, "Fim", fim),
            atividade(3, "Início", inicio),
            atividade(4, "Prorrogada", AGORA - 100),
            atividade(5, "Tardia", fim + 1),
        ),
        {
            2: {"lastattempt": {"submission": {"status": "new"}}},
            3: {"lastattempt": {"submission": {"status": "new"}}},
            4: {"lastattempt": {"extensionduedate": AGORA + 500, "submission": {"status": "draft"}}},
        },
    )
    resultado = executar(server.prazos_da_semana(limite=12))
    assert [i["nao_confiavel"]["atividade"] for i in resultado["dados"]] == ["Início", "Prorrogada", "Fim"]
    assert [i["status_envio"] for i in resultado["dados"]] == ["sem_submissao", "rascunho", "sem_submissao"]
    ids = [params["assignid"] for nome, params in chamadas if nome == "mod_assign_get_submission_status"]
    assert ids == [4, 3, 2]


def test_falha_status_marca_nao_verificado_e_resposta_vazia(monkeypatch):
    erro = ToolError("indisponível")
    instalar(monkeypatch, dados(atividade(1, "Falha", AGORA + 100)), {1: erro})
    resultado = executar(server.prazos_da_semana())
    assert resultado["dados"][0]["status_envio"] == "nao_verificado"

    instalar(monkeypatch, dados(atividade(1, "Passou", AGORA - 20 * 86400)))
    vazia = executar(server.prazos_da_semana())
    assert vazia["dados"] == []


@pytest.mark.parametrize(
    ("status", "esperado"),
    [
        ({}, "nao_verificado"),
        ({"lastattempt": {}}, "sem_submissao"),
        ({"lastattempt": {"submission": {}}}, "nao_verificado"),
        ({"lastattempt": {"submission": {"status": "new"}}}, "sem_submissao"),
        ({"lastattempt": {"submission": {"status": "draft"}}}, "rascunho"),
        ({"lastattempt": {"submission": {"status": "submitted"}}}, "enviada"),
        ({"lastattempt": {"submission": {"status": "reopened"}}}, "reaberta"),
        ({"lastattempt": {"teamsubmission": {"status": "submitted"}}}, "enviada"),
        ({"lastattempt": {"submission": {"status": "unexpected"}}}, "nao_verificado"),
    ],
)
def test_resposta_de_status_incompleta_ou_desconhecida_nao_afirma_submissao(monkeypatch, status, esperado):
    instalar(monkeypatch, dados(atividade(1, "Tarefa", AGORA + 100)), {1: status})
    resultado = executar(server.prazos_da_semana())
    if esperado == "enviada":
        assert resultado["dados"] == []
        return
    assert len(resultado["dados"]) == 1
    assert resultado["dados"][0]["status_envio"] == esperado


def test_limite_de_itens_e_texto(monkeypatch):
    atividades = [atividade(i, "T" * 300 + str(i), AGORA + i) for i in range(1, 15)]
    instalar(monkeypatch, dados(*atividades))
    resultado = executar(server.prazos_da_semana(limite=99))
    assert len(resultado["dados"]) == 8
    assert len(resultado["dados"][0]["nao_confiavel"]["atividade"]) <= 121
    assert len(str(resultado)) < 8000
    assert resultado["limite"] == 8


def test_fuso_padrao_preserva_data_hora_e_offset_sem_parametro(monkeypatch):
    prazo = int(datetime(2026, 11, 25, 23, 59, tzinfo=ZoneInfo("America/Sao_Paulo")).timestamp())
    instalar(monkeypatch, dados(atividade(1, "Entrega", prazo)))
    resultado = executar(server.prazos_da_semana(nome_tarefa="Entrega"))
    assert resultado["dados"][0]["prazo"] == "2026-11-25T23:59-03:00"


def test_padrao_do_fuso_no_esquema_mcp_corresponde_ao_padrao_da_execucao():
    ferramentas = executar(server.mcp.list_tools())
    schema = next(f.input_schema for f in ferramentas if f.name == "prazos_da_semana")
    assert schema["properties"]["fuso_horario"]["default"] == "America/Sao_Paulo"
    assert schema["properties"]["limite"]["default"] == 8


def test_fuso_explicito_sobrescreve_padrao(monkeypatch):
    prazo = int(datetime(2026, 11, 25, 23, 59, tzinfo=ZoneInfo("America/Sao_Paulo")).timestamp())
    instalar(monkeypatch, dados(atividade(1, "Entrega", prazo)))
    resultado = executar(server.prazos_da_semana(nome_tarefa="Entrega", fuso_horario="UTC"))
    assert resultado["dados"][0]["prazo"] == "2026-11-26T02:59+00:00"


def test_consulta_especifica_usa_prazo_prorrogado_sem_alterar_dados(monkeypatch):
    prazo_base = AGORA + 100
    prazo_extensao = AGORA + 500
    assignments = dados(atividade(1, "Prorrogada", prazo_base))
    instalar(monkeypatch, assignments, {1: {"lastattempt": {
        "extensionduedate": prazo_extensao,
        "submission": {"status": "draft"},
    }}})
    resultado = executar(server.prazos_da_semana(nome_tarefa="Prorrogada"))
    assert resultado["dados"][0]["prazo"] == datetime.fromtimestamp(prazo_extensao, UTC).astimezone(ZoneInfo("America/Sao_Paulo")).isoformat(timespec="minutes")
    assert assignments["courses"][0]["assignments"][0]["duedate"] == prazo_base


def test_limita_chamadas_de_status_e_marca_restantes_nao_verificadas(monkeypatch):
    atividades = [atividade(i, f"Tarefa {i}", AGORA + i) for i in range(1, 17)]
    statuses = {i: envio("submitted") for i in range(1, 9)}
    chamadas = instalar(monkeypatch, dados(*atividades), statuses)
    resultado = executar(server.prazos_da_semana())
    verificacoes = [c for c in chamadas if c[0] == "mod_assign_get_submission_status"]
    assert len(verificacoes) == 15
    assert len(resultado["dados"]) == 8
    assert [t["status_envio"] for t in resultado["dados"]] == ["sem_submissao"] * 7 + ["nao_verificado"]


def test_consulta_especifica_enviada_fora_da_janela_com_multiplos_arquivos(monkeypatch):
    status = {
        "lastattempt": {
            "submission": {"status": "submitted", "timemodified": AGORA - 20 * 86400, "userid": 999},
            "plugins": [
                {"editorfields": {"text": "conteúdo privado"}, "fileareas": [{"files": [{"filename": "um.pdf"}, {"filename": "dois.zip"}]}]},
                {"fileareas": [{"files": [{"filename": "tres.txt"}]}]},
            ],
        }
    }
    chamadas = instalar(monkeypatch, dados(atividade(5, "Trabalho antigo", AGORA - 20 * 86400)), {5: status})
    resultado = executar(server.prazos_da_semana(nome_tarefa="trabalho antigo"))
    tarefa = resultado["dados"][0]
    assert tarefa["status_envio"] == "enviada"
    assert tarefa["timemodified"]
    assert tarefa["significado_horario"] == "última modificação registrada pelo Moodle"
    assert [a["nao_confiavel"]["arquivo"] for a in tarefa["arquivos"]] == ["um.pdf", "dois.zip", "tres.txt"]
    assert "conteúdo privado" not in str(resultado) and "userid" not in str(resultado)
    assert chamadas[-1] == ("mod_assign_get_submission_status", {"assignid": 5})


def test_consulta_especifica_duplicada_desambigua_sem_status(monkeypatch):
    chamadas = instalar(monkeypatch, {"courses": [
        {"fullname": "A", "assignments": [atividade(1, "EP 2", AGORA - 50 * 86400)]},
        {"fullname": "B", "assignments": [atividade(2, "EP 2", AGORA + 1)]},
    ]})
    resultado = executar(server.prazos_da_semana(nome_tarefa="ep 2"))
    assert resultado["modo"] == "desambiguar"
    assert len(resultado["dados"]) == 2
    assert not any(nome == "mod_assign_get_submission_status" for nome, _ in chamadas)


def test_sem_arquivos_grupo_e_status_desconhecido(monkeypatch):
    status = {"lastattempt": {"teamsubmission": {"status": "submitted", "timemodified": AGORA}, "submission": {"status": "draft"},
                              "plugins": [{"fileareas": [{"files": []}]}], "submissiongroup": 23,
                              "submissiongroupmemberswhoneedtosubmit": [9, 10]}}
    instalar(monkeypatch, dados(atividade(8, "Grupo", AGORA + 50)), {8: status})
    resultado = executar(server.prazos_da_semana(nome_tarefa="Grupo"))
    tarefa = resultado["dados"][0]
    assert tarefa["status_envio"] == "enviada"
    assert tarefa["arquivos"] == []
    assert "23" not in str(resultado) and "9" not in str(resultado) and "10" not in str(resultado)


def test_consulta_especifica_sem_submissao_e_fuso_invalido(monkeypatch):
    instalar(monkeypatch, dados(atividade(1, "Novo", None)), {1: {"lastattempt": {"submission": {"status": "new"}}}})
    resultado = executar(server.prazos_da_semana(nome_tarefa="Novo"))
    assert resultado["dados"][0]["status_envio"] == "sem_submissao"
    with pytest.raises(ToolError, match="Fuso horário inválido"):
        executar(server.prazos_da_semana(fuso_horario="Planeta/Errado"))
