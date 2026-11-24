# Solução de problemas

## O Moodle recusou a consulta (token expirado ou inválido)

- **Sintoma:** uma tool falha com `O Moodle recusou <função>. O token expirou ou foi revogado. Entre de novo usando a tool entrar...` (ou erro de token expirado/inválido).
- **Causa:** o token de acesso do Moodle expirou, foi revogado ou deixou de ser aceito pela instituição.
- **Como resolver:**
  1. Peça ao agente para entrar de novo usando a tool `entrar`.
  2. Enquanto o fluxo de login ainda não estiver disponível no seu ambiente, gere um novo token e atualize a variável provisória `MOODLE_TOKEN` (veja [Configuração](../referencia/configuracao.md#token-do-moodle-provisório)), reiniciando o servidor MCP em seguida.
  3. Use a tool `quem_sou_eu` (ou pergunte ao agente "estou conectado no Moodle certo?") para confirmar que a conexão voltou a funcionar.
