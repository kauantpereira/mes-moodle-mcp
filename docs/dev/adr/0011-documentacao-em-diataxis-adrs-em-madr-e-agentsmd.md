---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0011: Documentação em Diátaxis, ADRs em MADR e AGENTS.md

## Contexto e problema
Precisamos separar a documentação do usuário da do desenvolvedor e preparar o repositório para agentes.

## Decisão
Documentação do usuário em `docs/` seguindo Diátaxis; documentação de desenvolvimento em `docs/dev/` com ADRs no formato MADR (mínimo); instruções para agentes em `AGENTS.md` (padrão aberto), importado por `.claude/CLAUDE.md` e configurado no Gemini CLI.

## Opções consideradas
- **Escolhida:** a decisão acima
- Um único README longo
- CLAUDE.md na raiz (o validador de plugin avisa; não é carregado como contexto do plugin)

## Consequências
- Bom: Padrões amplamente adotados; um só arquivo de instruções serve aos três agentes.
- Ruim / a acompanhar: Manter a separação exige disciplina na revisão.
