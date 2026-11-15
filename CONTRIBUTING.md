# Contribuição

## Regras do projeto
1. **Só leitura.** Nenhuma tool chama função do Moodle que envie, publique ou altere dados.
2. **Só dados do próprio aluno.** Nada de participantes, posts de colegas ou notas de terceiros.
3. **Nenhum token, senha ou dado pessoal no repositório**, nem em testes ou fixtures.
4. **Perfis isolados.** O que é específico de uma instituição (URL, login, regras) fica em `src/moodle_mcp/perfis/<instituicao>.py`, entra em PR próprio e pode ser revertido sem quebrar o núcleo. O núcleo recebe só URL + token.
5. **Texto do Moodle é dado não confiável.** Toda tool que devolve texto escrito por pessoas marca isso na resposta.
6. **Contexto medido.** Toda tool nova informa o tamanho típico da resposta; o alvo é ficar abaixo de ~2 mil tokens, com filtros e cortes padrão.
7. **Skills por categoria** (`~~calendário`, `~~tarefas`), nunca por produto. Partir de skills oficiais ou open source confiáveis quando houver.

## Fluxo
- Uma história = uma issue = um PR.
- `uv run pytest` e `claude plugin validate .` passam antes do merge.
