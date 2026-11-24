"""Moodle por semestre (ADR-0017): URL padrão vinda do perfil, parâmetro `semestre` e `usar_semestre`.

Perfil fictício em `moodle.exemplo.edu`; token fictício; nada sai para a rede.
"""

import asyncio
import json
import re
from pathlib import Path

import httpx
import pytest
from mcp.server.mcpserver.exceptions import ToolError

from moodle_mcp import chaveiro, cli, nucleo, perfis
from moodle_mcp.perfis import GENERICO, Perfil
from moodle_mcp.server import mcp

BASE = "https://moodle.exemplo.edu"
TOKEN = "token-ficticio-123"
RAIZ = Path(__file__).resolve().parents[1]


def url_ficticia(semestre: str | None) -> str:
    codigo = {None: "20262", "atual": "20262", "anterior": "20261"}.get(semestre, (semestre or "").replace(".", ""))
    if not re.fullmatch(r"\d{4}[12]", codigo):
        raise ValueError("use o formato AAAA.S, ex.: 2026.1")
    return f"{BASE}/{codigo}/"


FICTICIO = Perfil(nome="ficticio", hosts=frozenset({"moodle.exemplo.edu"}), url_do_semestre=url_ficticia)


@pytest.fixture(autouse=True)
def limpar(monkeypatch):
    monkeypatch.delenv("MOODLE_URL", raising=False)
    monkeypatch.delenv("MOODLE_TOKEN", raising=False)
    monkeypatch.setattr(perfis, "PERFIS", (FICTICIO,))
    nucleo._reiniciar()
    yield
    nucleo._reiniciar()


@pytest.fixture
def moodle(monkeypatch):
    """Moodle simulado: registra (URL, token) de cada chamada."""
    vistos: list[tuple[str, str]] = []

    def handler(req):
        token = dict(httpx.QueryParams(req.content.decode()))["wstoken"]
        vistos.append((str(req.url).split("/webservice")[0], token))
        return httpx.Response(200, json={"userid": 7, "siteurl": str(req.url).split("/webservice")[0]})

    monkeypatch.setattr(nucleo, "_transporte", httpx.MockTransport(handler))
    return vistos


# ---------- de onde vem a URL ----------


def test_sem_url_usa_o_semestre_atual_do_perfil_padrao():
    assert nucleo.url_do_moodle() == f"{BASE}/20262"


def test_sem_url_e_sem_perfil_padrao_pede_o_endereco(monkeypatch):
    monkeypatch.setattr(perfis, "PERFIS", ())
    with pytest.raises(ToolError, match="MOODLE_URL"):
        nucleo.url_do_moodle()


def test_moodle_url_tem_prioridade_sobre_o_perfil(monkeypatch):
    monkeypatch.setenv("MOODLE_URL", BASE + "/20252/")
    assert nucleo.url_do_moodle() == f"{BASE}/20252"


def test_semestre_com_moodle_url_usa_o_perfil_do_host(monkeypatch):
    monkeypatch.setenv("MOODLE_URL", BASE + "/20252")
    assert nucleo.url_do_moodle("2026.1") == f"{BASE}/20261"


def test_semestre_em_moodle_sem_semestres(monkeypatch):
    monkeypatch.setattr(perfis, "PERFIS", ())
    monkeypatch.setenv("MOODLE_URL", "https://outro.exemplo.edu")
    with pytest.raises(ToolError, match="não separa as disciplinas por semestre"):
        nucleo.url_do_moodle("2026.1")


def test_semestre_invalido_explica_o_formato():
    with pytest.raises(ToolError, match="Semestre inválido: use o formato"):
        nucleo.url_do_moodle("primeiro")


@pytest.mark.parametrize(
    ("candidatos", "esperado"),
    [((), None), ((GENERICO,), None), ((FICTICIO,), FICTICIO), ((FICTICIO, Perfil(nome="b", url_do_semestre=url_ficticia)), None)],
)
def test_perfil_padrao_so_quando_ha_um(candidatos, esperado):
    assert perfis.padrao(candidatos) is esperado


# ---------- um cliente e um token por semestre ----------


def test_parametro_semestre_vale_so_para_a_chamada(moodle):
    chaveiro.salvar(f"{BASE}/20262", "token-atual-111")
    chaveiro.salvar(f"{BASE}/20261", "token-anterior-222")

    async def consultas():
        await nucleo.chamar("core_webservice_get_site_info")
        await nucleo.chamar("core_webservice_get_site_info", semestre="2026.1")
        await nucleo.chamar("core_webservice_get_site_info")

    asyncio.run(consultas())
    assert moodle == [
        (f"{BASE}/20262", "token-atual-111"),
        (f"{BASE}/20261", "token-anterior-222"),
        (f"{BASE}/20262", "token-atual-111"),
    ]


def test_semestres_somam_no_mesmo_limite(moodle):
    chaveiro.salvar(f"{BASE}/20262", TOKEN)
    chaveiro.salvar(f"{BASE}/20261", TOKEN)
    assert nucleo.cliente().limitador is nucleo.cliente("2026.1").limitador


def test_semestre_sem_token_faz_o_login_daquele_moodle(monkeypatch, moodle):
    chaveiro.salvar(f"{BASE}/20262", TOKEN)
    logins: list[str] = []

    async def entrar(base_url, interacao):
        logins.append(base_url)
        return "token-novo-333"

    monkeypatch.setattr(perfis, "PERFIS", (Perfil(nome="f", hosts=FICTICIO.hosts, url_do_semestre=url_ficticia, login=entrar),))
    asyncio.run(nucleo.chamar("core_webservice_get_site_info", semestre="anterior"))
    assert logins == [f"{BASE}/20261"]
    assert chaveiro.ler(f"{BASE}/20261") == "token-novo-333"
    assert chaveiro.ler(f"{BASE}/20262") == TOKEN  # o do semestre atual continua lá


def test_usar_semestre_vale_para_as_proximas_tools(moodle):
    chaveiro.salvar(f"{BASE}/20261", TOKEN)
    assert nucleo.usar_semestre("2026.1") == f"{BASE}/20261"
    asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    assert moodle == [(f"{BASE}/20261", TOKEN)]
    assert nucleo.usar_semestre("atual") == f"{BASE}/20262"


def test_usar_semestre_invalido_mantem_o_anterior():
    nucleo.usar_semestre("2026.1")
    with pytest.raises(ToolError):
        nucleo.usar_semestre("primeiro")
    assert nucleo.url_do_moodle() == f"{BASE}/20261"


# ---------- tools, CLI e manifesto ----------


def test_tools_aceitam_semestre():
    tools = {t.name: t for t in asyncio.run(mcp.list_tools())}
    assert "semestre" in tools["quem_sou_eu"].input_schema["properties"]
    assert tools["usar_semestre"].input_schema["required"] == ["semestre"]
    assert tools["usar_semestre"].annotations.read_only_hint


def test_tool_usar_semestre_mostra_o_moodle_escolhido():
    resultado = asyncio.run(mcp.call_tool("usar_semestre", {"semestre": "anterior"}))
    assert json.loads(resultado[0].text if isinstance(resultado, list) else resultado.content[0].text) == {
        "moodle": "moodle.exemplo.edu/20261"
    }


def test_cli_sair_do_semestre(chaveiro_falso, capsys):
    chaveiro.salvar(f"{BASE}/20261", TOKEN)
    chaveiro.salvar(f"{BASE}/20262", TOKEN)
    assert cli.main(["sair", "--semestre", "2026.1"]) == 0
    assert chaveiro_falso.dados == {("moodle-mcp", f"{BASE}/20262"): TOKEN}


def test_servidor_do_plugin_nao_depende_de_user_config():
    """O Claude Desktop descarta servidores cuja config cita `${user_config...}` (ADR-0017)."""
    assert "user_config" not in (RAIZ / ".mcp.json").read_text()
    assert "moodle_url" not in json.loads((RAIZ / ".claude-plugin" / "plugin.json").read_text()).get("userConfig", {})
