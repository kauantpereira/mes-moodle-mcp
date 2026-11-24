"""Moodle MCP: servidor MCP somente leitura para o Moodle do aluno."""

import sys

from .server import mcp


def main() -> None:
    if len(sys.argv) > 1:  # `moodle-mcp entrar` / `moodle-mcp sair`
        from .cli import main as cli

        raise SystemExit(cli(sys.argv[1:]))
    mcp.run()
