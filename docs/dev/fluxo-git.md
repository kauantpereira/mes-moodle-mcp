# Fluxo de trabalho no repositório

Como interagir com o repositório: branches, commits, PRs, revisão e versões. Vale para pessoas e agentes (ver [AGENTS.md](../../AGENTS.md)). Decisão: [ADR-0014](adr/0014-github-flow-conventional-commits-e-semver.md).

## Branches: GitHub Flow
- `main` está sempre funcionando (testes e validação do plugin passam).
- **Não há branch `dev`** nem `develop`: no GitHub Flow, `main` é a única branch de longa duração (ADR-0014). Ideias adiadas não viram branch: ver `sugestoes.md`.
- Toda mudança nasce numa branch a partir de `main`, com prefixo do tipo e o número da issue:
  `feat/12-novidades-desde`, `fix/30-token-expirado`, `docs/15-guia-gemini`.
- Uma tarefa (issue `task`) = uma branch = um PR.
- Código de perfil de instituição (`perfis/`) sempre em branch e PR próprios, com label `perfil-ufmg` (ADR-0009).

## Commits: Conventional Commits 1.0
```
<tipo>(<escopo opcional>): <descrição no imperativo, minúscula, sem ponto>

<corpo opcional: o porquê>

Refs #12
```
| Tipo | Uso |
|---|---|
| `feat` | nova funcionalidade para o usuário (tool, skill, opção) |
| `fix` | correção de bug |
| `docs` | só documentação (usuário ou dev, ADRs) |
| `test` | testes e evals |
| `refactor` | mudança interna sem alterar comportamento |
| `chore` | manutenção (dependências, configuração, CI) |

- Escopos sugeridos: `tools`, `skills`, `perfil-ufmg`, `plugin`, `auth`, `docs`.
- Descrição em português, no imperativo: `feat(tools): adiciona novidades_desde`.
- Mudança incompatível: `!` depois do tipo (`feat(tools)!:`) e rodapé `BREAKING CHANGE:`.
- Rodapés: `Refs #N` (relaciona) no commit; o fechamento da issue fica no PR.
- Commits feitos com ajuda de agente de IA levam o rodapé `Co-Authored-By:` do agente (transparência, Guia de IA da UFMG).

## Pull requests
- **Título** no mesmo formato de commit (`feat(tools): adiciona novidades_desde`): ele vira a mensagem do squash.
- **Corpo** pelo [template](../../.github/pull_request_template.md): descrição, `Closes #N` (palavra-chave de fechamento do GitHub: só funciona em inglês; `Fecha #N` não fecha a issue), ADRs, como testar, plano de reversão (uma opção) e checklist (caixinha vazia = pendente; item que não se aplica vira `N/A` com o motivo).
- Pequeno e focado: se passar de ~400 linhas alteradas, quebrar.
- **Revisão:** pelo menos 1 pessoa do grupo que não seja a autora. Quem revisa confere a [Definição de Pronto](../../CONTRIBUTING.md#definição-de-pronto) e as regras do projeto.
- **Merge:** *squash and merge* (um commit por PR em `main`), e a branch é apagada depois.
- Mudou uma decisão aceita? O PR inclui um ADR novo.

## Versões e mudanças
- **SemVer** (`MAJOR.MINOR.PATCH`): `feat` → MINOR, `fix` → PATCH, `!`/`BREAKING CHANGE` → MAJOR (antes da 1.0, MINOR).
- A versão aparece em 4 lugares e muda junto: `pyproject.toml`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`.
- `CHANGELOG.md` no formato Keep a Changelog, atualizado a cada versão (os títulos dos PRs em Conventional Commits facilitam).
- Versão marcada com tag `vX.Y.Z` em `main`.

## Fontes
- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)
- [Conventional Commits 1.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [GitHub — vincular PR a issue (palavras-chave de fechamento)](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)
- [GitHub — squash merge](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests)
- [GitHub — commits com coautores](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
- [Google Engineering Practices — tamanho de mudanças](https://google.github.io/eng-practices/review/developer/small-cls.html)
