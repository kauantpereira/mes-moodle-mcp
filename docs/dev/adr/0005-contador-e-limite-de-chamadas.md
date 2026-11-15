---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0005: Contador e limite de chamadas

## Contexto e problema
Item 3.9 (não esgotar recursos) e Políticas de Uso do Moodle (backup diário 01h30–06h00).

## Decisão
Contar e limitar chamadas por usuário; cache curto para dados que mudam pouco; evitar a janela de manutenção.

## Opções consideradas
- **Escolhida:** a decisão acima
- Sem limite (como os MCPs open source analisados)

## Consequências
- Bom: Respeito à infraestrutura e argumento no pedido de autorização.
- Ruim / a acompanhar: Respostas podem vir do cache por alguns minutos.

## Fontes
- [Termo de Compromisso de Uso dos Recursos de TI da UFMG](https://sistemas.ufmg.br/termos-de-uso) (versão de 20/10/2025), item 3.9
- [Moodle — Políticas de Uso (DTI/UFMG)](https://www.ufmg.br/dti/moodle-politicas-de-uso/)
- [MCP spec 2026-07-28 (RC): `ttlMs`/`cacheScope`](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)
