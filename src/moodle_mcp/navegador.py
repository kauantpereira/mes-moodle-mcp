"""Captura do token pelo navegador no fluxo do app (ADR-0002, ADR-0016), com Playwright.

Genérico (só API padrão do Moodle), usado pelo login de perfis de instituição com SSO.
A janela abre numa página web comum (a de login do Moodle, ou a que o perfil indicar) e o aluno
entra como em qualquer dia, terminando numa página normal do Moodle. Com a sessão aberta, o
servidor pede o token ao `launch.php` por baixo, com os cookies da janela: o redirecionamento
para `moodlemobile://token=...` nunca passa pelo navegador (sem diálogo de "abrir com outro
programa" e sem página de erro no fim). A janela mostra "Login concluído" e fecha; o token é
conferido pela assinatura do `passport`. Nenhuma URL, cookie ou token é registrado.

Ordem de navegador: Chrome instalado → Edge instalado → Chromium do Playwright (baixado uma
vez, ~150 MB, com aviso) → login manual (o aluno cola o link no terminal: `moodle-mcp entrar --manual`).
"""

import asyncio
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

from . import login
from .login import Interacao, LoginFalhou

TEMPO_LOGIN_S = 600
INTERVALO_AVISO_S = 15
_RE_LINK = re.compile(rf"{login.ESQUEMA_APP}://token=[A-Za-z0-9+/=]+")
_PAGINA_FIM = "<!doctype html><meta charset=utf-8><title>Moodle MCP</title><h2>Login concluído. Pode fechar esta janela.</h2>"


class NavegadorIndisponivel(Exception):
    """Nenhum navegador pôde ser aberto (sem Playwright, sem tela ou falha ao baixar)."""


def _async_playwright() -> Any:
    from playwright.async_api import async_playwright

    return async_playwright()


def _erro_playwright() -> type[Exception]:
    from playwright.async_api import Error

    return Error


_DIR_X11 = Path("/tmp/.X11-unix")


def _dir_runtime() -> Path:
    return Path(os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}")


def _achar_tela() -> dict[str, str]:
    """Variáveis da tela da sessão gráfica do aluno, quando o app não as repassa ao servidor.

    O Claude Desktop (Linux) inicia o servidor MCP só com HOME, PATH e poucas outras variáveis:
    sem DISPLAY/WAYLAND_DISPLAY, o Chrome não abre. Procura os sockets da sessão do próprio
    usuário (X11 em /tmp/.X11-unix, Wayland em XDG_RUNTIME_DIR) e o arquivo de autorização do X.
    """
    achadas: dict[str, str] = {}
    runtime = _dir_runtime()
    wayland = sorted(p for p in runtime.glob("wayland-*") if not p.name.endswith(".lock")) if runtime.is_dir() else []
    if wayland:
        achadas |= {"WAYLAND_DISPLAY": wayland[0].name, "XDG_RUNTIME_DIR": str(runtime)}
    meus = []
    if _DIR_X11.is_dir():
        for sock in sorted(_DIR_X11.glob("X*")):
            try:
                if sock.name[1:].isdigit() and sock.stat().st_uid == os.getuid():
                    meus.append(sock)
            except OSError:
                continue
    if meus:
        achadas["DISPLAY"] = f":{meus[0].name[1:]}"
        candidatos = [runtime / "gdm" / "Xauthority", Path.home() / ".Xauthority", *sorted(runtime.glob(".mutter-Xwaylandauth.*"))]
        autorizacao = next((c for c in candidatos if c.is_file()), None)
        if autorizacao is not None and not os.environ.get("XAUTHORITY"):
            achadas["XAUTHORITY"] = str(autorizacao)
    return achadas


def _tem_tela() -> bool:
    """Há tela para abrir a janela? No Linux, completa o ambiente com a sessão do aluno se faltar."""
    if not sys.platform.startswith("linux"):
        return True
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        os.environ.update(_achar_tela())  # o Chrome aberto pelo Playwright herda estas variáveis
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


async def _instalar_chromium() -> bool:
    """`playwright install chromium` com a saída descartada (o stdout é o canal do MCP)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "playwright", "install", "chromium",
            stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
        )
        return await asyncio.wait_for(proc.wait(), timeout=TEMPO_LOGIN_S) == 0
    except (OSError, TimeoutError):
        return False


async def _abrir(pw: Any, interacao: Interacao) -> Any:
    erro = _erro_playwright()
    for canal in ("chrome", "msedge"):
        try:
            return await pw.chromium.launch(headless=False, channel=canal)
        except erro:
            continue
    try:
        return await pw.chromium.launch(headless=False)
    except erro:
        pass
    await interacao.avisar("Não achei Chrome nem Edge. Vou baixar o navegador do Playwright (~150 MB, uma única vez)...")
    if not await _instalar_chromium():
        raise NavegadorIndisponivel
    try:
        return await pw.chromium.launch(headless=False)
    except erro:
        raise NavegadorIndisponivel from None


def _procurar(texto: str | None) -> str | None:
    m = _RE_LINK.search(texto or "")
    return m.group(0) if m else None


MAX_SALTOS = 10
# Caminhos de login/SSO no host do Moodle: enquanto a janela está num deles, o aluno não entrou.
_CAMINHOS_DE_LOGIN = ("/login", "/auth/", "/shibboleth.sso", "/saml")


def _parece_logado(url: str, host: str) -> bool:
    partes = urlsplit(url)
    return partes.hostname == host and not any(c in partes.path.lower() for c in _CAMINHOS_DE_LOGIN)


async def _buscar_token(requisicao: Any, base_url: str, passport: str) -> str | None:
    """Pede o token ao `launch.php` com a sessão da janela; None se o aluno ainda não entrou.

    Segue os redirecionamentos só dentro do Moodle: ir para outro host (o login da instituição)
    quer dizer que não há sessão ainda, e esta busca não deve abrir login nenhum.
    """
    host = urlsplit(base_url).hostname
    url = login.url_de_lancamento(base_url, passport)
    for _ in range(MAX_SALTOS):
        resp = await requisicao.get(url, max_redirects=0)
        destino = resp.headers.get("location")
        link = _procurar(destino)
        if link is None and "html" in resp.headers.get("content-type", ""):
            link = _procurar(await resp.text())
        if link is not None:
            return link
        if not (300 <= resp.status < 400 and destino):
            return None
        url = urljoin(resp.url, destino)
        if urlsplit(url).hostname != host:
            return None
    return None


async def capturar_token(
    base_url: str, interacao: Interacao, tempo_s: int = TEMPO_LOGIN_S, pagina_inicial: str | None = None
) -> str:
    """Abre o navegador para o aluno entrar e devolve o token. NavegadorIndisponivel se não abrir.

    `pagina_inicial`: onde a janela abre (padrão: o login do Moodle). Se for outra página da
    instituição (ex.: um portal de turmas no mesmo host), depois do login a janela vai ao Moodle.
    """
    if not _tem_tela():
        raise NavegadorIndisponivel
    try:
        gerenciador = _async_playwright()
    except ImportError:
        raise NavegadorIndisponivel from None
    base_url = base_url.rstrip("/")
    host = urlsplit(base_url).hostname or ""
    passport = login.novo_passport()
    link: str | None = None
    try:
        async with gerenciador as pw:
            navegador = await _abrir(pw, interacao)
            try:
                contexto = await navegador.new_context()
                pagina = await contexto.new_page()
                await pagina.goto(pagina_inicial or f"{base_url}/login/index.php")
                await interacao.avisar("Abri o login do Moodle no navegador. Entre com a sua conta; a janela fecha sozinha.")
                limite = time.monotonic() + tempo_s
                proximo_aviso = time.monotonic() + INTERVALO_AVISO_S
                tentados: set[str] = set()
                while link is None:
                    if pagina.is_closed():
                        raise LoginFalhou(
                            "A janela do navegador foi fechada antes de concluir o login. "
                            "Só abra o login de novo se o aluno pedir."
                        )
                    agora = time.monotonic()
                    if agora > limite:
                        raise LoginFalhou("Tempo esgotado sem concluir o login no navegador. Só tente de novo se o aluno pedir.")
                    if agora >= proximo_aviso:  # progresso mantém a tool viva no cliente
                        await interacao.avisar(f"Aguardando o login no navegador ({int((limite - agora) // 60) + 1} min restantes)...")
                        proximo_aviso = agora + INTERVALO_AVISO_S
                    url = pagina.url
                    if url not in tentados and _parece_logado(url, host):
                        tentados.add(url)
                        if url == base_url or url.startswith(base_url + "/"):
                            link = await _buscar_token(contexto.request, base_url, passport)
                            continue
                        # Outra página da instituição (ex.: portal de turmas): leva a janela ao Moodle.
                        await pagina.goto(f"{base_url}/my/")
                        continue
                    await pagina.wait_for_timeout(500)
                await pagina.set_content(_PAGINA_FIM)
                await pagina.wait_for_timeout(1500)
            finally:
                await navegador.close()
    except _erro_playwright():
        # Ex.: o aluno fechou a janela no meio de uma espera. Sem detalhes (podem ter URL).
        raise LoginFalhou(
            "O navegador fechou ou falhou antes de concluir o login. Só abra o login de novo se o aluno pedir."
        ) from None
    return login.decodificar_token_do_app(base_url, passport, link)


async def login_pelo_navegador(base_url: str, interacao: Interacao, pagina_inicial: str | None = None) -> str:
    """Login de perfil com SSO: navegador; sem navegador, login manual (só no terminal)."""
    try:
        return await capturar_token(base_url, interacao, pagina_inicial=pagina_inicial)
    except NavegadorIndisponivel:
        if not interacao.pode_perguntar:
            raise LoginFalhou("Não consegui abrir um navegador. " + login.no_terminal(manual=True)) from None
        await interacao.avisar("Não consegui abrir um navegador; vamos pelo login manual.")
        return await login.login_manual(base_url, interacao)
