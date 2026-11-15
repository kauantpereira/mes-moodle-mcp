---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0008: Tools orientadas à tarefa

## Contexto e problema
Medição na demo: ~123 mil caracteres para descobrir 'o que mudou' lendo o conteúdo de 12 disciplinas; 555 com `core_course_get_updates_since` no maior curso.

## Decisão
Preferir tools que respondem a uma pergunta do aluno (ex.: `novidades_desde`) às que espelham a API, com filtros e cortes padrão.

## Opções consideradas
- **Escolhida:** a decisão acima
- Tools espelhando a API

## Consequências
- Bom: Economia de contexto de duas ordens de grandeza.
- Ruim / a acompanhar: Mais lógica no servidor; precisa de testes.

## Fontes
- [Anthropic — Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic — Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Moodle — Web service API functions](https://docs.moodle.org/dev/Web_service_API_functions) (`core_course_get_updates_since`) e medições na demo (15/11/2026)
