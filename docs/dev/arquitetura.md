# Arquitetura

```
agente (Claude Code / Codex / Gemini CLI)
  ├── skills/ (SKILL.md)            como usar: rotinas e regras
  └── MCP local (stdio) ── src/moodle_mcp/
        ├── núcleo: cliente da API REST do Moodle, tools, avisos, limite de chamadas
        └── perfis/<instituicao>.py  URL, login e regras específicas (isolado; ADR-0009)
              └── API de web services do Moodle (só funções get)
```

Decisões: ver [adr/](adr/).
