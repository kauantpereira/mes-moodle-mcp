"""Cache curto para dados do Moodle que mudam pouco (ADR-0005).

Guarda em memória, por alguns minutos, as respostas de funções cujo conteúdo muda
raramente ao longo de uma sessão (lista de disciplinas e conteúdo de uma disciplina).
Uma resposta servida daqui não sai para a rede e não conta no limite de chamadas.

- Chave = função + parâmetros já no formato enviado ao Moodle (ordem não importa).
- Só respostas de sucesso entram; erros nunca são guardados.
- Cada leitura devolve uma cópia, para que uma tool não altere o que está guardado.
- O cache vive no processo (um cliente = um token = um aluno), como o limitador.
"""

import copy
import time
from collections import OrderedDict
from collections.abc import Callable, Mapping
from typing import Any

# Função → validade em segundos. Escolha: 5 min. Uma rotina (ex.: novidades, plano da
# semana) pede a mesma lista de disciplinas e o mesmo conteúdo várias vezes em poucos
# minutos; 5 min corta essas repetições, e um material novo aparece no máximo 5 min depois.
# Prazos, entregas, notas e novidades (`core_course_get_updates_since`) ficam fora: mudam
# no meio da sessão e o aluno espera vê-los na hora.
TTL_PADRAO: Mapping[str, float] = {
    "core_enrol_get_users_courses": 300,
    "core_course_get_contents": 300,
}
# Teto de entradas, para o cache não crescer sem limite numa sessão longa.
MAX_ENTRADAS = 128

Chave = tuple[str, tuple[tuple[str, str], ...]]


def chave(wsfunction: str, params: Mapping[str, str]) -> Chave:
    return wsfunction, tuple(sorted(params.items()))


class CacheCurto:
    def __init__(
        self,
        ttl: Mapping[str, float] = TTL_PADRAO,
        relogio: Callable[[], float] = time.monotonic,
        max_entradas: int = MAX_ENTRADAS,
    ):
        if any(v <= 0 for v in ttl.values()) or max_entradas < 1:
            raise ValueError("validade e tamanho do cache precisam ser positivos")
        self._ttl = dict(ttl)
        self._relogio = relogio
        self._max = max_entradas
        self._itens: OrderedDict[Chave, tuple[float, Any]] = OrderedDict()

    def guarda(self, wsfunction: str) -> bool:
        return wsfunction in self._ttl

    def obter(self, k: Chave) -> tuple[bool, Any]:
        """(True, cópia da resposta) se houver entrada válida; (False, None) senão."""
        item = self._itens.get(k)
        if item is None:
            return False, None
        expira, valor = item
        if self._relogio() >= expira:
            del self._itens[k]
            return False, None
        return True, copy.deepcopy(valor)

    def salvar(self, k: Chave, valor: Any) -> None:
        if not self.guarda(k[0]):
            return
        self._itens.pop(k, None)
        self._itens[k] = (self._relogio() + self._ttl[k[0]], copy.deepcopy(valor))
        while len(self._itens) > self._max:
            self._itens.popitem(last=False)

    def limpar(self) -> None:
        self._itens.clear()

    def __len__(self) -> int:
        return len(self._itens)
