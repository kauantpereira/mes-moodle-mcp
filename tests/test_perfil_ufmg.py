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

IDP = "https://sistemas.ufmg.br/idp/login.jsp"


class Resposta:
    def __init__(self, headers, corpo="", status=200, url=BASE):
        self.headers, self._corpo, self.status, self.url = headers, corpo, status, url

    async def text(self):
        return self._corpo


class Requisicao:
    """APIRequestContext simulado (mesmos cookies da janela): responde conforme o modo."""

    def __init__(self, nav):
        self.nav, self.pedidos = nav, []

    async def get(self, url, max_redirects=None):
        assert max_redirects == 0  # nada de seguir redirecionamentos sozinho
        self.pedidos.append(url)
        return self.nav.modo.servir(url)


class Pagina:
    def __init__(self, nav):
        self.nav, self.fechada, self.url, self.conteudo = nav, False, "about:blank", None

    async def goto(self, url):
        self.nav.urls.append(url)
        self.url = self.nav.modo.navegar(url)

    async def set_content(self, html):
        self.conteudo = html

    def is_closed(self):
        return self.fechada

    async def wait_for_timeout(self, ms):
        self.nav.esperas += 1
        if self.nav.fechar_na_espera:
            raise ErroPlaywright("Target page, context or browser has been closed")
        if self.nav.esperas > 3 and self.conteudo is None:
            self.fechada = True


class Contexto:
    def __init__(self, nav):
        self.nav, self.request = nav, nav.requisicao

    async def new_page(self):
        self.nav.pagina = Pagina(self.nav)
        return self.nav.pagina


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
        self.requisicao = Requisicao(self)
        self.pagina = None
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


def _launch(url):
    """passport do pedido ao launch.php (o servidor que escolhe; o Moodle assina com ele)."""
    assert url.startswith(BASE + "/admin/tool/mobile/launch.php?")
    return parse_qs(urlsplit(url).query)["passport"][0]


class Logado:
    """O aluno entra e a janela termina no Moodle; o launch.php responde com o token no Location."""

    def navegar(self, url):
        return BASE + "/my/"

    def servir(self, url):
        return Resposta({"location": link_do_app(BASE, _launch(url))}, status=303)


class ViaPortal(Logado):
    """A janela abre no Minhas Turmas (mesmo host, fora do Moodle do semestre)."""

    def navegar(self, url):
        return url if "minhasturmas" in url else BASE + "/my/"


class ViaHtml(Logado):
    """O launch.php devolve uma página que tenta abrir moodlemobile:// por JavaScript."""

    def servir(self, url):
        corpo = f"<script>location.href='{link_do_app(BASE, _launch(url))}'</script>"
        return Resposta({"content-type": "text/html; charset=utf-8"}, corpo)


class SemSessao:
    """A janela parece logada (página do Moodle para visitantes), mas o launch.php manda ao IdP."""

    def navegar(self, url):
        return BASE + "/"

    def servir(self, url):
        saltos = {
            "launch.php": Resposta({"location": "/20262/login/index.php"}, status=303, url=url),
            "login/index.php": Resposta({"location": "/20262/auth/shibboleth/index.php"}, status=303, url=BASE + "/login/index.php"),
            "shibboleth": Resposta({"location": IDP}, status=302, url=BASE + "/auth/shibboleth/index.php"),
        }
        return next(r for chave, r in saltos.items() if chave in url)


class Nunca:
    """O aluno não termina o login: a janela fica no IdP."""

    def navegar(self, url):
        return IDP

    def servir(self, url):
        raise AssertionError("sem sessão não há busca do token")


@pytest.fixture
def simular(monkeypatch):
    monkeypatch.setattr(navegador, "_tem_tela", lambda: True)

    def criar(canais_ok=("chrome",), modo=None, instala=True):
        pw = Playwright(set(canais_ok), modo or Logado())
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
    from moodle_mcp.perfis import ufmg

    perfil = perfil_para(BASE)
    assert perfil.nome == "ufmg"
    assert perfil.fuso == "America/Sao_Paulo"
    assert perfil.janelas_manutencao == ((time(1, 30), time(6, 0)),)
    assert perfil.login is ufmg.entrar
    assert nucleo.metodo_de_login(BASE) is ufmg.entrar
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


def test_login_na_pagina_do_moodle_e_token_por_baixo(simular):
    """A janela abre no login do Moodle, o aluno entra e termina numa página normal; o token vem
    do launch.php pedido com a sessão da janela, sem o navegador ver o moodlemobile://."""
    pw = simular(canais_ok=("chrome",))
    interacao = Interacao()
    assert rodar(navegador.login_pelo_navegador(BASE, interacao)) == TOKEN
    assert pw.tentativas == ["chrome"]
    assert pw.urls == [BASE + "/login/index.php"]  # a janela nunca vai ao launch.php
    assert len(pw.requisicao.pedidos) == 1
    assert "Login concluído" in pw.pagina.conteudo and "token" not in pw.pagina.conteudo
    assert pw.fechado
    assert all(TOKEN not in a and "token=" not in a for a in interacao.avisos)


def test_pagina_inicial_do_portal_leva_ao_moodle_do_semestre(simular):
    from moodle_mcp.perfis import ufmg

    pw = simular(modo=ViaPortal())
    assert rodar(navegador.login_pelo_navegador(BASE, Interacao(), pagina_inicial=ufmg.MINHAS_TURMAS)) == TOKEN
    assert pw.urls == [ufmg.MINHAS_TURMAS, BASE + "/my/"]


def test_token_na_pagina_html_do_launch(simular):
    simular(modo=ViaHtml())
    assert rodar(navegador.login_pelo_navegador(BASE, Interacao())) == TOKEN


def test_sem_sessao_a_busca_nao_segue_para_o_login_da_instituicao(simular):
    """Se o Moodle ainda manda ao IdP, a busca para ali (não abre login por baixo) e a janela espera."""
    pw = simular(modo=SemSessao())
    with pytest.raises(LoginFalhou, match="fechada"):
        rodar(navegador.login_pelo_navegador(BASE, Interacao()))
    assert all(urlsplit(u).hostname == "virtual.ufmg.br" for u in pw.requisicao.pedidos)
    assert len(pw.requisicao.pedidos) == 3  # uma tentativa por página nova, não a cada meio segundo


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
    pw = simular(modo=Nunca())
    with pytest.raises(LoginFalhou, match="fechada.*se o aluno pedir"):
        rodar(navegador.login_pelo_navegador(BASE, Interacao()))
    assert pw.fechado

    pw = simular(modo=Nunca())
    pw.fechar_na_espera = True
    with pytest.raises(LoginFalhou, match="fechou") as exc:
        rodar(navegador.login_pelo_navegador(BASE, Interacao()))
    assert "closed" not in str(exc.value)


def test_tempo_esgotado(simular):
    pw = simular(modo=Nunca())
    with pytest.raises(LoginFalhou, match="Tempo esgotado"):
        rodar(navegador.capturar_token(BASE, Interacao(), tempo_s=0))
    assert pw.fechado


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


# ---------- um Moodle por semestre (ADR-0017) ----------


@pytest.fixture
def em(monkeypatch):
    """Fixa a data de hoje do perfil."""
    from datetime import date

    from moodle_mcp.perfis import ufmg

    def fixar(ano, mes, dia=15):
        monkeypatch.setattr(ufmg, "hoje", lambda: date(ano, mes, dia))
        return ufmg

    return fixar


@pytest.mark.parametrize(("mes", "codigo"), [(1, "20261"), (6, "20261"), (7, "20262"), (12, "20262")])
def test_semestre_atual_pela_data(em, mes, codigo):
    assert em(2026, mes).url_do_semestre(None) == f"https://virtual.ufmg.br/{codigo}"


@pytest.mark.parametrize(
    ("pedido", "codigo"),
    [("2026.1", "20261"), ("20251", "20251"), ("2025/2", "20252"), (" 2025-2 ", "20252"), ("Atual", "20262"), ("anterior", "20261"), ("", "20262")],
)
def test_formatos_de_semestre(em, pedido, codigo):
    assert em(2026, 11).url_do_semestre(pedido) == f"https://virtual.ufmg.br/{codigo}"


def test_anterior_ao_primeiro_semestre_e_o_segundo_do_ano_passado(em):
    assert em(2026, 3).url_do_semestre("anterior") == "https://virtual.ufmg.br/20252"


@pytest.mark.parametrize("pedido", ["2026.3", "primeiro", "26.1"])
def test_semestre_invalido(em, pedido):
    with pytest.raises(ValueError, match="2026.1"):
        em(2026, 11).url_do_semestre(pedido)


def test_sem_moodle_url_vale_o_semestre_atual_da_ufmg(em, monkeypatch):
    em(2026, 11)
    monkeypatch.delenv("MOODLE_URL", raising=False)
    nucleo._reiniciar()
    assert perfis.padrao().nome == "ufmg"
    assert nucleo.url_do_moodle() == BASE
    assert nucleo.url_do_moodle("anterior") == "https://virtual.ufmg.br/20261"


def test_reverter_o_perfil_volta_a_pedir_o_endereco(monkeypatch):
    """Critério do ADR-0009: sem o perfil ufmg, nada quebra; o núcleo só pede MOODLE_URL."""
    from mcp.server.mcpserver.exceptions import ToolError

    monkeypatch.delenv("MOODLE_URL", raising=False)
    monkeypatch.setattr(perfis, "PERFIS", tuple(p for p in perfis.carregados() if p.nome != "ufmg"))
    with pytest.raises(ToolError, match="MOODLE_URL"):
        nucleo.url_do_moodle()

