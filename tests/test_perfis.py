"""Contrato dos perfis de instituição (ADR-0009). Perfis fictícios."""

from datetime import time

from moodle_mcp import perfis
from moodle_mcp.perfis import GENERICO, Perfil, perfil_para

EXEMPLO = Perfil(
    nome="exemplo",
    hosts=frozenset({"moodle.exemplo.edu"}),
    fuso="America/Sao_Paulo",
    janelas_manutencao=((time(1, 30), time(6, 0)),),
)


def test_escolhe_perfil_pelo_host():
    assert perfil_para("https://moodle.exemplo.edu/20262", (EXEMPLO,)) is EXEMPLO
    assert perfil_para("https://MOODLE.exemplo.edu", (EXEMPLO,)) is EXEMPLO


def test_sem_perfil_cai_no_generico():
    assert perfil_para("https://outro.exemplo.org", (EXEMPLO,)) is GENERICO
    assert perfil_para("http://localhost:8080", ()) is GENERICO


def test_generico_e_neutro():
    assert GENERICO.fuso == "UTC" and GENERICO.janelas_manutencao == () and GENERICO.login is None


def test_perfis_descobertos_sao_validos():
    assert all(isinstance(p, Perfil) and p.hosts for p in perfis.carregados())
