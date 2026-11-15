# Sugestões de histórias: da ideia ao board

Qualquer pessoa do grupo pode sugerir histórias. Toda sugestão passa por uma **triagem de conformidade** contra os ADRs antes de ir para o board. Decisão: [ADR-0015](adr/0015-fluxo-de-sugestoes-com-triagem-de-conformidade.md).

```
Sugestão (issue, label "sugestão")
  └─ Triagem: revisão automática + 1 pessoa do grupo, contra os ADRs 0001–0006
       ├─ aprovada  → vira "user story" no Product Backlog, quebrada em tarefas
       ├─ adaptar   → ajustar o texto e voltar para a triagem
       └─ adiada    → fechada como "not planned", label "adiada", milestone "Revisitar após a DTI"
```

## 1. Sugerir
Abrir uma issue pelo modelo **Sugestão de história** (`.github/ISSUE_TEMPLATE/sugestao.yml`). As histórias com label `user story` servem de exemplo.

## 2. Triagem
- **Automática:** o workflow `.github/workflows/triagem-sugestao.yml` comenta na issue uma tabela "ADR → atende / não atende / dúvida", uma proposta de adaptação e as tarefas já existentes que podem ser reaproveitadas. Ela só ajuda; quem decide é o grupo.
- **Humana:** uma pessoa do grupo (não a autora) confere e aplica um dos rótulos abaixo.

| Resultado | O que fazer |
|---|---|
| `aprovada` | Trocar `sugestão` por `user story`, completar critérios Gherkin e pontos, mover para Product Backlog, criar as tarefas. |
| `adaptar` | Comentar o que muda para atender aos ADRs; a autora edita e pede nova triagem. |
| `adiada` | Fechar como **not planned**, citar no comentário o ADR que impede e pôr no milestone **Revisitar após a DTI**. |

## 3. Reaproveitar tarefas
No GitHub, uma tarefa (sub-issue) tem **um só pai**. Se a história nova precisa de uma tarefa que já existe em outra história:
- **não duplicar**: marcar a história nova como **bloqueada por** a tarefa existente (dependência nativa do GitHub);
- citar a tarefa na descrição ("Reaproveita #N").
Só criar tarefa nova para o que for exclusivo da história.

## 4. Sugestões adiadas
Ficam fechadas, mas pesquisáveis (`is:closed label:adiada`), cada uma ligada ao ADR que a impediu. Se a DTI autorizar e um ADR for substituído por outro mais brando, reabrir as adiadas daquele ADR e refazer a triagem.

Por que não uma branch separada: branches guardam código, não ideias; uma branch que nunca é mesclada fica desatualizada e não aparece no board. Issue fechada como "not planned" com label e milestone é o mecanismo nativo do GitHub para isso.

## Fontes
- [GitHub — issue forms](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms)
- [GitHub — fechar issue como "not planned"](https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/closing-an-issue)
- [GitHub — sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues) (um pai por sub-issue) e [dependências entre issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies)
- [GitHub — milestones](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones)
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) (revisão automática)
