---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0001: Pedir autorização à instituição antes de divulgar

## Contexto e problema
Termo de Uso da UFMG, item 3.9: robôs que autenticam e extraem dados exigem autorização expressa da DTI.

## Decisão
Pedir autorização à DTI antes de qualquer divulgação. Se ela negar, ou não responder até 25/11/2026, o projeto não é publicado e a demo usa um Moodle local.

## Opções consideradas
- **Escolhida:** a decisão acima
- Publicar sem pedir
- Pedir e só então decidir

## Consequências
- Bom: Coerência com a análise de conformidade; a negativa vira resultado na apresentação.
- Ruim / a acompanhar: O repositório fica privado até a resposta.
