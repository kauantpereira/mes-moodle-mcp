import asyncio

import httpx
import pytest
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError

from moodle_mcp import cli, nucleo
from moodle_mcp.perfis import GENERICO
from moodle_mcp.server import ServidorMoodle, mcp

BASE = "https://moodle.exemplo.edu"
TOKEN = "token-ficticio-123"


@pytest.fixture(autouse=True)
def limpar(monkeypatch):
    monkeypatch.setenv("MOODLE_URL", BASE)
    monkeypatch.delenv("MOODLE_TOKEN", raising=False)
    monkeypatch.setattr(nucleo, "_transporte", httpx.MockTransport(lambda r: httpx.Response(200, json={"userid": 7})))
    nucleo._reiniciar()
    yield
    nucleo._reiniciar()


def test_servidor_carrega():
    assert mcp.name == "moodle"


def test_tool_entrar_registrada():
    tools = {t.name: t for t in asyncio.run(mcp.list_tools())}
    assert "entrar" in tools
    assert tools["entrar"].input_schema.get("properties", {}) == {}


def test_entrar_sem_formulario_indica_o_terminal(monkeypatch):
    monkeypatch.setattr(nucleo, "perfil_para", lambda url: GENERICO)
    with pytest.raises(ToolError, match="moodle-mcp entrar"):
        asyncio.run(mcp.call_tool("entrar", {}))


def test_entrar_responde_sem_token(monkeypatch):
    async def proprio(base_url, interacao):
        return TOKEN

    monkeypatch.setattr(nucleo, "perfil_para", lambda url: GENERICO.__class__(nome="x", login=proprio))
    resultado = asyncio.run(mcp.call_tool("entrar", {}))
    texto = str(resultado)
    assert TOKEN not in texto
    assert "moodle.exemplo.edu" in texto and "conectado" in texto


def test_servidor_expoe_o_contexto_da_tool_ao_nucleo():
    servidor = ServidorMoodle(name="teste")
    vistos = []

    @servidor.tool()
    async def espia() -> str:
        vistos.append(nucleo._contexto.get())
        return "ok"

    ctx = Context(mcp_server=servidor)  # o servidor real sempre passa o contexto da requisição
    asyncio.run(servidor.call_tool("espia", {}, ctx))
    assert vistos == [ctx]
    assert nucleo._contexto.get() is None


def test_cli_entrar_por_senha(monkeypatch, capsys, chaveiro_falso):
    from moodle_mcp import login

    monkeypatch.setattr(nucleo, "perfil_para", lambda url: GENERICO)
    monkeypatch.setattr(login, "transporte", httpx.MockTransport(lambda r: httpx.Response(200, json={"token": TOKEN})))
    respostas = iter(["senha", "aluno"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(respostas))
    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt="": "senha-ficticia-456")
    monkeypatch.delenv("MOODLE_URL")
    assert cli.main(["entrar", "--url", BASE]) == 0
    saida = capsys.readouterr()
    assert "chaveiro" in saida.out
    assert "senha-ficticia-456" not in saida.out + saida.err and TOKEN not in saida.out + saida.err
    assert chaveiro_falso.dados == {("moodle-mcp", BASE): TOKEN}
    assert cli.main(["sair", "--url", BASE]) == 0
    assert chaveiro_falso.dados == {}


def _cliente_mcp(modo, respostas):
    from mcp.client.client import Client
    from mcp_types import ElicitResult

    pedidos = []

    async def formulario(ctx, params):
        campos = set(params.requested_schema["properties"])
        pedidos.append(campos)
        return ElicitResult(action="accept", content=respostas[frozenset(campos)])

    return Client(mcp, elicitation_callback=formulario, mode=modo), pedidos


def test_entrar_por_formulario_de_ponta_a_ponta(monkeypatch, chaveiro_falso):
    """Cliente MCP real em memória (protocolo com pedidos no meio da tool): senha só no formulário."""
    from moodle_mcp import login

    monkeypatch.setattr(nucleo, "perfil_para", lambda url: GENERICO)
    monkeypatch.setattr(login, "transporte", httpx.MockTransport(lambda r: httpx.Response(200, json={"token": TOKEN})))
    cliente, pedidos = _cliente_mcp(
        "legacy",
        {frozenset({"metodo"}): {"metodo": "senha"}, frozenset({"usuario", "senha"}): {"usuario": "aluno", "senha": "senha-ficticia-456"}},
    )

    async def rodar():
        async with cliente as c:
            return await c.call_tool("entrar", {})

    resultado = asyncio.run(rodar())
    assert not resultado.is_error and resultado.structured_content["conectado"] is True
    assert pedidos == [{"metodo"}, {"usuario", "senha"}]
    assert "senha-ficticia-456" not in str(resultado) and TOKEN not in str(resultado)
    assert chaveiro_falso.dados == {("moodle-mcp", BASE): TOKEN}


def test_protocolo_sem_pedidos_no_meio_da_tool_indica_o_terminal(monkeypatch):
    monkeypatch.setattr(nucleo, "perfil_para", lambda url: GENERICO)
    cliente, pedidos = _cliente_mcp("auto", {})

    async def rodar():
        async with cliente as c:
            return await c.call_tool("entrar", {})

    resultado = asyncio.run(rodar())
    assert resultado.is_error and "moodle-mcp entrar" in str(resultado)
    assert pedidos == []
