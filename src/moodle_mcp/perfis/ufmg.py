"""Perfil da UFMG (ADR-0009): reverter este arquivo deixa o Moodle da UFMG no perfil genérico.

- Hosts: Moodle da UFMG (`virtual.ufmg.br`).
- Um Moodle por semestre (ADR-0017): `virtual.ufmg.br/AAAAS` (ex.: `/20262`). Sem MOODLE_URL, este é
  o perfil padrão e vale o semestre atual, calculado pela data: janeiro a junho → 1º, julho a
  dezembro → 2º. O aluno pode pedir outro semestre como `2026.1`, `20261`, `anterior` ou `atual`.
- Login: SSO (minhaUFMG) com o navegador (ADR-0002, ADR-0016). A janela abre no Minhas Turmas, a
  página que o aluno já usa; depois do login, o servidor pega o token do app com a sessão.
- Fuso de Brasília e a janela diária de backup do Moodle (01h30–06h00), em que o servidor
  não deve chamar o Moodle (ADR-0005; Políticas de Uso do Moodle da DTI/UFMG).
"""

import re
from collections.abc import Callable
from datetime import date, time

from ..login import Interacao
from ..navegador import login_pelo_navegador
from . import Perfil

ENDERECO = "https://virtual.ufmg.br"
MINHAS_TURMAS = f"{ENDERECO}/minhasturmas/"
hoje: Callable[[], date] = date.today  # trocado nos testes


def semestre_atual(dia: date) -> str:
    return f"{dia.year}{1 if dia.month <= 6 else 2}"


def _anterior(codigo: str) -> str:
    ano, periodo = int(codigo[:4]), codigo[4]
    return f"{ano}1" if periodo == "2" else f"{ano - 1}2"


def url_do_semestre(semestre: str | None) -> str:
    texto = (semestre or "atual").strip().lower()
    atual = semestre_atual(hoje())
    if texto == "atual":
        codigo = atual
    elif texto == "anterior":
        codigo = _anterior(atual)
    else:
        achado = re.fullmatch(r"(\d{4})\s*[./-]?\s*([12])", texto)
        if achado is None:
            raise ValueError("use ano e semestre, como 2026.1 ou 20261, ou então 'anterior' ou 'atual'.")
        codigo = achado[1] + achado[2]
    return f"{ENDERECO}/{codigo}"


async def entrar(base_url: str, interacao: Interacao) -> str:
    return await login_pelo_navegador(base_url, interacao, pagina_inicial=MINHAS_TURMAS)


PERFIL = Perfil(
    nome="ufmg",
    hosts=frozenset({"virtual.ufmg.br"}),
    fuso="America/Sao_Paulo",
    janelas_manutencao=((time(1, 30), time(6, 0)),),
    login=entrar,
    url_do_semestre=url_do_semestre,
)
