# Moodle MCP

Deixe seu assistente de IA (Claude, Codex ou Gemini CLI) acompanhar o seu Moodle por você: avisos dos professores, prazos e mudanças de cronograma, **só leitura e só com os seus dados**.

> **Repositório privado.** Não divulgar sem autorização da instituição que hospeda o Moodle (ver [ADR-0001](docs/dev/adr/0001-pedir-autorizacao-a-instituicao-antes-de-divulgar.md)).

## O que ele faz
- **Novidades da faculdade:** todo dia, resume o que mudou (avisos, materiais, prazos) e atualiza o seu calendário.
- **Organizar a semana:** "como organizo minha semana para entregar tudo e estudar para X e Y?"
- **Regras de IA:** lembra de conferir se a disciplina permite IA antes de ajudar numa atividade avaliativa.

## Comece em 5 minutos
1. Instale no seu agente (no Claude Code: `/plugin marketplace add kauantpereira/mes-moodle-mcp` e `/plugin install moodle-mcp@mes-moodle-mcp`): [Claude Code](docs/guias/instalar-no-claude.md) · [Codex](docs/guias/instalar-no-codex.md) · [Gemini CLI](docs/guias/instalar-no-gemini.md)
2. Siga o [tutorial de primeiros passos](docs/tutorial/primeiros-passos.md).

## Documentação
| Preciso… | Vá para |
|---|---|
| aprender a usar, do zero | [Tutorial](docs/tutorial/primeiros-passos.md) |
| resolver uma tarefa específica | [Guias](docs/guias/) |
| consultar tools, opções e conectores | [Referência](docs/referencia/) |
| entender privacidade e regras | [Explicação](docs/explicacao/) |

Quer contribuir? Veja [CONTRIBUTING.md](CONTRIBUTING.md) e a [documentação de desenvolvimento](docs/dev/).
