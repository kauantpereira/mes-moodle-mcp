# Processo: Scrum no GitHub Projects

Não inventamos processo: seguimos modelos já validados e usamos os recursos nativos do GitHub.

| Peça | Modelo adotado | Fonte |
|---|---|---|
| Processo | **Scrum**: Product Backlog → Sprint Backlog → sprint → revisão → incremento pronto | [Scrum Guide 2020](https://scrumguides.org/scrum-guide.html) |
| Histórias | Formato **Connextra** ("Como …, quero …, para …") + critérios **INVEST** | Connextra (2001); Bill Wake, INVEST (2003) |
| Critérios de aceite | **Gherkin** (Dado / Quando / Então) | [Cucumber — Gherkin](https://cucumber.io/docs/gherkin/reference/) |
| Estimativa | **Story points** em Fibonacci (1, 2, 3, 5, 8); acima de 8, quebrar | Planning Poker (Mike Cohn) |
| Tarefas | **Sub-issues** nativas do GitHub ("Parte de #N") | [GitHub — sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues) |
| Sprints | Campo nativo **Iteration** | [GitHub Projects — iteration fields](https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-iteration-fields) |
| Fluxo | Automações nativas (item fechado → Done; PR mesclado → Done) | [GitHub Projects — built-in automations](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations) |
| Commits/PRs | **Conventional Commits** (`feat:`, `fix:`, `docs:`…) | [conventionalcommits.org](https://www.conventionalcommits.org/) |

## Board
https://github.com/users/kauantpereira/projects/1 (privado)

- **Status:** Product Backlog → Sprint Backlog → In Progress → In Review → Done
- **Points:** 1, 2, 3, 5, 8 (nas histórias)
- **Sprint:** Sprint 1 (16–20/11), Sprint 2 (21–25/11; apresentação em 25/11)
- **Views:** Histórias (`label:"user story"`), Sprint atual (`sprint:@current`), Tabela por responsável — criadas pela [API REST de Projects](https://docs.github.com/en/enterprise-server@3.22/rest/projects/views).
- **Automações nativas:** só pela interface (a API não permite ligá-las): item fechado → Done, PR mesclado → Done, PR vinculado → In Review, auto-add do repo.

## Issues
- **História** (`user story`): Connextra + critérios Gherkin + checklist INVEST + checklist de conformidade. Modelo: `.github/ISSUE_TEMPLATE/historia.yml`.
- **Tarefa** (`task`): sub-issue da história. Uma tarefa = uma branch = um PR.

## Labels
| Label | Uso |
|---|---|
| `user story` | história |
| `task` | tarefa |
| `perfil-ufmg` | código específico da UFMG; PR isolado e reversível (ADR-0009) |
| `condicional` | só executar se a DTI negar (ADR-0001) |
| `adiada` | sugestão que não atende a um ADR hoje; issue fechada como "not planned" no milestone "Revisitar após a DTI" (ADR-0015) |
| `prevista-no-build` | entra no build da apresentação (25/11) |
| `nao-prevista` | fica fora do build da apresentação; Product Backlog |
| `apresentação` | preparação da apresentação (slides, roteiro, vídeos das demos; sem live demo) |

## Definição de Pronto (Definition of Done)
Ver [CONTRIBUTING.md](../../CONTRIBUTING.md#definição-de-pronto).
