"""Login genérico (senha e fluxo do app), sem rede nem navegador. Dados fictícios."""

import asyncio
import base64
import hashlib
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from mcp.server.elicitation import render_elicitation_schema

from moodle_mcp import login
from moodle_mcp.login import LoginFalhou

BASE = "https://moodle.exemplo.edu"
TOKEN = "token-ficticio-123"
SENHA = "senha-ficticia-456"


def link_do_app(base: str, passport: str, token: str = TOKEN) -> str:
    assinatura = hashlib.md5((base + passport).encode()).hexdigest()
    return "moodlemobile://token=" + base64.b64encode(f"{assinatura}:::{token}:::privado".encode()).decode()


class InteracaoFalsa:
    def __init__(self, metodo=None, credenciais=None, link=None, pode_perguntar=True):
        self.pode_perguntar = pode_perguntar
        self.metodo, self.credenciais, self.link = metodo, credenciais, link
        self.mensagens: list[str] = []

    async def avisar(self, mensagem):
        self.mensagens.append(mensagem)

    async def escolher_metodo(self, mensagem):
        self.mensagens.append(mensagem)
        return self.metodo

    async def pedir_credenciais(self, mensagem):
        self.mensagens.append(mensagem)
        return self.credenciais

    async def pedir_link(self, mensagem):
        self.mensagens.append(mensagem)
        if callable(self.link):
            return self.link(mensagem)
        return self.link


@pytest.fixture
def moodle(monkeypatch):
    """Simula login/token.php; devolve a lista de requisições."""
    class Pedidos(list):
        responder = None

    pedidos = Pedidos()
    resposta = {"valor": httpx.Response(200, json={"token": TOKEN, "privatetoken": "x"})}

    def handler(req):
        pedidos.append(req)
        r = resposta["valor"]
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setattr(login, "transporte", httpx.MockTransport(handler))
    pedidos.responder = lambda r: resposta.__setitem__("valor", r)
    return pedidos


# ---------- fluxo do app ----------


def test_url_de_lancamento_usa_servico_do_app():
    url = login.url_de_lancamento(BASE + "/", "abc123")
    partes = urlsplit(url)
    assert url.startswith(f"{BASE}/admin/tool/mobile/launch.php?")
    assert parse_qs(partes.query) == {"service": ["moodle_mobile_app"], "passport": ["abc123"], "urlscheme": ["moodlemobile"]}


def test_decodifica_link_do_app():
    assert login.decodificar_token_do_app(BASE, "abc123", link_do_app(BASE, "abc123")) == TOKEN
    # Aceita só o que vem depois de token=, e sem o padding.
    so_valor = link_do_app(BASE, "abc123").split("token=")[1].rstrip("=")
    assert login.decodificar_token_do_app(BASE, "abc123", so_valor) == TOKEN


def test_link_de_outro_login_e_recusado():
    with pytest.raises(LoginFalhou, match="assinatura"):
        login.decodificar_token_do_app(BASE, "abc123", link_do_app(BASE, "outro"))
    with pytest.raises(LoginFalhou, match="assinatura"):
        login.decodificar_token_do_app(BASE, "abc123", link_do_app("https://outro.exemplo.edu", "abc123"))


@pytest.mark.parametrize("link", ["", "moodlemobile://token=%%%", "moodlemobile://token=" + base64.b64encode(b"sem-separador").decode()])
def test_link_invalido(link):
    with pytest.raises(LoginFalhou):
        login.decodificar_token_do_app(BASE, "abc123", link)


def test_login_manual_mostra_link_e_decodifica():
    def colar(mensagem):
        url = next(p for p in mensagem.split() if "launch.php" in p)
        passport = parse_qs(urlsplit(url).query)["passport"][0]
        return link_do_app(BASE, passport)

    interacao = InteracaoFalsa(link=colar)
    assert asyncio.run(login.login_manual(BASE, interacao)) == TOKEN
    assert "launch.php" in interacao.mensagens[0]


def test_login_manual_cancelado():
    with pytest.raises(LoginFalhou, match="cancelado"):
        asyncio.run(login.login_manual(BASE, InteracaoFalsa(link=None)))


# ---------- senha ----------


def test_login_por_senha(moodle):
    assert asyncio.run(login.login_senha(BASE, "aluno", SENHA)) == TOKEN
    (req,) = moodle
    assert req.url == f"{BASE}/login/token.php"
    assert req.method == "POST"
    corpo = parse_qs(req.content.decode())
    assert corpo == {"username": ["aluno"], "password": [SENHA], "service": ["moodle_mobile_app"]}
    assert SENHA not in str(req.url)


@pytest.mark.parametrize(
    "resposta, mensagem",
    [
        (httpx.Response(200, json={"error": "Usuário inválido " + SENHA, "errorcode": "invalidlogin"}), "incorretos"),
        (httpx.Response(200, json={"error": "x", "errorcode": "servicenotavailable"}), "moodle_mobile_app"),
        (httpx.Response(200, json={"error": "x", "errorcode": "outro"}), "recusou"),
        (httpx.Response(303, headers={"location": "https://sso.exemplo.edu/?senha=" + SENHA}), "SSO"),
        (httpx.Response(500, text="erro " + SENHA), "recusou"),
        (httpx.Response(200, text="<html>" + SENHA), "inesperada"),
        (httpx.ConnectError("falhou com " + SENHA), "conexão"),
    ],
)
def test_erros_do_login_por_senha_sem_dado_sensivel(moodle, resposta, mensagem):
    moodle.responder(resposta)
    with pytest.raises(LoginFalhou, match=mensagem) as exc:
        asyncio.run(login.login_senha(BASE, "aluno", SENHA))
    assert SENHA not in str(exc.value) and "aluno" not in str(exc.value)
    assert exc.value.__context__ is None or exc.value.__suppress_context__


def test_senha_so_por_https(moodle):
    with pytest.raises(LoginFalhou, match="HTTPS"):
        asyncio.run(login.login_senha("http://moodle.exemplo.edu", "aluno", SENHA))
    assert moodle == []
    # Moodle local pode ser HTTP.
    assert asyncio.run(login.login_senha("http://localhost:8080", "aluno", SENHA)) == TOKEN


# ---------- genérico ----------


def test_generico_por_senha(moodle):
    interacao = InteracaoFalsa(metodo="senha", credenciais=(" aluno ", SENHA))
    assert asyncio.run(login.login_generico(BASE, interacao)) == TOKEN
    assert parse_qs(moodle[0].content.decode())["username"] == ["aluno"]
    assert all(SENHA not in m for m in interacao.mensagens)


def test_generico_pelo_fluxo_do_app(moodle):
    def colar(mensagem):
        url = next(p for p in mensagem.split() if "launch.php" in p)
        return link_do_app(BASE, parse_qs(urlsplit(url).query)["passport"][0])

    assert asyncio.run(login.login_generico(BASE, InteracaoFalsa(metodo="app", link=colar))) == TOKEN
    assert moodle == []


@pytest.mark.parametrize("interacao", [InteracaoFalsa(metodo=None), InteracaoFalsa(metodo="senha", credenciais=None)])
def test_generico_cancelado(moodle, interacao):
    with pytest.raises(LoginFalhou, match="cancelado"):
        asyncio.run(login.login_generico(BASE, interacao))
    assert moodle == []


def test_sem_formulario_indica_o_terminal():
    with pytest.raises(LoginFalhou, match="moodle-mcp entrar"):
        asyncio.run(login.login_generico(BASE, InteracaoFalsa(pode_perguntar=False)))


# ---------- interação MCP ----------


def test_formularios_seguem_o_formato_de_elicitation():
    for modelo in (login._Metodo, login._Credenciais, login._Link):
        render_elicitation_schema(modelo)  # levanta TypeError se o cliente não puder mostrar


def test_interacao_mcp_sem_contexto_nao_pergunta():
    interacao = login.InteracaoMCP(None)
    assert interacao.pode_perguntar is False
    asyncio.run(interacao.avisar("ok"))  # sem contexto, avisar não falha
    with pytest.raises(LoginFalhou, match="elicitation"):
        asyncio.run(interacao.pedir_link("x"))
