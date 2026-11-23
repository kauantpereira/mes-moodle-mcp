# Arquitetura

```
agente (Claude Code / Codex / Gemini CLI)
  ├── skills/ (SKILL.md)            como usar: rotinas e regras
  └── MCP local (stdio) ── src/moodle_mcp/
        ├── núcleo: cliente da API REST do Moodle, tools, avisos, limite de chamadas
        └── perfis/<instituicao>.py  URL, login e regras específicas (isolado; ADR-0009)
              └── API de web services do Moodle (só funções get)
```

## Núcleo
- `client.py`: cliente da API REST. Recebe só URL + token. Só chama funções de `FUNCOES_PERMITIDAS` (regra 1): **toda função nova entra nessa lista no mesmo PR da tool que a usa**. Token só no corpo do POST, nunca em mensagens de erro; HTTPS obrigatório (HTTP só em `localhost`, para o Moodle local); downloads só do host do Moodle.
- `nucleo.py`: o que as tools usam. `cliente()` lê `MOODLE_URL` e o token (por enquanto `MOODLE_TOKEN`; o login troca `obter_token`), e `chamar()` traduz erros do Moodle para mensagens ao agente.

Decisões: ver [adr/](adr/).
