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

## Fontes
- [Diátaxis](https://diataxis.fr/)
- [MADR](https://adr.github.io/madr/)
- [AGENTS.md](https://agents.md/) e [Agentic AI Foundation](https://openai.com/index/agentic-ai-foundation/)
- [AAIF — medindo o AGENTS.md](https://aaif.io/blog/measuring-agents-md-what-five-runs-show-that-one-doesn-t)
- [Structural Quality Gaps in Practitioner AI Governance Prompts (arXiv 2604.21090)](https://arxiv.org/pdf/2604.21090)
- Plugin Engineering da Anthropic: skills `architecture` (formato de ADR) e `documentation`
- [Claude Code — CLAUDE.md na raiz de plugin não é carregado](https://code.claude.com/docs/en/plugins-reference)
