from moodle_mcp.server import mcp


def test_servidor_carrega():
    assert mcp.name == "moodle"
