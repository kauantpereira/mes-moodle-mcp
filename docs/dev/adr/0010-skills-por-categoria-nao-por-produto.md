---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0010: Skills por categoria, não por produto

## Contexto e problema
Nem todo aluno usa Google Agenda; padrão dos plugins oficiais da Anthropic (`~~categoria` + CONNECTORS.md).

## Decisão
Skills escritas para `~~calendário` e `~~tarefas`; destino escolhido na instalação (`userConfig`); saídas universais (.ics, Markdown, chat).

## Opções consideradas
- **Escolhida:** a decisão acima
- Skills específicas do Google Agenda

## Consequências
- Bom: Serve a quem usa Outlook, Notion, Todoist, Obsidian ou nada.
- Ruim / a acompanhar: Cada destino novo precisa de teste.
