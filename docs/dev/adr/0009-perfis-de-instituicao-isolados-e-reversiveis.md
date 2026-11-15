---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0009: Perfis de instituição isolados e reversíveis

## Contexto e problema
O acesso à UFMG pode ser negado (ADR-0001).

## Decisão
O que é específico de uma instituição fica em `src/moodle_mcp/perfis/`, num PR próprio; o núcleo recebe só URL + token. Moodle local e dados mockados só se houver negativa.

## Opções consideradas
- **Escolhida:** a decisão acima
- Código da UFMG espalhado pelo núcleo

## Consequências
- Bom: Reverter o acesso à UFMG sem perder a demo.
- Ruim / a acompanhar: Um nível a mais de indireção.

## Fontes
- Feedback do professor (cuidado com os termos de uso)
- [Termo de Compromisso de Uso dos Recursos de TI da UFMG](https://sistemas.ufmg.br/termos-de-uso) (versão de 20/10/2025)
