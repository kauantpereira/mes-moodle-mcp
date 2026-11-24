"""Tela no Linux quando o app não repassa DISPLAY ao servidor (Claude Desktop). Sessão falsa em tmp_path."""

import pytest

from moodle_mcp import navegador


@pytest.fixture
def sessao(monkeypatch, tmp_path):
    """Sessão gráfica falsa: diretório de sockets do X e XDG_RUNTIME_DIR em tmp_path."""
    import os

    x11 = tmp_path / "x11"
    runtime = tmp_path / "runtime"
    x11.mkdir()
    runtime.mkdir()
    for var in ("DISPLAY", "WAYLAND_DISPLAY", "XAUTHORITY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))
    monkeypatch.setattr(navegador.sys, "platform", "linux")
    monkeypatch.setattr(navegador, "_DIR_X11", x11)
    monkeypatch.setattr(navegador.os, "environ", dict(os.environ))
    return x11, runtime


def test_sem_display_acha_a_sessao_x11_do_aluno(sessao):
    x11, runtime = sessao
    (x11 / "X1").touch()
    (runtime / "gdm").mkdir()
    (runtime / "gdm" / "Xauthority").touch()
    assert navegador._tem_tela()
    assert navegador.os.environ["DISPLAY"] == ":1"
    assert navegador.os.environ["XAUTHORITY"] == str(runtime / "gdm" / "Xauthority")


def test_sem_display_acha_a_sessao_wayland(sessao):
    _, runtime = sessao
    (runtime / "wayland-0").touch()
    (runtime / "wayland-0.lock").touch()
    assert navegador._tem_tela()
    assert navegador.os.environ["WAYLAND_DISPLAY"] == "wayland-0"


def test_sem_sessao_grafica_nao_ha_tela(sessao):
    assert not navegador._tem_tela()


def test_display_definido_nao_e_trocado(sessao, monkeypatch):
    x11, _ = sessao
    (x11 / "X1").touch()
    navegador.os.environ["DISPLAY"] = ":5"
    assert navegador._tem_tela()
    assert navegador.os.environ["DISPLAY"] == ":5"
