# Board e issues

Mesmo formato do TP de Engenharia de Software do grupo (`Josejgs1/Trabalho_Pratico-ES`).

## Issues
- **História** (`user story`): título "Como aluno, quero …, para …", com critérios de aceite e checklist de conformidade (modelo em `.github/ISSUE_TEMPLATE/historia.yml`).
- **Tarefa** (`task`): passo implementável, criado como **sub-issue** da história; corpo começa com "Parte de #N".
- Uma tarefa = uma branch = um PR (`feat/…`, `fix/…`, `docs/…`, `refactor/…`, `chore/…`, `test/…`), título com o mesmo prefixo.

## Labels
| Label | Uso |
|---|---|
| `user story` | história |
| `task` | tarefa (sub-issue) |
| `perfil-ufmg` | código específico da UFMG; PR isolado e reversível (ADR-0009) |
| `condicional` | só executar se a DTI negar (ADR-0001) |
| `documentation`, `bug` | padrão do GitHub |

## Board (GitHub Projects)
Colunas: **Backlog → A fazer → Fazendo → Em revisão → Concluído**.
Campos: Tipo (história/tarefa), Responsável, Etapa (planejamento, implementação, demo, apresentação), Prazo.
Prazo final: apresentação em 25/11/2026.
