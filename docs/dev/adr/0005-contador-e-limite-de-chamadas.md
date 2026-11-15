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
