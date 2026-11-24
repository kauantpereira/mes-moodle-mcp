"""Token do Moodle no chaveiro do sistema (ADR-0002, ADR-0016).

Keychain no macOS, Cofre de Credenciais no Windows, Secret Service no Linux, via `keyring`.
A chave é a URL base do Moodle: um token por Moodle, nunca em arquivo.

Sem chaveiro disponível (ex.: Linux sem Secret Service), as funções não levantam erro:
`ler` devolve None e `salvar` devolve False; o núcleo então mantém o token só na memória
do processo e avisa o aluno. Nenhuma mensagem de log inclui o token.
"""

import logging

import keyring
from keyring.errors import KeyringError, PasswordDeleteError

SERVICO = "moodle-mcp"
_log = logging.getLogger(__name__)


def ler(base_url: str) -> str | None:
    try:
        return keyring.get_password(SERVICO, base_url)
    except KeyringError:
        _log.warning("chaveiro do sistema indisponível para leitura")
        return None


def salvar(base_url: str, token: str) -> bool:
    try:
        keyring.set_password(SERVICO, base_url, token)
        return True
    except KeyringError:
        _log.warning("chaveiro do sistema indisponível; o token fica só na memória deste processo")
        return False


def apagar(base_url: str) -> bool:
    try:
        keyring.delete_password(SERVICO, base_url)
        return True
    except (PasswordDeleteError, KeyringError):
        return False
