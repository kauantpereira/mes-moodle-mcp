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


def test_entrar_generico_indica_o_terminal(monkeypatch):
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


def test_cli_entrar_manual(monkeypatch, capsys, chaveiro_falso):
    """`--manual`: não usa o login do perfil; o link é lido sem eco e só o token vai ao chaveiro."""
    import base64
    import hashlib

    from moodle_mcp import login

    async def perfil_nao_usado(base_url, interacao):
        raise AssertionError("--manual não deve abrir o login do perfil")

    monkeypatch.setattr(nucleo, "perfil_para", lambda url: GENERICO.__class__(nome="x", login=perfil_nao_usado))
    monkeypatch.setattr(login, "novo_passport", lambda: "passport-ficticio")
    assinatura = hashlib.md5((BASE + "passport-ficticio").encode()).hexdigest()
    link = "moodlemobile://token=" + base64.b64encode(f"{assinatura}:::{TOKEN}".encode()).decode()
    monkeypatch.setattr("builtins.input", lambda prompt="": pytest.fail("o link não pode ser lido com eco"))
    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt="": link)
    monkeypatch.delenv("MOODLE_URL")
    assert cli.main(["entrar", "--url", BASE, "--manual"]) == 0
    saida = capsys.readouterr()
    assert TOKEN not in saida.out + saida.err and link not in saida.out + saida.err
    assert chaveiro_falso.dados == {("moodle-mcp", BASE): TOKEN}


@pytest.mark.parametrize("modo", ["legacy", "auto"])
def test_cliente_mcp_nunca_recebe_formulario(monkeypatch, modo):
    """Cliente MCP real em memória, com e sem pedidos no meio da tool: o servidor nunca pede
    senha nem link (elicitation); responde com o comando de terminal."""
    from mcp.client.client import Client

    pedidos = []

    async def formulario(ctx, params):
        pedidos.append(params)
        raise AssertionError("o servidor não deve pedir formulário")

    monkeypatch.setattr(nucleo, "perfil_para", lambda url: GENERICO)

    async def rodar():
        async with Client(mcp, elicitation_callback=formulario, mode=modo) as c:
            return await c.call_tool("entrar", {})

    resultado = asyncio.run(rodar())
    assert resultado.is_error and "moodle-mcp entrar" in str(resultado)
    assert pedidos == []
