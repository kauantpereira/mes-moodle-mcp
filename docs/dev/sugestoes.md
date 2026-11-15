# Coleta de histórias

Estrutura e estratégia para o grupo sugerir histórias. Nada é automático. Decisão: [ADR-0015](adr/0015-fluxo-de-sugestoes-com-triagem-de-conformidade.md).

## Estrutura
- **Uma issue fixada, "Coleta de histórias"** (label `task`, no board). Todo mundo sugere **comentando nela**, um comentário por ideia, no formato:
  ```
  Como aluno, quero … para …
  Exemplo: na segunda de manhã eu pergunto … e o agente …
  Dados do Moodle que usaria: …
  ```
- As histórias-exemplo (label `user story`) mostram o formato completo.

## Estratégia
- As sugestões se acumulam na coleta e são **processadas em lote**, de tempos em tempos (a rotina — quando e quem — será combinada depois).
- No processamento, cada sugestão é comparada aos ADRs de conformidade (0001–0006) e recebe uma resposta no próprio comentário:

| Resultado | O que acontece |
|---|---|
| **aprovada** | vira issue `user story` no Product Backlog, quebrada em tarefas; tarefas que já existem são reaproveitadas como dependência ("bloqueada por #N"), sem duplicar |
| **adaptar** | a resposta propõe uma versão que atende aos ADRs; a autora ajusta no próprio comentário |
| **adiada** | vira issue fechada como "not planned", label `adiada`, citando o ADR, no milestone **Revisitar após a DTI** |

- Por que as adiadas viram issue fechada: ficam pesquisáveis (`is:closed label:adiada`) e ligadas ao ADR que as impediu. Se a DTI autorizar e um ADR ficar mais brando, reabrem-se as daquele ADR.
- Uma tarefa (sub-issue) tem **um só pai** no GitHub; por isso o reaproveitamento é por dependência.

## Fontes
- [GitHub — fixar issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/pinning-an-issue-to-your-repository)
- [GitHub — fechar issue como "not planned"](https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/closing-an-issue)
- [GitHub — sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues) e [dependências entre issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies)
- [GitHub — milestones](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones)
