---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0015: Fluxo de sugestões com triagem de conformidade

## Contexto e problema
As histórias serão construídas com o grupo. Cada sugestão precisa ser checada rapidamente contra as decisões de conformidade (ADRs 0001–0006) e, se não couber agora, não deve se perder: uma resposta positiva da DTI pode abrandar alguma decisão.

## Decisão
- Sugestões entram como issue pelo formulário "Sugestão de história" (label `sugestão`).
- Triagem feita por uma pessoa do grupo com o seu agente de código local, seguindo o roteiro do `AGENTS.md`; decisão: `aprovada`, `adaptar` ou `adiada`.
- Adiadas: fechadas como "not planned", com o ADR citado e no milestone "Revisitar após a DTI".
- Tarefas compartilhadas: um pai só (sub-issue) e as demais histórias usam dependência "bloqueada por".

## Opções consideradas
- **Escolhida:** a decisão acima
- Guardar as adiadas numa branch nunca mesclada (ideias fora do board, desatualizam, não são pesquisáveis como issues)
- Workflow no GitHub Actions com revisão automática (descartado: processo pesado demais para o grupo e com custo de API)
- GitHub Discussions (bom para debate aberto, mas sem templates com checklist nem integração direta com o board)
- Descartar as que não atendem (perde ideias que podem caber depois)

## Consequências
- Bom: nenhuma ideia se perde; a triagem é rápida e rastreável até o ADR.
- Ruim / a acompanhar: a qualidade da triagem depende de cada pessoa rodar o roteiro do AGENTS.md.

## Fontes
- Ver as fontes de [../sugestoes.md](../sugestoes.md#fontes).

> Revisada em 15/11/2026, antes do primeiro uso: a revisão por workflow foi trocada pelo roteiro no AGENTS.md.
