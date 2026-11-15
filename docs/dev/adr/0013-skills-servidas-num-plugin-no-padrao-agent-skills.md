---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0013: Skills servidas num plugin, no padrão Agent Skills

## Contexto e problema
O MCP dá acesso aos dados; as rotinas (novidades do dia, organizar a semana, regras de IA) dizem ao agente como usá-lo. Precisamos de um formato que funcione nos três agentes locais (ADR-0007).

## Decisão
- As skills ficam em `skills/<nome>/SKILL.md`, no padrão aberto **Agent Skills** (o mesmo arquivo funciona no Claude Code, Codex e Gemini CLI).
- O **plugin** é o pacote que junta skills + configuração do MCP. Uma skill sozinha não é plugin; a Anthropic nem aceita skill avulsa no diretório.
- Cada plataforma tem o seu manifesto e a sua forma de instalar; não há marketplace comum:
  - Claude Code: `.claude-plugin/plugin.json` + `marketplace.json`, instalado com `/plugin marketplace add` (o próprio repo é o marketplace, que pode ser privado);
  - Codex: `.codex-plugin/plugin.json` (+ `.codex-mcp.json`), via marketplace do Codex;
  - Gemini CLI: `gemini-extension.json`, via `gemini extensions install <url>` (descobre `skills/` sozinho).
- Sempre que existir, partir de uma skill oficial (Anthropic, Google, OpenAI) ou open source confiável e adaptar.

## Opções consideradas
- **Escolhida:** a decisão acima
- Só o MCP, sem skills (o agente teria de reinventar as rotinas a cada conversa)
- Skills específicas de uma plataforma

## Consequências
- Bom: um conteúdo, três plataformas; as skills só carregam quando usadas (economia de contexto).
- Ruim / a acompanhar: três manifestos para manter; a instalação no Codex e no Gemini CLI ainda precisa ser validada.

## Fontes
- [Especificação Agent Skills](https://github.com/agentskills/agentskills)
- [Claude Code — criar plugin](https://code.claude.com/docs/en/plugins/create) e [manifesto](https://code.claude.com/docs/en/plugins-reference)
- [Claude — o que incluir no plugin (skills vão dentro de plugins)](https://claude.com/docs/connectors/building/what-to-build)
- [OpenAI Codex — skills](https://developers.openai.com/codex/skills) e [empacotar plugin](https://developers.openai.com/plugins/build/plugins.md)
- [Gemini CLI — skills](https://geminicli.com/docs/cli/skills/) e [extensões](https://google-gemini.github.io/gemini-cli/docs/extensions/)
- [cooklang/cooklang-skills](https://github.com/cooklang/cooklang-skills) (exemplo real)
