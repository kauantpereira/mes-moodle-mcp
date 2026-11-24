"""Cache curto (ADR-0005). Relógio simulado, sem rede. Token fictício."""

import asyncio

import httpx
import pytest

from moodle_mcp.cache import MAX_ENTRADAS, TTL_PADRAO, CacheCurto, chave
from moodle_mcp.client import MoodleClient, MoodleError
from moodle_mcp.limite import Limitador

TOKEN = "token-ficticio-123"
BASE = "https://moodle.exemplo.edu"


class Relogio:
    def __init__(self):
        self.agora = 1000.0

    def __call__(self):
        return self.agora


def montar(handler, ttl=TTL_PADRAO):
    r = Relogio()
    pedidos: list[httpx.Request] = []

    def registrar(req):
        pedidos.append(req)
        return handler(req)

    c = MoodleClient(
        BASE,
        TOKEN,
        transport=httpx.MockTransport(registrar),
        limitador=Limitador(relogio=r),
        cache=CacheCurto(ttl, relogio=r),
    )
    return c, pedidos, r


def rodar(coro):
    return asyncio.run(coro)


def test_padrao_cobre_disciplinas_e_conteudo_por_minutos():
    assert set(TTL_PADRAO) == {"core_enrol_get_users_courses", "core_course_get_contents"}
    assert all(60 <= v <= 900 for v in TTL_PADRAO.values())
    assert MAX_ENTRADAS > 0


def test_acerto_nao_vai_a_rede_nem_conta_no_limite():
    c, pedidos, _ = montar(lambda req: httpx.Response(200, json=[{"id": 1}]))
    assert rodar(c.call("core_enrol_get_users_courses", userid=7)) == [{"id": 1}]
    assert rodar(c.call("core_enrol_get_users_courses", userid=7)) == [{"id": 1}]
    assert len(pedidos) == 1
    assert c.limitador.total == 1


def test_expira_depois_da_validade():
    c, pedidos, r = montar(lambda req: httpx.Response(200, json=[]))
    rodar(c.call("core_course_get_contents", courseid=3))
    r.agora += TTL_PADRAO["core_course_get_contents"] - 1
    rodar(c.call("core_course_get_contents", courseid=3))
    assert len(pedidos) == 1
    r.agora += 1
    rodar(c.call("core_course_get_contents", courseid=3))
    assert len(pedidos) == 2 and c.limitador.total == 2


def test_parametros_diferentes_nao_colidem():
    c, pedidos, _ = montar(lambda req: httpx.Response(200, json={"curso": req.content.decode()}))
    a = rodar(c.call("core_course_get_contents", courseid=3))
    b = rodar(c.call("core_course_get_contents", courseid=4))
    assert a != b and len(pedidos) == 2
    rodar(c.call("core_course_get_contents", courseid=3, options=[{"name": "x", "value": 1}]))
    assert len(pedidos) == 3


def test_ordem_dos_parametros_nao_importa():
    assert chave("f", {"a": "1", "b": "2"}) == chave("f", {"b": "2", "a": "1"})


def test_erro_nao_e_guardado():
    respostas = iter([{"errorcode": "nopermissions"}, [{"id": 1}]])
    c, pedidos, _ = montar(lambda req: httpx.Response(200, json=next(respostas)))
    with pytest.raises(MoodleError):
        rodar(c.call("core_enrol_get_users_courses", userid=7))
    assert rodar(c.call("core_enrol_get_users_courses", userid=7)) == [{"id": 1}]
    assert len(pedidos) == 2


def test_erro_http_nao_e_guardado():
    respostas = iter([httpx.Response(500), httpx.Response(200, json=[])])
    c, pedidos, _ = montar(lambda req: next(respostas))
    with pytest.raises(httpx.HTTPStatusError):
        rodar(c.call("core_enrol_get_users_courses", userid=7))
    assert rodar(c.call("core_enrol_get_users_courses", userid=7)) == []
    assert len(pedidos) == 2


def test_funcao_fora_da_lista_nao_usa_cache():
    c, pedidos, _ = montar(lambda req: httpx.Response(200, json={"events": []}))
    for _ in range(2):
        rodar(c.call("core_calendar_get_action_events_by_timesort", timesortfrom=0))
    assert len(pedidos) == 2 and len(c.cache) == 0


def test_alterar_a_resposta_nao_altera_o_cache():
    c, _, _ = montar(lambda req: httpx.Response(200, json=[{"id": 1}]))
    primeira = rodar(c.call("core_enrol_get_users_courses", userid=7))
    primeira.append({"id": 99})
    assert rodar(c.call("core_enrol_get_users_courses", userid=7)) == [{"id": 1}]


def test_teto_de_entradas_descarta_a_mais_antiga():
    r = Relogio()
    cache = CacheCurto({"f": 60}, relogio=r, max_entradas=2)
    for i in range(3):
        cache.salvar(chave("f", {"i": str(i)}), i)
    assert len(cache) == 2
    assert cache.obter(chave("f", {"i": "0"})) == (False, None)
    assert cache.obter(chave("f", {"i": "2"})) == (True, 2)


def test_configuracao_invalida():
    with pytest.raises(ValueError):
        CacheCurto({"f": 0})
    with pytest.raises(ValueError):
        CacheCurto(max_entradas=0)
