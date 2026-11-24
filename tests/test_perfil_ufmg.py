"""Perfil ufmg e captura do token pelo navegador, com Playwright simulado (nenhum navegador abre)."""

import asyncio
import base64
import hashlib
import pkgutil
from datetime import time
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.async_api import Error as ErroPlaywright

from moodle_mcp import login, navegador, nucleo, perfis
from moodle_mcp.login import LoginFalhou
from moodle_mcp.perfis import GENERICO, perfil_para

BASE = "https://virtual.ufmg.br/20262"
TOKEN = "token-ficticio-123"


def link_do_app(base, passport, token=TOKEN):
    assinatura = hashlib.md5((base + passport).encode()).hexdigest()
    return "moodlemobile://token=" + base64.b64encode(f"{assinatura}:::{token}".encode()).decode()


class Interacao:
    def __init__(self, pode_perguntar=True, link=None):
        self.pode_perguntar = pode_perguntar
        self.avisos: list[str] = []
        self.link = link

    async def avisar(self, mensagem):
        self.avisos.append(mensagem)

    async def pedir_link(self, mensagem):
        url = next(p for p in mensagem.split() if "launch.php" in p)
        return link_do_app(BASE, parse_qs(urlsplit(url).query)["passport"][0]) if self.link == "valido" else None


# ---------- Playwright simulado ----------


class Resposta:
    def __init__(self, headers, corpo=""):
        self.headers, self._corpo = headers, corpo

    async def text(self):
        return self._corpo


class Rota:
    def __init__(self, resposta):
        self.resposta, self.cumprida = resposta, None

    async def fetch(self, max_redirects=None):
        assert max_redirects == 0
        return self.resposta

    async def fulfill(self, **kw):
        self.cumprida = kw


class Pagina:
    def __init__(self, nav):
        self.nav, self.fechada, self.ouvintes = nav, False, {}

    def on(self, evento, f):
        self.ouvintes[evento] = f

    async def goto(self, url):
        self.nav.urls.append(url)
        passport = parse_qs(urlsplit(url).query)["passport"][0]
        await self.nav.modo(self, passport)

    def is_closed(self):
        return self.fechada

    async def wait_for_timeout(self, ms):
        self.nav.esperas += 1
        if self.nav.fechar_na_espera:
            raise ErroPlaywright("Target page, context or browser has been closed")
        if self.nav.esperas > 3:
            self.fechada = True


class Contexto:
    def __init__(self, nav):
        self.nav = nav

    async def route(self, padrao, handler):
        assert "launch.php" in padrao
        self.nav.handler = handler

    async def new_page(self):
        return Pagina(self.nav)


class Navegador:
    def __init__(self, dono):
        self.dono = dono

    async def new_context(self):
        return Contexto(self.dono)

    async def close(self):
        self.dono.fechado = True


class Playwright:
    """Simula `async_playwright()`. `canais_ok`: canais que abrem (None = Chromium do Playwright)."""

    def __init__(self, canais_ok, modo):
        self.canais_ok, self.modo = canais_ok, modo
        self.tentativas: list[str | None] = []
        self.urls: list[str] = []
        self.esperas = 0
        self.fechado = False
        self.fechar_na_espera = False
        self.handler = None
        self.chromium = self

    async def launch(self, headless, channel=None):
        assert headless is False
        self.tentativas.append(channel)
        if channel not in self.canais_ok:
            raise ErroPlaywright("Executable doesn't exist")
        return Navegador(self)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False


async def redireciona(pagina, passport):
    """O Moodle responde ao launch.php com Location: moodlemobile://token=..."""
    pagina.nav.rota = Rota(Resposta({"location": link_do_app(BASE, passport)}))
    await pagina.nav.handler(pagina.nav.rota)


async def via_console(pagina, passport):
    """Sem Location: o token só aparece no Console (o Chrome não abre moodlemobile://)."""
    pagina.nav.rota = None
    pagina.ouvintes["console"](type("Msg", (), {"text": "Failed to launch '" + link_do_app(BASE, passport) + "'"}))


async def nunca(pagina, passport):
    pagina.nav.rota = None


@pytest.fixture
def simular(monkeypatch):
    monkeypatch.setattr(navegador, "_tem_tela", lambda: True)

    def criar(canais_ok=("chrome",), modo=redireciona, instala=True):
        pw = Playwright(set(canais_ok), modo)
        monkeypatch.setattr(navegador, "_async_playwright", lambda: pw)
        instalacoes = []

        async def instalar():
            instalacoes.append(1)
            if instala:
                pw.canais_ok.add(None)
            return instala

        monkeypatch.setattr(navegador, "_instalar_chromium", instalar)
        pw.instalacoes = instalacoes
        return pw

    return criar


def rodar(coro):
    return asyncio.run(coro)


# ---------- perfil ----------


def test_perfil_ufmg_escolhido_pelo_host():
    perfil = perfil_para(BASE)
    assert perfil.nome == "ufmg"
    assert perfil.fuso == "America/Sao_Paulo"
    assert perfil.janelas_manutencao == ((time(1, 30), time(6, 0)),)
    assert perfil.login is navegador.login_pelo_navegador
    assert nucleo.metodo_de_login(BASE) is navegador.login_pelo_navegador
    assert perfil_para("https://moodle.exemplo.edu") is GENERICO


def test_reverter_o_perfil_volta_ao_login_generico(monkeypatch):
    """Sem perfis/ufmg.py (PR revertido), o Moodle da UFMG cai no GENERICO: senha ou fluxo do app."""
    originais = pkgutil.iter_modules
    monkeypatch.setattr(pkgutil, "iter_modules", lambda path: [m for m in originais(path) if m.name != "ufmg"])
    sem_ufmg = perfis._carregar()
    assert all(p.nome != "ufmg" for p in sem_ufmg)
    assert perfil_para(BASE, sem_ufmg) is GENERICO
    monkeypatch.setattr(perfis, "PERFIS", sem_ufmg)
    assert nucleo.metodo_de_login(BASE) is login.login_generico


# ---------- captura pelo navegador ----------


def test_captura_pelo_location_e_fecha_a_janela(simular):
    pw = simular(canais_ok=("chrome",))
    interacao = Interacao()
    assert rodar(navegador.login_pelo_navegador(BASE, interacao)) == TOKEN
    assert pw.tentativas == ["chrome"]
    assert pw.urls[0].startswith(BASE + "/admin/tool/mobile/launch.php?")
    assert pw.rota.cumprida["body"].count("Login concluído") == 1  # o aluno não vê o link
    assert pw.fechado
    assert all(TOKEN not in a and "token=" not in a for a in interacao.avisos)


def test_captura_pelo_console(simular):
    pw = simular(canais_ok=("chrome",), modo=via_console)
    assert rodar(navegador.login_pelo_navegador(BASE, Interacao())) == TOKEN


def test_ordem_chrome_edge_chromium(simular):
    pw = simular(canais_ok=("msedge",))
    rodar(navegador.login_pelo_navegador(BASE, Interacao()))
    assert pw.tentativas == ["chrome", "msedge"]

    pw = simular(canais_ok=(None,))
    rodar(navegador.login_pelo_navegador(BASE, Interacao()))
    assert pw.tentativas == ["chrome", "msedge", None] and pw.instalacoes == []


def test_sem_navegador_baixa_o_chromium_com_aviso(simular):
    pw = simular(canais_ok=())
    interacao = Interacao()
    assert rodar(navegador.login_pelo_navegador(BASE, interacao)) == TOKEN
    assert pw.instalacoes == [1]
    assert pw.tentativas == ["chrome", "msedge", None, None]
    assert any("150 MB" in a for a in interacao.avisos)


def test_download_falhou_cai_no_login_manual(simular):
    pw = simular(canais_ok=(), instala=False)
    assert rodar(navegador.login_pelo_navegador(BASE, Interacao(link="valido"))) == TOKEN
    assert pw.urls == []


def test_sem_navegador_pelo_chat_indica_o_login_manual_no_terminal(simular):
    simular(canais_ok=(), instala=False)
    with pytest.raises(LoginFalhou, match="moodle-mcp entrar .*--manual"):
        rodar(navegador.login_pelo_navegador(BASE, Interacao(pode_perguntar=False)))


def test_pelo_chat_o_navegador_funciona_sem_perguntar(simular):
    """Caminho normal da UFMG pelo chat: a interação do MCP nunca pergunta, e o SSO não precisa."""
    from moodle_mcp.login import InteracaoMCP

    simular()
    assert rodar(navegador.login_pelo_navegador(BASE, InteracaoMCP(None))) == TOKEN


def test_sem_playwright_cai_no_login_manual(monkeypatch):
    monkeypatch.setattr(navegador, "_tem_tela", lambda: True)

    def ausente():
        raise ImportError("sem playwright")

    monkeypatch.setattr(navegador, "_async_playwright", ausente)
    assert asyncio.run(navegador.login_pelo_navegador(BASE, Interacao(link="valido"))) == TOKEN


def test_sem_tela_nao_tenta_abrir(monkeypatch, simular):
    pw = simular()
    monkeypatch.setattr(navegador, "_tem_tela", lambda: False)
    assert asyncio.run(navegador.login_pelo_navegador(BASE, Interacao(link="valido"))) == TOKEN
    assert pw.tentativas == []


def test_janela_fechada_pelo_aluno(simular):
    pw = simular(modo=nunca)
    with pytest.raises(LoginFalhou, match="fechada"):
        rodar(navegador.login_pelo_navegador(BASE, Interacao()))
    assert pw.fechado

    pw = simular(modo=nunca)
    pw.fechar_na_espera = True
    with pytest.raises(LoginFalhou, match="fechou") as exc:
        rodar(navegador.login_pelo_navegador(BASE, Interacao()))
    assert "closed" not in str(exc.value)


def test_tempo_esgotado(simular):
    pw = simular(modo=nunca)
    with pytest.raises(LoginFalhou, match="Tempo esgotado"):
        rodar(navegador.capturar_token(BASE, Interacao(), tempo_s=0))
    assert pw.fechado


def test_pagina_sem_token_segue_normal(simular):
    """Respostas do launch.php sem token (ex.: tela de login) passam intactas ao navegador."""
    rota = Rota(Resposta({"content-type": "text/html"}, "<form>login</form>"))
    achado = {}
    asyncio.run(navegador._interceptar(achado)(rota))
    assert achado == {} and rota.cumprida == {"response": rota.resposta}


@pytest.mark.parametrize("primeiro", ["moodle_mcp.server", "moodle_mcp.perfis", "moodle_mcp.client"])
def test_perfil_ufmg_carrega_em_qualquer_ordem_de_importacao(primeiro):
    """Processo novo, como o servidor real: o perfil não pode cair no genérico por ciclo de importação."""
    import subprocess
    import sys

    codigo = (
        f"import {primeiro}\n"
        "from moodle_mcp.perfis import perfil_para\n"
        "assert perfil_para('https://virtual.ufmg.br/x').nome == 'ufmg'\n"
    )
    saida = subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True)
    assert saida.returncode == 0 and "não carregou" not in saida.stderr, saida.stderr
