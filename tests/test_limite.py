"""Contador e limite de chamadas (ADR-0005). Relógio simulado, sem rede. Token fictício."""

import asyncio

import httpx
import pytest
from mcp.server.mcpserver.exceptions import ToolError

from moodle_mcp import nucleo
from moodle_mcp.client import MoodleClient
from moodle_mcp.limite import JANELAS_PADRAO, LimiteAtingido, Limitador

TOKEN = "token-ficticio-123"
BASE = "https://moodle.exemplo.edu"


class Relogio:
    def __init__(self):
        self.agora = 1000.0

    def __call__(self):
        return self.agora


def test_conta_ate_o_limite_e_recusa_a_seguinte():
    r = Relogio()
    lim = Limitador(((3, 60),), relogio=r)
    for _ in range(3):
        lim.registrar()
    with pytest.raises(LimiteAtingido) as exc:
        lim.registrar()
    assert exc.value.maximo == 3 and exc.value.janela_s == 60 and exc.value.espera_s == 60
    assert lim.uso() == {"ultimos_60s": 3, "total": 3}


def test_libera_quando_a_mais_antiga_sai_da_janela():
    r = Relogio()
    lim = Limitador(((2, 60),), relogio=r)
    lim.registrar()
    r.agora += 40
    lim.registrar()
    with pytest.raises(LimiteAtingido) as exc:
        lim.registrar()
    assert exc.value.espera_s == 20
    r.agora += 20
    lim.registrar()
    assert lim.total == 3


def test_janela_longa_tambem_limita():
    r = Relogio()
    lim = Limitador(((5, 60), (8, 3600)), relogio=r)
    for _ in range(8):
        lim.registrar()
        r.agora += 61
    with pytest.raises(LimiteAtingido) as exc:
        lim.registrar()
    assert exc.value.janela_s == 3600
    assert exc.value.espera_s == 3600 - 8 * 61


def test_padrao_e_janelas_invalidas():
    assert JANELAS_PADRAO == ((60, 60), (600, 3600))
    with pytest.raises(ValueError):
        Limitador(())
    with pytest.raises(ValueError):
        Limitador(((0, 60),))


def cliente_limitado(maximo):
    pedidos = []

    def handler(req):
        pedidos.append(req)
        return httpx.Response(200, json={"ok": True}) if "server.php" in str(req.url) else httpx.Response(200, content=b"x")

    lim = Limitador(((maximo, 60),), relogio=Relogio())
    return MoodleClient(BASE, TOKEN, transport=httpx.MockTransport(handler), limitador=lim), pedidos


def test_cliente_recusa_antes_da_rede():
    c, pedidos = cliente_limitado(2)
    asyncio.run(c.call("core_webservice_get_site_info"))
    asyncio.run(c.baixar(f"{BASE}/webservice/pluginfile.php/1/a.pdf", 10))
    with pytest.raises(LimiteAtingido):
        asyncio.run(c.call("core_webservice_get_site_info"))
    assert len(pedidos) == 2


def test_funcao_bloqueada_nao_gasta_cota():
    c, _ = cliente_limitado(1)
    with pytest.raises(ValueError):
        asyncio.run(c.call("core_user_update_users"))
    asyncio.run(c.call("core_webservice_get_site_info"))


def test_nucleo_traduz_para_mensagem_com_espera(monkeypatch):
    c, _ = cliente_limitado(1)
    nucleo._usar_cliente(c)
    asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    with pytest.raises(ToolError, match=r"Limite de 1 chamadas ao Moodle a cada 1 min.*Tente de novo em 1 min") as exc:
        asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    assert TOKEN not in str(exc.value)
