<!-- Título em Conventional Commits: feat(escopo): descrição — vira a mensagem do squash. Ver docs/dev/fluxo-git.md -->

## Descrição

## História / tarefa relacionada
Fecha #

## ADRs
<!-- ADR novo ou afetado; mudar uma decisão aceita exige um ADR novo -->

## Como testar
1.

## Reversão
- [ ] Seguro reverter (sem efeito fora do repositório)
- [ ] Toca um perfil de instituição (`perfis/`): reverter só este PR deixa o núcleo funcionando
- [ ] Exige passo manual (descrever)

## Checklist
- [ ] Branch segue a convenção (`feat/`, `fix/`, `docs/`, `refactor/`, `chore/`, `test/`)
- [ ] Só leitura; nenhum token, senha ou dado pessoal
- [ ] Tamanho das respostas das tools medido (se mudou tool)
- [ ] `uv run pytest` e `claude plugin validate .` passam
- [ ] Documentação do usuário (`docs/`) ou de dev (`docs/dev/`) atualizada
