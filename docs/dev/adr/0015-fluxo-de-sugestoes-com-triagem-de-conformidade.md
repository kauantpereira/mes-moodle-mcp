---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0015: Coleta de histórias com triagem de conformidade

## Contexto e problema
As histórias serão construídas com o grupo. Cada sugestão precisa ser checada rapidamente contra as decisões de conformidade (ADRs 0001–0006) e, se não couber agora, não deve se perder: uma resposta positiva da DTI pode abrandar alguma decisão.

## Decisão
- Sugestões entram como comentários numa issue fixada, "Coleta de histórias".
- São processadas em lote, manualmente (com apoio do agente de cada um, se quiserem), contra os ADRs de conformidade: aprovada → `user story`; adaptar → resposta com versão que atende; adiada → issue fechada como "not planned", ADR citado, milestone "Revisitar após a DTI".
- Tarefas compartilhadas: um pai só (sub-issue); as demais histórias usam dependência "bloqueada por".
- A rotina de processamento (quando e quem) será combinada depois.

## Opções consideradas
- **Escolhida:** a decisão acima
- Guardar as adiadas numa branch nunca mesclada (ideias fora do board, desatualizam, não são pesquisáveis como issues)
- Workflow no GitHub Actions com revisão automática (descartado: processo pesado demais para o grupo e com custo de API)
- Uma issue por sugestão, com formulário (descartado: mais cerimônia do que o grupo precisa)
- GitHub Discussions (bom para debate aberto, mas sem templates com checklist nem integração direta com o board)
- Descartar as que não atendem (perde ideias que podem caber depois)

## Consequências
- Bom: nenhuma ideia se perde; a triagem é rápida e rastreável até o ADR.
- Ruim / a acompanhar: sem rotina definida, a coleta pode acumular; combinar a rotina antes da Sprint 2.

## Fontes
- Ver as fontes de [../sugestoes.md](../sugestoes.md#fontes).

> Revisada em 15/11/2026, antes do primeiro uso: de formulário + workflow para uma issue de coleta processada manualmente.
