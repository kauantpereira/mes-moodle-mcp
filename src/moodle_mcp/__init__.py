"""Moodle MCP: servidor MCP somente leitura para o Moodle do aluno."""

from .server import mcp


def main() -> None:
    mcp.run()
