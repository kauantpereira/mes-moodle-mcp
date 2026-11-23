"""Cliente da API do Moodle, sem rede: respostas simuladas com httpx.MockTransport. Token fictício."""

import asyncio
from urllib.parse import parse_qs

import httpx
import pytest

from moodle_mcp.client import (
    FUNCOES_PERMITIDAS,
    FuncaoNaoPermitida,
    MoodleClient,
    MoodleError,
    _achatar,
)

BASE = "https://moodle.exemplo.edu"
TOKEN = "token-ficticio-123"


def cliente(handler, base=BASE):
    pedidos: list[httpx.Request] = []

    def registrar(req: httpx.Request) -> httpx.Response:
        pedidos.append(req)
        return handler(req)

    return MoodleClient(base, TOKEN, transport=httpx.MockTransport(registrar)), pedidos


def rodar(coro):
    return asyncio.run(coro)


def test_achatar_listas_dicts_e_booleanos():
    assert _achatar({"courseids": [3, 5], "options": [{"name": "x", "value": True}], "vazio": None}) == {
        "courseids[0]": "3",
        "courseids[1]": "5",
        "options[0][name]": "x",
        "options[0][value]": "1",
    }


def test_call_manda_token_no_corpo_e_nao_na_url():
    c, pedidos = cliente(lambda req: httpx.Response(200, json={"ok": True}))
    assert rodar(c.call("core_enrol_get_users_courses", userid=7)) == {"ok": True}
    req = pedidos[0]
    assert req.url.path == "/webservice/rest/server.php"
    assert req.url.params["wsfunction"] == "core_enrol_get_users_courses"
    assert req.url.params["moodlewsrestformat"] == "json"
    assert TOKEN not in str(req.url)
    corpo = parse_qs(req.content.decode())
    assert corpo["wstoken"] == [TOKEN] and corpo["userid"] == ["7"]


def test_erro_do_moodle_vira_moodleerror_sem_debuginfo():
    resposta = {"exception": "x", "errorcode": "invalidtoken", "message": "Token inválido", "debuginfo": "segredo"}
    c, _ = cliente(lambda req: httpx.Response(200, json=resposta))
    with pytest.raises(MoodleError) as exc:
        rodar(c.call("core_webservice_get_site_info"))
    assert exc.value.errorcode == "invalidtoken"
    assert "segredo" not in str(exc.value)


def test_funcao_fora_da_lista_e_barrada_antes_da_requisicao():
    c, pedidos = cliente(lambda req: httpx.Response(200, json={}))
    with pytest.raises(FuncaoNaoPermitida):
        rodar(c.call("mod_forum_add_discussion", forumid=1))
    assert pedidos == []


def test_lista_de_funcoes_so_tem_leitura():
    assert all("_get_" in f for f in FUNCOES_PERMITIDAS)
    assert not any(f.startswith("mod_forum_") for f in FUNCOES_PERMITIDAS)


def test_site_info_fica_em_cache():
    c, pedidos = cliente(lambda req: httpx.Response(200, json={"userid": 42}))
    assert rodar(c.userid()) == 42
    assert rodar(c.userid()) == 42
    assert len(pedidos) == 1


@pytest.mark.parametrize("base", ["http://moodle.exemplo.edu", "ftp://moodle.exemplo.edu"])
def test_recusa_moodle_sem_https(base):
    with pytest.raises(ValueError):
        MoodleClient(base, TOKEN)


@pytest.mark.parametrize("base", [f"https://{TOKEN}@moodle.exemplo.edu", "https://moodle.exemplo.edu/?token=segredo"])
def test_recusa_url_com_credenciais_ou_query(base):
    with pytest.raises(ValueError):
        MoodleClient(base, TOKEN)


def test_aceita_http_em_moodle_local():
    assert MoodleClient("http://localhost:8080/", TOKEN).base_url == "http://localhost:8080"


def test_repr_nao_mostra_token():
    assert TOKEN not in repr(MoodleClient(BASE, TOKEN))


def test_baixar_arquivo_do_proprio_host():
    c, pedidos = cliente(lambda req: httpx.Response(200, content=b"conteudo"))
    assert rodar(c.baixar(f"{BASE}/webservice/pluginfile.php/1/a.pdf", 100)) == b"conteudo"
    assert pedidos[0].url.params["token"] == TOKEN


def test_baixar_recusa_outro_host_sem_requisicao():
    c, pedidos = cliente(lambda req: httpx.Response(200, content=b"x"))
    with pytest.raises(ValueError, match="fora do host"):
        rodar(c.baixar("https://atacante.exemplo/a.pdf", 100))
    assert pedidos == []


def test_baixar_recusa_redirecionamento_para_outro_host():
    def handler(req):
        return httpx.Response(302, headers={"location": "https://atacante.exemplo/roubo"})

    c, pedidos = cliente(handler)
    with pytest.raises(ValueError, match="fora do host") as exc:
        rodar(c.baixar(f"{BASE}/webservice/pluginfile.php/1/a.pdf", 100))
    assert len(pedidos) == 1
    assert TOKEN not in str(exc.value)


def test_baixar_respeita_limite_de_tamanho():
    c, _ = cliente(lambda req: httpx.Response(200, content=b"x" * 101))
    with pytest.raises(ValueError, match="grande demais"):
        rodar(c.baixar(f"{BASE}/webservice/pluginfile.php/1/a.pdf", 100))


def test_baixar_erro_http_sem_url_nem_token():
    c, _ = cliente(lambda req: httpx.Response(403))
    with pytest.raises(ValueError) as exc:
        rodar(c.baixar(f"{BASE}/webservice/pluginfile.php/1/a.pdf", 100))
    assert "403" not in str(exc.value)
    assert TOKEN not in str(exc.value) and BASE not in str(exc.value)


def test_resposta_invalida_nao_vaza_corpo():
    c, _ = cliente(lambda req: httpx.Response(200, content=b"segredo privado"))
    with pytest.raises(ValueError) as exc:
        rodar(c.call("core_webservice_get_site_info"))
    assert "segredo privado" not in str(exc.value)


def test_erro_do_moodle_nao_vaza_mensagem():
    c, _ = cliente(lambda req: httpx.Response(200, json={"errorcode": "invalidtoken", "message": "senha e token secreto"}))
    with pytest.raises(MoodleError) as exc:
        rodar(c.call("core_webservice_get_site_info"))
    assert "senha e token secreto" not in str(exc.value)


def test_falha_transporte_download_sem_detalhes():
    def falhar(req):
        raise httpx.ConnectError("https://usuario:senha@moodle.exemplo.edu?token=segredo")
    c, _ = cliente(falhar)
    with pytest.raises(ValueError) as exc:
        rodar(c.baixar(f"{BASE}/arquivo?token=antigo", 100))
    assert str(exc.value) == "falha de transporte ao baixar arquivo"
    assert "senha" not in str(exc.value) and "segredo" not in repr(exc.value.__cause__)
