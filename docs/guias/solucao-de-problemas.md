# Solução de problemas

> Guia. Sintoma → causa → o que fazer. A preencher com os erros reais da demo (token expirado, Moodle fora do ar, limite de chamadas).

## O Moodle recusou a consulta (token expirado ou inválido)

- **Sintoma:** uma tool falha com `O Moodle recusou <função>. O token expirou ou foi revogado. Entre de novo usando a tool entrar...` (ou erro de token expirado/inválido).
- **Causa:** o token de acesso do Moodle expirou, foi revogado ou deixou de ser aceito pela instituição.
- **Como resolver:**
  1. Peça ao agente para entrar de novo usando a tool `entrar`.
  2. Enquanto o fluxo de login ainda não estiver disponível no seu ambiente, gere um novo token e atualize a variável provisória `MOODLE_TOKEN` (veja [Configuração](../referencia/configuracao.md#token-do-moodle-provisório)), reiniciando o servidor MCP em seguida.
  3. Use a tool `quem_sou_eu` (ou pergunte ao agente "estou conectado no Moodle certo?") para confirmar que a conexão voltou a funcionar.

## Um material ou disciplina nova ainda não aparece
- **Causa:** a lista de disciplinas e o conteúdo de cada disciplina ficam guardados por até 5 minutos, para não sobrecarregar o Moodle da instituição.
- **O que fazer:** espere alguns minutos e peça de novo. Prazos, entregas e notas não passam por esse cache.

## "O Moodle está em manutenção"
- **Causa:** algumas instituições reservam um horário fixo para manutenção do Moodle (ex.: backup de madrugada). Nesse horário o plugin não chama o Moodle, para não atrapalhar a manutenção.
- **O que fazer:** tente de novo a partir do horário indicado na mensagem. O que foi consultado há poucos minutos (lista de disciplinas, conteúdo) ainda pode aparecer, porque vem do cache.
