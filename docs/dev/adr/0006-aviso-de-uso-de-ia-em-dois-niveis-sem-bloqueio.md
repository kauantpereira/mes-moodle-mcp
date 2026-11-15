---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0006: Aviso de uso de IA em dois níveis, sem bloqueio

## Contexto e problema
Guia de IA (p. 23): o aluno só usa IA se o plano de ensino permitir.

## Decisão
Nível 1: instrução do servidor ao agente. Nível 2: campo `aviso` nas respostas com atividades avaliativas.

## Opções consideradas
- **Escolhida:** a decisão acima
- Bloquear ou pedir confirmação (nível 3)

## Consequências
- Bom: O servidor não conhece a regra de cada disciplina; a decisão é do aluno.
- Ruim / a acompanhar: O aviso é mitigação, não garantia: o agente pode ignorá-lo (tema de evals).
