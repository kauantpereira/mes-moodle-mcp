"""Estado local e comparação do cronograma: só ids e datas, em arquivo temporário."""

import json
import os
import stat

import pytest

from moodle_mcp import cronograma

URL = "https://moodle.exemplo.edu/20262"
AGORA = 1_800_000_000


def test_sem_arquivo_nao_ha_leitura():
    assert cronograma.ler(URL, 1) is None


def test_salva_e_le_a_ultima_leitura():
    assert cronograma.salvar(URL, 1, AGORA, {10: AGORA + 100, 11: AGORA + 200})

    assert cronograma.ler(URL, 1) == (AGORA, {10: AGORA + 100, 11: AGORA + 200})


def test_so_guarda_ids_e_datas():
    cronograma.salvar(URL, 1, AGORA, {10: AGORA + 100})
    conteudo = json.loads(cronograma.arquivo().read_text(encoding="utf-8"))

    assert conteudo == {"versao": 1, "leituras": {f"{URL}|1": {"lida_em": AGORA, "prazos": {"10": AGORA + 100}}}}


def test_alunos_e_moodles_diferentes_nao_se_misturam():
    cronograma.salvar(URL, 1, AGORA, {10: 1})
    cronograma.salvar(URL, 2, AGORA, {20: 2})
    cronograma.salvar("https://moodle.exemplo.edu/20261", 1, AGORA, {30: 3})

    assert cronograma.ler(URL, 1)[1] == {10: 1}
    assert cronograma.ler(URL, 2)[1] == {20: 2}
    assert cronograma.ler("https://moodle.exemplo.edu/20261", 1)[1] == {30: 3}


def test_arquivo_so_o_dono_le():
    cronograma.salvar(URL, 1, AGORA, {10: 1})

    assert stat.S_IMODE(os.stat(cronograma.arquivo()).st_mode) == 0o600


@pytest.mark.parametrize(
    "conteudo",
    ["não é json", "[]", "{}", '{"versao": 99, "leituras": {}}', '{"versao": 1, "leituras": []}', '{"versao": 1, "leituras": {"%s|1": {"lida_em": "x"}}}' % URL],
)
def test_arquivo_corrompido_ou_de_outra_versao_vale_como_sem_leitura(conteudo):
    cronograma.arquivo().parent.mkdir(parents=True)
    cronograma.arquivo().write_text(conteudo, encoding="utf-8")

    assert cronograma.ler(URL, 1) is None
    assert cronograma.salvar(URL, 1, AGORA, {10: 1})  # e é recriado sem erro
    assert cronograma.ler(URL, 1) == (AGORA, {10: 1})


def test_falha_de_escrita_nao_levanta_erro(monkeypatch, tmp_path):
    arquivo_no_lugar_do_diretorio = tmp_path / "bloqueado"
    arquivo_no_lugar_do_diretorio.write_text("x")
    monkeypatch.setenv("XDG_DATA_HOME", str(arquivo_no_lugar_do_diretorio))

    assert cronograma.salvar(URL, 1, AGORA, {10: 1}) is False


def test_escrita_nao_deixa_arquivo_temporario():
    cronograma.salvar(URL, 1, AGORA, {10: 1})
    cronograma.salvar(URL, 1, AGORA + 1, {10: 2})

    assert [p.name for p in cronograma.arquivo().parent.iterdir()] == ["cronograma.json"]


def test_compara_adiado_adiantado_novo_e_removido():
    antes = {1: 100, 2: 200, 3: 300, 4: 400}
    depois = {1: 150, 2: 150, 3: 300, 5: 500}

    assert sorted(cronograma.comparar(antes, depois)) == [
        (1, "adiado", 100, 150),
        (2, "adiantado", 200, 150),
        (4, "removido", 400, None),
        (5, "novo", None, 500),
    ]


def test_sem_diferenca_nao_ha_mudanca():
    assert cronograma.comparar({1: 100}, {1: 100}) == []
