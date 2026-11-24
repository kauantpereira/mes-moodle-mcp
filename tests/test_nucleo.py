"""Acesso ao Moodle pelas tools: configuração e tradução de erros. Token fictício."""

import asyncio

import httpx
import pytest
from mcp.server.mcpserver.exceptions import ToolError

from moodle_mcp import nucleo
from moodle_mcp.client import MoodleClient

TOKEN = "token-ficticio-123"


@pytest.fixture(autouse=True)
def limpar(monkeypatch):
    monkeypatch.delenv("MOODLE_URL", raising=False)
    monkeypatch.delenv("MOODLE_TOKEN", raising=False)
    nucleo._reiniciar()
    yield
    nucleo._reiniciar()


def com_resposta(monkeypatch, handler):
    c = MoodleClient("https://moodle.exemplo.edu", TOKEN, transport=httpx.MockTransport(handler))
    monkeypatch.setattr(nucleo, "_cliente", c)


def test_sem_url_configurada():
    with pytest.raises(ToolError, match="MOODLE_URL"):
        nucleo.cliente()


def test_sem_token(monkeypatch):
    monkeypatch.setenv("MOODLE_URL", "https://moodle.exemplo.edu")
    with pytest.raises(ToolError, match="token"):
        nucleo.cliente()


def test_url_sem_https(monkeypatch):
    monkeypatch.setenv("MOODLE_URL", "http://moodle.exemplo.edu")
    monkeypatch.setenv("MOODLE_TOKEN", TOKEN)
    with pytest.raises(ToolError, match="HTTPS"):
        nucleo.cliente()


def test_cliente_unico_por_processo(monkeypatch):
    monkeypatch.setenv("MOODLE_URL", "https://moodle.exemplo.edu/")
    monkeypatch.setenv("MOODLE_TOKEN", TOKEN)
    assert nucleo.cliente() is nucleo.cliente()
    assert nucleo.cliente().base_url == "https://moodle.exemplo.edu"


def test_token_expirado_vira_dica_de_login(monkeypatch):
    com_resposta(
        monkeypatch,
        lambda r: httpx.Response(200, json={"errorcode": "invalidtoken", "message": "Token inválido"}),
    )
    with pytest.raises(ToolError, match="token expirou ou foi revogado") as exc:
        asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    mensagem = str(exc.value)
    assert "entrar" in mensagem
    assert "MOODLE_TOKEN" in mensagem
    assert TOKEN not in mensagem
    assert "https://moodle.exemplo.edu" not in mensagem
    assert "Token inválido" not in mensagem


def test_outro_errorcode_mantem_mensagem_generica(monkeypatch):
    com_resposta(
        monkeypatch,
        lambda r: httpx.Response(
            200,
            json={"errorcode": "accessexception", "message": "detalhe interno secreto"},
        ),
    )
    with pytest.raises(ToolError) as exc:
        asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    mensagem = str(exc.value)
    assert mensagem == "O Moodle recusou core_webservice_get_site_info."
    assert "entrar" not in mensagem
    assert "MOODLE_TOKEN" not in mensagem
    assert TOKEN not in mensagem
    assert "https://moodle.exemplo.edu" not in mensagem
    assert "detalhe interno secreto" not in mensagem


def test_funcao_de_escrita_vira_toolerror(monkeypatch):
    com_resposta(monkeypatch, lambda r: httpx.Response(200, json={}))
    with pytest.raises(ToolError, match="só leitura"):
        asyncio.run(nucleo.chamar("core_user_update_users"))


def test_falha_de_rede_sem_token(monkeypatch):
    def falha(r):
        raise httpx.ConnectError("sem rede")

    com_resposta(monkeypatch, falha)
    with pytest.raises(ToolError, match="Falha de conexão com o Moodle") as exc:
        asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    assert TOKEN not in str(exc.value)
    assert "sem rede" not in str(exc.value)


def test_erro_rest_nao_expoe_mensagem_bruta(monkeypatch):
    com_resposta(monkeypatch, lambda r: httpx.Response(200, json={"errorcode": "invalidtoken", "message": "token super secreto"}))
    with pytest.raises(ToolError) as exc:
        asyncio.run(nucleo.chamar("core_webservice_get_site_info"))
    assert "token super secreto" not in str(exc.value)
