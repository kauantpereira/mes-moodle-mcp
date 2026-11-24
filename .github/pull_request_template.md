<!-- Título em Conventional Commits: feat(escopo): descrição — vira a mensagem do squash. Ver docs/dev/fluxo-git.md -->

## Descrição

## História / tarefa relacionada
<!-- "Closes #N" fecha a issue no merge (o GitHub só entende a palavra-chave em inglês). Para só relacionar: "Refs #N". -->
Closes #

## ADRs
<!-- ADR novo ou afetado; mudar uma decisão aceita exige um ADR novo -->

## Como testar
1.

## Reversão
<!-- Escolha uma opção e apague as outras. -->
Seguro reverter (sem efeito fora do repositório) | Toca `perfis/`: reverter só este PR deixa o núcleo funcionando | Exige passo manual: (descrever)

## Checklist
<!-- Marque o que vale. Item que não se aplica: troque [ ] por "N/A" e diga o porquê. Caixinha vazia = pendente: não faça merge. -->
- [ ] Branch segue a convenção (`feat/`, `fix/`, `docs/`, `refactor/`, `chore/`, `test/`)
- [ ] Só leitura; nenhum token, senha ou dado pessoal
- [ ] Tamanho das respostas das tools medido (N/A se não mudou tool)
- [ ] `uv run pytest` e `claude plugin validate .` passam
- [ ] Documentação do usuário (`docs/`) ou de dev (`docs/dev/`) atualizada (N/A se não muda comportamento)
