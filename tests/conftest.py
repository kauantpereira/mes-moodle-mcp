"""Nenhum teste toca o chaveiro real do sistema: backend do keyring em memória."""

import httpx
import keyring.core
import pytest
from keyring.backend import KeyringBackend
from keyring.errors import PasswordDeleteError


class ChaveiroEmMemoria(KeyringBackend):
    priority = 1

    def __init__(self):
        super().__init__()
        self.dados: dict[tuple[str, str], str] = {}

    def get_password(self, service, username):
        return self.dados.get((service, username))

    def set_password(self, service, username, password):
        self.dados[(service, username)] = password

    def delete_password(self, service, username):
        if self.dados.pop((service, username), None) is None:
            raise PasswordDeleteError("não existe")


@pytest.fixture(autouse=True)
def chaveiro_falso(monkeypatch):
    falso = ChaveiroEmMemoria()
    monkeypatch.setattr(keyring.core, "_keyring_backend", falso)
    return falso


@pytest.fixture(autouse=True)
def sem_navegador_nem_rede_real(monkeypatch):
    """Nenhum teste abre navegador de verdade nem chama um Moodle real.

    Sem MOODLE_URL, o perfil `ufmg` é o padrão (ADR-0017): um teste distraído iria ao login da UFMG.
    Testes que precisam do navegador ou da rede trocam estes pontos por simulações.
    """
    from moodle_mcp import login, navegador, nucleo

    def proibido(*_args, **_kwargs):
        pytest.fail("teste tentou abrir um navegador ou chamar um Moodle de verdade")

    monkeypatch.setattr(navegador, "_async_playwright", proibido)
    monkeypatch.setattr(navegador, "_instalar_chromium", proibido)
    monkeypatch.setattr(nucleo, "_transporte", httpx.MockTransport(proibido))
    monkeypatch.setattr(login, "transporte", httpx.MockTransport(proibido))


@pytest.fixture(autouse=True)
def sem_estado_local_real(monkeypatch, tmp_path):
    """Nenhum teste lê nem escreve no diretório de dados do usuário (estado do cronograma)."""
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "dados"))
