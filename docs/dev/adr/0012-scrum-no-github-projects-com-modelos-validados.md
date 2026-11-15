---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0012: Scrum no GitHub Projects com modelos validados

## Contexto e problema
O grupo já usou Scrum no GitHub Projects no TP de Engenharia de Software. Queremos o mesmo modelo, mas a partir das fontes originais, sem reinventar processo.

## Decisão
Scrum (Scrum Guide 2020) com recursos nativos do GitHub: campo Iteration para as sprints, sub-issues para as tarefas, automações nativas. Histórias em Connextra com INVEST, critérios de aceite em Gherkin, story points em Fibonacci, Conventional Commits. Duas sprints de 5 dias até a apresentação (25/11/2026). Detalhes em `docs/dev/board.md`.

## Opções consideradas
- **Escolhida:** a decisão acima
- Copiar o board do TP de ES (traria nomes e views ad hoc)
- Kanban simples (sem cadência para um prazo fixo)

## Consequências
- Bom: formato conhecido pelo grupo e documentado por fontes externas.
- Views padrão criadas por API (Histórias, Sprint atual, Tabela por responsável).
- Ruim / a acompanhar: as automações nativas do GitHub Projects só se ligam pela interface (sem API); ver `pesquisa.md`.

## Fontes
- [Scrum Guide 2020](https://scrumguides.org/scrum-guide.html)
- Connextra (2001) e INVEST (Bill Wake, 2003)
- [Gherkin](https://cucumber.io/docs/gherkin/reference/)
- [GitHub — sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues), [iteration fields](https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-iteration-fields), [automações](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations), [issue forms](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms)
- [Conventional Commits](https://www.conventionalcommits.org/)
- Board do TP de Engenharia de Software do grupo (modelo de referência)
