# Documentação de desenvolvimento

Para quem desenvolve o projeto (pessoas e agentes). A documentação do usuário fica em `docs/` (fora desta pasta).

| Assunto | Onde |
|---|---|
| Regras e comandos (pessoas e agentes) | [AGENTS.md](../../AGENTS.md), [CONTRIBUTING.md](../../CONTRIBUTING.md) |
| Decisões técnicas | [adr/](adr/) (MADR, com fontes) |
| Pesquisa (regras, boas práticas, comparação, distribuição) | [pesquisa.md](pesquisa.md) |
| Arquitetura | [arquitetura.md](arquitetura.md) |
| Avaliações (evals) | [../../evals/](../../evals/) |
| Processo (Scrum), board e issues | [board.md](board.md) |
| Branches, commits, PRs e versões | [fluxo-git.md](fluxo-git.md) |
| Coleta de histórias (sugestões do grupo) | [sugestoes.md](sugestoes.md) |

## Como registrar contexto
- **Decisão que afeta a arquitetura, a conformidade ou o usuário → ADR** (`adr/template.md`), em PR junto com o código.
- **Regra que todo agente/pessoa deve seguir sempre → AGENTS.md** (curto; o resto fica linkado).
- **Discussão e andamento → issues e PRs**, ligando o ADR quando houver.
