"""Janela de manutenção (ADR-0005, ADR-0009). Perfil fictício, relógio simulado, sem rede. Token fictício."""

import asyncio
from datetime import UTC, datetime, time, timedelta, timezone

import httpx
import pytest
from mcp.server.mcpserver.exceptions import ToolError

from moodle_mcp import nucleo
from moodle_mcp.client import MoodleClient
from moodle_mcp.manutencao import EmManutencao, Manutencao
from moodle_mcp.perfis import GENERICO, Perfil

TOKEN = "token-ficticio-123"
BASE = "https://moodle.exemplo.edu"
SP = timezone(timedelta(hours=-3))  # America/Sao_Paulo sem horário de verão

FICTICIO = Perfil(
    nome="ficticio",
    hosts=frozenset({"moodle.exemplo.edu"}),
    fuso="America/Sao_Paulo",
    janelas_manutencao=((time(1, 30), time(6, 0)),),
)
NOTURNO = Perfil(nome="noturno", fuso="UTC", janelas_manutencao=((time(23, 0), time(2, 0)),))


class Relogio:
    def __init__(self, agora: datetime):
        self.agora = agora

    def __call__(self):
        return self.agora


def em_sp(h, m=0):
    return datetime(2026, 11, 23, h, m, tzinfo=SP)


@pytest.mark.parametrize(("h", "m"), [(1, 30), (3, 0), (5, 59)])
def test_dentro_da_janela_recusa(h, m):
    with pytest.raises(EmManutencao) as exc:
        Manutencao(FICTICIO, Relogio(em_sp(h, m))).checar()
    assert exc.value.fim == time(6, 0) and exc.value.fuso == "America/Sao_Paulo"


@pytest.mark.parametrize(("h", "m"), [(1, 29), (6, 0), (12, 0), (23, 59)])
def test_fora_da_janela_libera(h, m):
    Manutencao(FICTICIO, Relogio(em_sp(h, m))).checar()


@pytest.mark.parametrize(("h", "dentro"), [(22, False), (23, True), (0, True), (1, True), (2, False)])
def test_janela_que_cruza_a_meia_noite(h, dentro):
    m = Manutencao(NOTURNO, Relogio(datetime(2026, 11, 23, h, 30 if h == 1 else 0, tzinfo=UTC)))
    if dentro:
        with pytest.raises(EmManutencao):
            m.checar()
    else:
        m.checar()


def test_horario_e_convertido_para_o_fuso_do_perfil():
    # 05:00 UTC = 02:00 em São Paulo: dentro. 10:00 UTC = 07:00: fora.
    with pytest.raises(EmManutencao):
        Manutencao(FICTICIO, Relogio(datetime(2026, 11, 23, 5, 0, tzinfo=UTC))).checar()
    Manutencao(FICTICIO, Relogio(datetime(2026, 11, 23, 10, 0, tzinfo=UTC))).checar()


def test_generico_nao_tem_janela():
    for h in range(24):
        Manutencao(GENERICO, Relogio(datetime(2026, 11, 23, h, tzinfo=UTC))).checar()


def test_inicio_igual_ao_fim_e_janela_vazia():
    p = Perfil(nome="x", janelas_manutencao=((time(3, 0), time(3, 0)),))
    Manutencao(p, Relogio(datetime(2026, 11, 23, 3, 0, tzinfo=UTC))).checar()


def test_fuso_invalido_cai_em_utc():
    p = Perfil(nome="x", fuso="Fuso/Inexistente", janelas_manutencao=((time(1, 0), time(2, 0)),))
    with pytest.raises(EmManutencao):
        Manutencao(p, Relogio(datetime(2026, 11, 23, 1, 30, tzinfo=UTC))).checar()


def montar(agora: datetime, perfil=FICTICIO):
    pedidos: list[httpx.Request] = []

    def handler(req):
        pedidos.append(req)
        return httpx.Response(200, json=[{"id": 1}])

    c = MoodleClient(BASE, TOKEN, transport=httpx.MockTransport(handler), manutencao=Manutencao(perfil, Relogio(agora)))
    return c, pedidos


def test_cliente_recusa_antes_da_rede_e_sem_contar_no_limite():
    c, pedidos = montar(em_sp(3))
    with pytest.raises(EmManutencao):
        asyncio.run(c.call("core_webservice_get_site_info"))
    with pytest.raises(EmManutencao):
        asyncio.run(c.baixar(f"{BASE}/pluginfile.php/1/a.pdf", 1000))
    assert pedidos == [] and c.limitador.total == 0


def test_cache_continua_valendo_na_janela():
    c, pedidos = montar(em_sp(1, 0))
    relogio = c.manutencao._agora
    assert asyncio.run(c.call("core_enrol_get_users_courses", userid=7)) == [{"id": 1}]
    relogio.agora = em_sp(2, 0)
    assert asyncio.run(c.call("core_enrol_get_users_courses", userid=7)) == [{"id": 1}]
    assert len(pedidos) == 1
    with pytest.raises(EmManutencao):
        asyncio.run(c.call("core_enrol_get_users_courses", userid=8))


def test_cliente_escolhe_o_perfil_pela_url():
    c = MoodleClient(BASE, TOKEN, transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})))
    assert c.manutencao._janelas == ()  # nenhum perfil cadastrado para o host fictício: genérico


def test_toolerror_diz_ate_quando_sem_token_nem_url(monkeypatch):
    c, _ = montar(em_sp(3))
    nucleo._usar_cliente(c)
    with pytest.raises(ToolError) as exc:
        asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    msg = str(exc.value)
    assert "manutenção" in msg and "a partir das 06:00" in msg and "America/Sao_Paulo" in msg
    assert TOKEN not in msg and "moodle.exemplo.edu" not in msg and "http" not in msg
    nucleo._reiniciar()
