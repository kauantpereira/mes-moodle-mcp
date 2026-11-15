---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0014: GitHub Flow, Conventional Commits e SemVer

## Contexto e problema
Quatro pessoas e agentes de IA vão mexer no repositório em duas sprints curtas. Precisamos de um padrão de interação simples e amplamente conhecido.

## Decisão
GitHub Flow (branch curta a partir de `main`, PR, revisão, merge); Conventional Commits nos commits e títulos de PR; squash and merge; SemVer com a versão sincronizada nos 4 manifestos; CHANGELOG no formato Keep a Changelog. Detalhes em `docs/dev/fluxo-git.md`.

## Opções consideradas
- **Escolhida:** a decisão acima
- Git Flow (branches `develop`/`release`: pesado para duas sprints)
- Sem convenção de commits

## Consequências
- Bom: histórico legível, changelog quase automático, mesmo padrão do TP de ES.
- Ruim / a acompanhar: proteção de branch em repositório privado depende do plano do GitHub; enquanto isso, a revisão obrigatória é combinada, não imposta.

## Fontes
- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)
- [Conventional Commits 1.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
