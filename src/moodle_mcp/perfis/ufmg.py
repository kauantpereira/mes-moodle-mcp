"""Perfil da UFMG (ADR-0009): reverter este arquivo deixa o Moodle da UFMG no perfil genérico.

- Hosts: Moodle da UFMG (`virtual.ufmg.br`). O semestre fica no caminho da URL configurada
  pelo aluno (`moodle_url`), nunca aqui.
- Login: SSO (minhaUFMG) pelo fluxo do app, com o navegador (ADR-0002, ADR-0016).
- Fuso de Brasília e a janela diária de backup do Moodle (01h30–06h00), em que o servidor
  não deve chamar o Moodle (ADR-0005; Políticas de Uso do Moodle da DTI/UFMG).
"""

from datetime import time

from ..navegador import login_pelo_navegador
from . import Perfil

PERFIL = Perfil(
    nome="ufmg",
    hosts=frozenset({"virtual.ufmg.br"}),
    fuso="America/Sao_Paulo",
    janelas_manutencao=((time(1, 30), time(6, 0)),),
    login=login_pelo_navegador,
)
