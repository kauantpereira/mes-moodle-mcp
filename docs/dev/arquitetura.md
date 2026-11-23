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
- `client.py`: cliente da API REST. Recebe só URL + token. Só chama funções explicitamente listadas em `FUNCOES_PERMITIDAS`; funções fora da lista são barradas antes da rede. O token vai no corpo do POST. Downloads usam GET separado, limitado ao host do Moodle, com token apenas na requisição. Mensagens brutas, corpos inválidos e detalhes de transporte são descartados.
- `nucleo.py`: ponto usado pelas tools. `cliente()` reutiliza um cliente por processo. `MOODLE_TOKEN` é um provedor provisório para desenvolvimento e será substituído pelo login e chaveiro previstos no ADR-0002. `chamar()` expõe mensagens genéricas sem conteúdo bruto do Moodle, URL ou detalhes de exceção. O transporte HTTP é encerrado por `aclose()` no cliente.

Decisões: ver [adr/](adr/).
