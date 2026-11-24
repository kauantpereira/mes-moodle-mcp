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
- `limite.py`: contador e limite de chamadas (ADR-0005). Janelas deslizantes, padrão de 60 chamadas por minuto e 600 por hora; `call()` e `baixar()` registram antes da rede, e a recusa vira `ToolError` com o tempo de espera. O contador é por processo: sessões simultâneas contam separado.
- `cache.py`: cache curto em memória (ADR-0005). `core_enrol_get_users_courses` e `core_course_get_contents` valem 5 min; chave = função + parâmetros já achatados. `call()` consulta o cache antes do limitador: um acerto não sai para a rede nem conta no limite. Só respostas de sucesso entram; erros do Moodle e de HTTP não. Cada leitura devolve uma cópia; teto de 128 entradas (sai a mais antiga). Relógio injetável, como em `limite.py`. Também é por processo.
- `manutencao.py`: janela de manutenção (ADR-0005, ADR-0009). O cliente pega `perfil_para(base_url).janelas_manutencao` e, dentro de uma janela (horário no `perfil.fuso`; janela com início > fim cruza a meia-noite; início = fim é vazia), `call()` e `baixar()` levantam `EmManutencao` antes do limitador e da rede. `chamar()` traduz para `ToolError` com a janela e o horário para tentar de novo, sem token nem URL. Respostas já no cache curto continuam valendo durante a janela. O `GENERICO` não tem janela; os horários de cada instituição ficam no seu perfil. Fuso desconhecido cai em UTC (com aviso no log). Relógio injetável.

## Perfis (`perfis/`)
- `perfis/__init__.py`: contrato `Perfil` (hosts, fuso, janelas de manutenção, login próprio) e `perfil_para(base_url)`. Cada instituição é um módulo `perfis/<inst>.py` com `PERFIL = Perfil(...)`, descoberto sozinho; sem módulo (ou com o PR revertido), vale o `GENERICO`. O núcleo nunca importa um perfil pelo nome (ADR-0009).

Decisões: ver [adr/](adr/).
