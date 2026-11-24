"""Perfis de conformidade por instituição (ADR-0009).

Cada instituição fica num módulo próprio (ex.: `perfis/ufmg.py`), isolado do núcleo,
que define uma constante `PERFIL = Perfil(...)`. Os módulos são descobertos sozinhos:
remover um arquivo de perfil (ou reverter o PR que o criou) não quebra o resto, e o
Moodle daquela instituição passa a usar o perfil `GENERICO`.

O núcleo nunca importa um perfil pelo nome; pergunta `perfil_para(base_url)`.
"""

import importlib
import logging
import pkgutil
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import time
from typing import Any
from urllib.parse import urlsplit

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Perfil:
    """O que muda de uma instituição para outra. Tudo tem padrão neutro."""

    nome: str
    # Hosts do Moodle da instituição (ex.: "virtual.ufmg.br"); é por eles que o perfil é escolhido.
    hosts: frozenset[str] = field(default_factory=frozenset)
    # Fuso IANA para exibir datas e interpretar horários do perfil.
    fuso: str = "UTC"
    # Janelas diárias em que o Moodle não deve ser chamado (ex.: backup), no horário de `fuso`.
    # Pares (início, fim); uma janela que cruza a meia-noite tem início > fim.
    janelas_manutencao: tuple[tuple[time, time], ...] = ()
    # Login específico da instituição (ex.: SSO pelo fluxo do app). None = login genérico do núcleo.
    # A assinatura é definida pela tarefa de login (#22/#23).
    login: Callable[..., Any] | None = None


GENERICO = Perfil(nome="generico")


def _carregar() -> tuple[Perfil, ...]:
    perfis: list[Perfil] = []
    for modulo in pkgutil.iter_modules(__path__):
        if modulo.name.startswith("_"):
            continue
        try:
            perfil = getattr(importlib.import_module(f"{__name__}.{modulo.name}"), "PERFIL", None)
        except Exception:  # um perfil quebrado não derruba o servidor
            _log.warning("perfil %s não carregou; usando o genérico", modulo.name, exc_info=True)
            continue
        if isinstance(perfil, Perfil):
            perfis.append(perfil)
    return tuple(perfis)


PERFIS: tuple[Perfil, ...] = _carregar()


def perfil_para(base_url: str, perfis: tuple[Perfil, ...] | None = None) -> Perfil:
    """Perfil cujo host bate com o do Moodle; `GENERICO` se nenhum bater."""
    host = (urlsplit(base_url).hostname or "").lower()
    for perfil in PERFIS if perfis is None else perfis:
        if host in perfil.hosts:
            return perfil
    return GENERICO
