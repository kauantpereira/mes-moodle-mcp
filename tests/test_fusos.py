"""Os fusos horários precisam funcionar mesmo sem banco de fusos no sistema (caso do Windows)."""

import zoneinfo
from zoneinfo import ZoneInfo

import pytest


@pytest.fixture
def sem_banco_do_sistema():
    zoneinfo.reset_tzpath(to=[])
    ZoneInfo.clear_cache()
    yield
    zoneinfo.reset_tzpath()
    ZoneInfo.clear_cache()


def test_fusos_usados_pelo_plugin_vem_do_pacote_tzdata(sem_banco_do_sistema):
    assert ZoneInfo("America/Sao_Paulo").key == "America/Sao_Paulo"
    assert ZoneInfo("UTC").key == "UTC"


def test_cliente_do_moodle_nasce_sem_banco_de_fusos_do_sistema(sem_banco_do_sistema):
    from moodle_mcp.client import MoodleClient

    # A janela de manutenção do perfil da UFMG cria o fuso ao construir o cliente.
    MoodleClient("https://virtual.ufmg.br/20262", "x")
