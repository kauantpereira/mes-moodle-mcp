# Moodle MCP

Servidor MCP **somente leitura** para o Moodle do próprio aluno, distribuído como plugin com skills de rotina, para agentes locais: **Claude Code/Desktop, OpenAI Codex e Gemini CLI**.

TP3 de Manutenção e Evolução de Software (DCC071, UFMG), grupo G15.

> **Repositório privado.** Não publicar nem divulgar sem autorização da instituição que hospeda o Moodle (no caso da UFMG, a DTI; ver docs/decisoes.md, D1).

## Princípios
- **Só leitura:** só funções `get` da API de web services do Moodle; nada é enviado, publicado ou alterado.
- **Só dados do próprio aluno:** nenhuma tool expõe participantes, posts de colegas ou notas de terceiros.
- **Credenciais locais:** cada aluno usa o próprio token, guardado no chaveiro do sistema; o servidor roda na máquina dele (stdio) e nunca vê a senha.
- **Respeito à infraestrutura:** contador e limite de chamadas; cache curto; evitar janelas de manutenção.
- **Regras de IA:** instrução ao agente + aviso em atividades avaliativas.
- **Economia de contexto:** tools orientadas à tarefa (ex.: o que mudou desde X), com filtros e cortes padrão.
- **Perfis por instituição:** o que é específico de uma instituição fica em `src/moodle_mcp/perfis/`, isolado do núcleo.

## Estrutura
```
src/moodle_mcp/            servidor MCP (núcleo + perfis/)
skills/                    SKILL.md (padrão aberto Agent Skills), compartilhados pelas 3 plataformas
CONNECTORS.md              categorias ~~calendário / ~~tarefas e conectores
.mcp.json                  MCP para o Claude Code
.claude-plugin/            manifesto + marketplace do Claude
.codex-plugin/ + .codex-mcp.json   manifesto do Codex
gemini-extension.json      manifesto do Gemini CLI
tests/  evals/  docs/
```

## Instalação (membros do grupo)
| Plataforma | Comando |
|---|---|
| Claude Code | `/plugin marketplace add kauantpereira/mes-moodle-mcp` e depois `/plugin install moodle-mcp@mes-moodle-mcp` |
| OpenAI Codex | `codex plugin marketplace add kauantpereira/mes-moodle-mcp` (a validar) |
| Gemini CLI | `gemini extensions install https://github.com/kauantpereira/mes-moodle-mcp` (a validar) |

## Desenvolvimento
```bash
uv sync
uv run pytest
claude plugin validate .
```

Regras de contribuição em CONTRIBUTING.md; decisões em docs/decisoes.md.
