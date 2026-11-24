"""Comandos de terminal: `moodle-mcp entrar` (login fora do cliente MCP) e `moodle-mcp sair`.

Único lugar em que o aluno digita algo no login (senha ou link do login manual): o servidor MCP
nunca pede esses dados pelo chat (ADR-0016). Usa os mesmos métodos de login do servidor (perfil ou
genérico) e guarda o token no mesmo chaveiro; senha e link são lidos sem eco.
"""

import argparse
import asyncio
import getpass
import os
import sys
from typing import Literal

from mcp.server.mcpserver.exceptions import ToolError

from . import chaveiro, nucleo


class InteracaoTerminal:
    pode_perguntar = True

    async def avisar(self, mensagem: str) -> None:
        print(mensagem, file=sys.stderr)

    async def escolher_metodo(self, mensagem: str) -> Literal["senha", "app"] | None:
        print(mensagem, file=sys.stderr)
        resposta = (await asyncio.to_thread(input, "Forma de login [senha/app]: ")).strip().lower()
        return resposta if resposta in ("senha", "app") else None  # type: ignore[return-value]

    async def pedir_credenciais(self, mensagem: str) -> tuple[str, str] | None:
        print(mensagem, file=sys.stderr)
        usuario = (await asyncio.to_thread(input, "Usuário: ")).strip()
        senha = await asyncio.to_thread(getpass.getpass, "Senha: ")
        return (usuario, senha) if usuario and senha else None

    async def pedir_link(self, mensagem: str) -> str | None:
        print(mensagem, file=sys.stderr)
        return (await asyncio.to_thread(getpass.getpass, "Link (não aparece na tela): ")).strip() or None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="moodle-mcp", description="Login do Moodle MCP pelo terminal.")
    parser.add_argument("comando", choices=["entrar", "sair"])
    parser.add_argument("--url", help="endereço do Moodle (padrão: variável MOODLE_URL ou o Moodle da instituição)")
    parser.add_argument("--semestre", help="semestre, em instituições com um Moodle por semestre (padrão: o atual)")
    parser.add_argument(
        "--manual", action="store_true",
        help="login manual: abre o link do fluxo do app no seu navegador e cola o moodlemobile://token=... aqui",
    )
    args = parser.parse_args(argv)
    if args.url:
        os.environ["MOODLE_URL"] = args.url
    try:
        url = nucleo.url_do_moodle(args.semestre)
        if args.comando == "sair":
            print("Token apagado do chaveiro." if chaveiro.apagar(url) else "Nenhum token guardado para este Moodle.")
            return 0
        print(f"Moodle: {url}", file=sys.stderr)
        resultado = asyncio.run(nucleo.entrar(InteracaoTerminal(), manual=args.manual, semestre=args.semestre))
    except ToolError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nLogin cancelado.", file=sys.stderr)
        return 1
    if not resultado["token_no_chaveiro"]:
        print("Login feito, mas o chaveiro do sistema está indisponível: o token não foi guardado.", file=sys.stderr)
        return 1
    print("Login feito. Token guardado no chaveiro do sistema; o servidor MCP passa a usá-lo.")
    return 0
