"""Acesso ao Moodle pelas tools: configuração e tradução de erros. Token fictício."""

import asyncio

import httpx
import pytest
from mcp.server.mcpserver.exceptions import ToolError

from moodle_mcp import chaveiro, login, nucleo
from moodle_mcp.client import MoodleClient
from moodle_mcp.perfis import GENERICO, Perfil

TOKEN = "token-ficticio-123"


@pytest.fixture(autouse=True)
def limpar(monkeypatch):
    monkeypatch.delenv("MOODLE_URL", raising=False)
    monkeypatch.delenv("MOODLE_TOKEN", raising=False)
    nucleo._reiniciar()
    yield
    nucleo._reiniciar()


def com_resposta(monkeypatch, handler):
    c = MoodleClient("https://moodle.exemplo.edu", TOKEN, transport=httpx.MockTransport(handler))
    monkeypatch.setattr(nucleo, "_cliente", c)


def test_sem_url_configurada():
    with pytest.raises(ToolError, match="MOODLE_URL"):
        nucleo.cliente()


def test_sem_token(monkeypatch):
    monkeypatch.setenv("MOODLE_URL", "https://moodle.exemplo.edu")
    with pytest.raises(ToolError, match="token"):
        nucleo.cliente()


def test_url_sem_https(monkeypatch):
    monkeypatch.setenv("MOODLE_URL", "http://moodle.exemplo.edu")
    monkeypatch.setenv("MOODLE_TOKEN", TOKEN)
    with pytest.raises(ToolError, match="HTTPS"):
        nucleo.cliente()


def test_cliente_unico_por_processo(monkeypatch):
    monkeypatch.setenv("MOODLE_URL", "https://moodle.exemplo.edu/")
    monkeypatch.setenv("MOODLE_TOKEN", TOKEN)
    assert nucleo.cliente() is nucleo.cliente()
    assert nucleo.cliente().base_url == "https://moodle.exemplo.edu"


def test_token_expirado_vira_dica_de_login(monkeypatch):
    com_resposta(
        monkeypatch,
        lambda r: httpx.Response(200, json={"errorcode": "invalidtoken", "message": "Token inválido"}),
    )
    with pytest.raises(ToolError, match="token expirou ou foi revogado") as exc:
        asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    mensagem = str(exc.value)
    assert "entrar" in mensagem
    assert "MOODLE_TOKEN" in mensagem
    assert TOKEN not in mensagem
    assert "https://moodle.exemplo.edu" not in mensagem
    assert "Token inválido" not in mensagem


def test_outro_errorcode_mantem_mensagem_generica(monkeypatch):
    com_resposta(
        monkeypatch,
        lambda r: httpx.Response(
            200,
            json={"errorcode": "accessexception", "message": "detalhe interno secreto"},
        ),
    )
    with pytest.raises(ToolError) as exc:
        asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    mensagem = str(exc.value)
    assert mensagem == "O Moodle recusou core_webservice_get_site_info."
    assert "entrar" not in mensagem
    assert "MOODLE_TOKEN" not in mensagem
    assert TOKEN not in mensagem
    assert "https://moodle.exemplo.edu" not in mensagem
    assert "detalhe interno secreto" not in mensagem


def test_funcao_de_escrita_vira_toolerror(monkeypatch):
    com_resposta(monkeypatch, lambda r: httpx.Response(200, json={}))
    with pytest.raises(ToolError, match="só leitura"):
        asyncio.run(nucleo.chamar("core_user_update_users"))


def test_falha_de_rede_sem_token(monkeypatch):
    def falha(r):
        raise httpx.ConnectError("sem rede")

    com_resposta(monkeypatch, falha)
    with pytest.raises(ToolError, match="Falha de conexão com o Moodle") as exc:
        asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    assert TOKEN not in str(exc.value)
    assert "sem rede" not in str(exc.value)


def test_erro_rest_nao_expoe_mensagem_bruta(monkeypatch):
    com_resposta(monkeypatch, lambda r: httpx.Response(200, json={"errorcode": "invalidtoken", "message": "token super secreto"}))
    with pytest.raises(ToolError) as exc:
        asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    assert "token super secreto" not in str(exc.value)


# ---------- token, chaveiro e login sob demanda (ADR-0016) ----------

BASE = "https://moodle.exemplo.edu"


@pytest.fixture
def moodle(monkeypatch):
    """Moodle simulado para os clientes criados pelo login; registra os tokens recebidos."""
    tokens: list[str] = []

    def handler(req):
        token = dict(httpx.QueryParams(req.content.decode()))["wstoken"]
        tokens.append(token)
        if token == "token-recusado-999":
            return httpx.Response(200, json={"errorcode": "invalidtoken", "message": "x"})
        return httpx.Response(200, json={"userid": 7, "sitename": "Moodle"})

    monkeypatch.setenv("MOODLE_URL", BASE + "/")
    monkeypatch.setattr(nucleo, "_transporte", httpx.MockTransport(handler))
    return tokens


def com_login(monkeypatch, token=TOKEN):
    """Perfil simulado cujo login devolve `token` e conta as chamadas."""
    chamadas: list[tuple[str, object]] = []

    async def entrar(base_url, interacao):
        chamadas.append((base_url, interacao))
        await asyncio.sleep(0)
        return token

    monkeypatch.setattr(nucleo, "perfil_para", lambda url: Perfil(nome="teste", hosts=frozenset({"moodle.exemplo.edu"}), login=entrar))
    return chamadas


def test_token_vem_do_chaveiro(monkeypatch, moodle, chaveiro_falso):
    chaveiro.salvar(BASE, TOKEN)
    assert asyncio.run(nucleo.chamar("core_webservice_get_site_info"))["userid"] == 7
    assert moodle == [TOKEN]


def test_login_feito_no_terminal_vale_sem_reiniciar(monkeypatch, moodle, chaveiro_falso):
    """Token expirado + `moodle-mcp entrar` no terminal: o servidor rodando passa ao token novo."""
    chaveiro.salvar(BASE, "token-antigo-111")
    asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    limitador = nucleo.cliente().limitador
    chaveiro.salvar(BASE, "token-novo-222")  # o que o terminal faz
    asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    assert moodle == ["token-antigo-111", "token-novo-222"]
    assert nucleo.cliente().limitador is limitador  # o limite de chamadas continua contando


def test_moodle_token_tem_prioridade(monkeypatch, moodle):
    chaveiro.salvar(BASE, "token-do-chaveiro-1")
    monkeypatch.setenv("MOODLE_TOKEN", TOKEN)
    asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    assert moodle == [TOKEN]


def test_primeira_tool_sem_token_faz_login_e_continua(monkeypatch, moodle):
    chamadas = com_login(monkeypatch)
    assert asyncio.run(nucleo.chamar("core_webservice_get_site_info"))["userid"] == 7
    assert [c[0] for c in chamadas] == [BASE]
    assert chaveiro.ler(BASE) == TOKEN
    # Próxima chamada usa o cliente já logado.
    asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    assert len(chamadas) == 1


def test_tools_em_paralelo_fazem_um_login_so(monkeypatch, moodle):
    chamadas = com_login(monkeypatch)

    async def varias():
        await asyncio.gather(*(nucleo.chamar("core_webservice_get_site_info") for _ in range(3)))

    asyncio.run(varias())
    assert len(chamadas) == 1


def test_login_usa_o_contexto_da_tool(monkeypatch, moodle):
    chamadas = com_login(monkeypatch)
    ctx = object()

    async def tool():
        with nucleo.contexto_da_chamada(ctx):
            await nucleo.chamar("core_webservice_get_site_info")

    asyncio.run(tool())
    interacao = chamadas[0][1]
    assert isinstance(interacao, login.InteracaoMCP) and interacao._ctx is ctx


def test_token_recusado_nao_e_guardado(monkeypatch, moodle):
    com_login(monkeypatch, token="token-recusado-999")
    with pytest.raises(ToolError, match="não aceitou o token") as exc:
        asyncio.run(nucleo.entrar(object()))  # type: ignore[arg-type]
    assert "token-recusado-999" not in str(exc.value)
    assert chaveiro.ler(BASE) is None
    assert nucleo._cliente is None


def test_falha_de_login_vira_toolerror(monkeypatch, moodle):
    async def falha(base_url, interacao):
        raise login.LoginFalhou("Usuário ou senha incorretos.")

    monkeypatch.setattr(nucleo, "perfil_para", lambda url: Perfil(nome="teste", login=falha))
    with pytest.raises(ToolError, match="incorretos"):
        asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    assert moodle == []


def test_entrar_troca_de_conta_e_mantem_o_limite(monkeypatch, moodle):
    chaveiro.salvar(BASE, "token-antigo-111")
    antigo = nucleo.cliente()
    com_login(monkeypatch, token="token-novo-222")
    assert asyncio.run(nucleo.entrar(object())) == {"conectado": True, "token_no_chaveiro": True}  # type: ignore[arg-type]
    assert nucleo.cliente() is not antigo
    assert nucleo.cliente().limitador is antigo.limitador
    assert chaveiro.ler(BASE) == "token-novo-222"


def test_entrar_com_moodle_token_definido(monkeypatch, moodle):
    monkeypatch.setenv("MOODLE_TOKEN", TOKEN)
    chamadas = com_login(monkeypatch)
    with pytest.raises(ToolError, match="MOODLE_TOKEN"):
        asyncio.run(nucleo.entrar(object()))  # type: ignore[arg-type]
    assert chamadas == []


def test_entrar_exige_https(monkeypatch, moodle):
    monkeypatch.setenv("MOODLE_URL", "http://moodle.exemplo.edu")
    chamadas = com_login(monkeypatch)
    with pytest.raises(ToolError, match="HTTPS"):
        asyncio.run(nucleo.entrar(object()))  # type: ignore[arg-type]
    assert chamadas == []


def test_sem_chaveiro_token_fica_na_memoria(monkeypatch, moodle):
    from keyring.errors import KeyringError

    def indisponivel(*a):
        raise KeyringError("sem backend")

    monkeypatch.setattr(chaveiro.keyring, "get_password", indisponivel)
    monkeypatch.setattr(chaveiro.keyring, "set_password", indisponivel)
    com_login(monkeypatch)
    assert asyncio.run(nucleo.entrar(object()))["token_no_chaveiro"] is False  # type: ignore[arg-type]
    asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    assert moodle == [TOKEN, TOKEN]


def test_generico_pelo_chat_explica_o_terminal(monkeypatch, moodle):
    monkeypatch.setattr(nucleo, "perfil_para", lambda url: GENERICO)
    with pytest.raises(ToolError, match="moodle-mcp entrar"):
        asyncio.run(nucleo.chamar("core_webservice_get_site_info"))


def test_metodo_de_login_vem_do_perfil(monkeypatch):
    async def proprio(base_url, interacao):
        return TOKEN

    monkeypatch.setattr(nucleo, "perfil_para", lambda url: GENERICO)
    assert nucleo.metodo_de_login(BASE) is login.login_generico
    monkeypatch.setattr(nucleo, "perfil_para", lambda url: Perfil(nome="x", login=proprio))
    assert nucleo.metodo_de_login(BASE) is proprio
