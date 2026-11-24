"""Janela de manutenção do Moodle (ADR-0005; ADR-0009).

O perfil da instituição diz em que horários o Moodle não deve ser chamado (ex.: backup
diário). Dentro da janela, a chamada é recusada antes da rede, com o horário em que
vale tentar de novo. O núcleo só aplica a regra; os horários vêm de `perfil_para()`.

Respostas já em cache (cache curto) continuam sendo servidas durante a janela: não
chegam ao Moodle, então não pesam na manutenção.
"""

import logging
from collections.abc import Callable
from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .perfis import Perfil

_log = logging.getLogger(__name__)


class EmManutencao(Exception):
    """Chamada recusada por cair na janela de manutenção do perfil."""

    def __init__(self, inicio: time, fim: time, fuso: str):
        super().__init__(f"Moodle em manutenção das {inicio:%H:%M} às {fim:%H:%M} ({fuso})")
        self.inicio = inicio
        self.fim = fim
        self.fuso = fuso


def _dentro(agora: time, inicio: time, fim: time) -> bool:
    if inicio < fim:
        return inicio <= agora < fim
    if inicio > fim:  # cruza a meia-noite
        return agora >= inicio or agora < fim
    return False  # início == fim: janela vazia


def _fuso(nome: str) -> ZoneInfo:
    try:
        return ZoneInfo(nome)
    except (ZoneInfoNotFoundError, ValueError):
        _log.warning("fuso %r indisponível; usando UTC para a janela de manutenção", nome)
        return ZoneInfo("UTC")


class Manutencao:
    def __init__(self, perfil: Perfil, agora: Callable[[], datetime] = lambda: datetime.now(UTC)):
        self._janelas = perfil.janelas_manutencao
        self._nome_fuso = perfil.fuso
        self._fuso = _fuso(perfil.fuso) if self._janelas else None
        self._agora = agora

    def checar(self) -> None:
        """Levanta EmManutencao se o horário atual (no fuso do perfil) cair numa janela."""
        if not self._janelas:
            return
        hora = self._agora().astimezone(self._fuso).time().replace(tzinfo=None)
        for inicio, fim in self._janelas:
            if _dentro(hora, inicio, fim):
                raise EmManutencao(inicio, fim, self._nome_fuso)
