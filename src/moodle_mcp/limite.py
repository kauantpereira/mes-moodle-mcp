"""Contador e limite de chamadas ao Moodle (ADR-0005; Termo de uso da UFMG, item 3.9).

Cada cliente (um por processo, um token = um aluno) conta as chamadas em janelas
deslizantes. Ao atingir o limite de qualquer janela, a chamada é recusada antes de
sair para a rede, com o tempo até liberar.

Limitação conhecida: o contador vive no processo. Duas sessões abertas ao mesmo tempo
(ex.: Claude Code e Claude Desktop) contam separadamente.
"""

import math
import time
from collections import deque
from collections.abc import Callable

# (máximo de chamadas, janela em segundos). Uma tool típica faz de 1 a ~15 chamadas.
JANELAS_PADRAO: tuple[tuple[int, int], ...] = ((60, 60), (600, 3600))


class LimiteAtingido(Exception):
    """Chamada recusada pelo limite local, antes de chegar ao Moodle."""

    def __init__(self, maximo: int, janela_s: int, espera_s: int):
        super().__init__(f"limite de {maximo} chamadas em {janela_s} s atingido; tente em {espera_s} s")
        self.maximo = maximo
        self.janela_s = janela_s
        self.espera_s = espera_s


class Limitador:
    def __init__(
        self,
        janelas: tuple[tuple[int, int], ...] = JANELAS_PADRAO,
        relogio: Callable[[], float] = time.monotonic,
    ):
        if not janelas or any(m < 1 or j < 1 for m, j in janelas):
            raise ValueError("janelas precisam de máximo e duração positivos")
        self._janelas = tuple(sorted(janelas, key=lambda x: x[1]))
        self._relogio = relogio
        self._horarios: deque[float] = deque()
        self.total = 0

    def _esquecer_antigas(self, agora: float) -> None:
        maior = self._janelas[-1][1]
        while self._horarios and self._horarios[0] <= agora - maior:
            self._horarios.popleft()

    def registrar(self) -> None:
        """Conta uma chamada ou levanta LimiteAtingido (sem contar a recusada)."""
        agora = self._relogio()
        self._esquecer_antigas(agora)
        for maximo, janela in self._janelas:
            na_janela = [t for t in self._horarios if t > agora - janela]
            if len(na_janela) >= maximo:
                # Libera quando a chamada mais antiga que ainda conta sair da janela.
                libera = na_janela[-maximo] + janela
                raise LimiteAtingido(maximo, janela, max(1, math.ceil(libera - agora)))
        self._horarios.append(agora)
        self.total += 1

    def uso(self) -> dict[str, int]:
        """Chamadas feitas em cada janela e no total do processo."""
        agora = self._relogio()
        self._esquecer_antigas(agora)
        saida = {f"ultimos_{janela}s": sum(1 for t in self._horarios if t > agora - janela) for _, janela in self._janelas}
        saida["total"] = self.total
        return saida
