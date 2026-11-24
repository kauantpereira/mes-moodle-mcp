"""Captura do token pelo navegador no fluxo do app (ADR-0002, ADR-0016), com Playwright.

Genérico (só API padrão do Moodle), usado pelo login de perfis de instituição com SSO.
Abre uma janela no `launch.php`, o aluno faz o login da instituição e o Moodle redireciona
para `moodlemobile://token=...`: a rota intercepta essa resposta, a janela fecha sozinha e o
token é conferido pela assinatura do `passport`. Nenhuma URL, cookie ou token é registrado.

Ordem de navegador: Chrome instalado → Edge instalado → Chromium do Playwright (baixado uma
vez, ~150 MB, com aviso) → login manual (o aluno cola o link num formulário).
"""

import asyncio
import os
import re
import sys
import time
from collections.abc import Callable
from typing import Any

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


def _tem_tela() -> bool:
    if sys.platform.startswith("linux"):
        return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    return True


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


def _procurar(texto: str | None, achado: dict[str, str]) -> bool:
    m = _RE_LINK.search(texto or "")
    if m:
        achado.setdefault("link", m.group(0))
    return bool(m)


def _interceptar(achado: dict[str, str]) -> Callable[[Any], Any]:
    async def rota(route: Any) -> None:
        # Busca o launch.php sem seguir o redirecionamento: o token vem no Location ou numa
        # página que tenta abrir moodlemobile:// por JavaScript.
        resp = await route.fetch(max_redirects=0)
        encontrou = _procurar(resp.headers.get("location"), achado)
        if not encontrou and "html" in resp.headers.get("content-type", ""):
            encontrou = _procurar(await resp.text(), achado)
        if encontrou:
            await route.fulfill(status=200, content_type="text/html; charset=utf-8", body=_PAGINA_FIM)
        else:
            await route.fulfill(response=resp)

    return rota


async def capturar_token(base_url: str, interacao: Interacao, tempo_s: int = TEMPO_LOGIN_S) -> str:
    """Abre o navegador no fluxo do app e devolve o token. NavegadorIndisponivel se não abrir."""
    if not _tem_tela():
        raise NavegadorIndisponivel
    try:
        gerenciador = _async_playwright()
    except ImportError:
        raise NavegadorIndisponivel from None
    passport = login.novo_passport()
    achado: dict[str, str] = {}
    try:
        async with gerenciador as pw:
            navegador = await _abrir(pw, interacao)
            try:
                contexto = await navegador.new_context()
                await contexto.route("**/admin/tool/mobile/launch.php*", _interceptar(achado))
                pagina = await contexto.new_page()
                # Rede de segurança: o Chrome avisa no Console quando não consegue abrir moodlemobile://.
                pagina.on("console", lambda msg: _procurar(msg.text, achado))
                await pagina.goto(login.url_de_lancamento(base_url, passport))
                await interacao.avisar("Abri o login do Moodle no navegador. Entre com a sua conta; a janela fecha sozinha.")
                limite = time.monotonic() + tempo_s
                proximo_aviso = time.monotonic() + INTERVALO_AVISO_S
                while "link" not in achado:
                    if pagina.is_closed():
                        raise LoginFalhou("A janela do navegador foi fechada antes de concluir o login.")
                    agora = time.monotonic()
                    if agora > limite:
                        raise LoginFalhou("Tempo esgotado sem concluir o login no navegador. Tente entrar de novo.")
                    if agora >= proximo_aviso:  # progresso mantém a tool viva no cliente
                        await interacao.avisar(f"Aguardando o login no navegador ({int((limite - agora) // 60) + 1} min restantes)...")
                        proximo_aviso = agora + INTERVALO_AVISO_S
                    await pagina.wait_for_timeout(500)
            finally:
                await navegador.close()
    except _erro_playwright():
        # Ex.: o aluno fechou a janela no meio de uma espera. Sem detalhes (podem ter URL).
        raise LoginFalhou("O navegador fechou ou falhou antes de concluir o login. Tente entrar de novo.") from None
    return login.decodificar_token_do_app(base_url, passport, achado["link"])


async def login_pelo_navegador(base_url: str, interacao: Interacao) -> str:
    """Login de perfil com SSO: navegador; sem navegador, login manual por formulário."""
    try:
        return await capturar_token(base_url, interacao)
    except NavegadorIndisponivel:
        await interacao.avisar("Não consegui abrir um navegador; vamos pelo login manual.")
        if not interacao.pode_perguntar:
            raise LoginFalhou(login.SEM_FORMULARIO) from None
        return await login.login_manual(base_url, interacao)
