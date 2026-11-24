"""Nenhum teste toca o chaveiro real do sistema: backend do keyring em memória."""

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
