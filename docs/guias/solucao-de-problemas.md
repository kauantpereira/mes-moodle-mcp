# Solução de problemas

> Guia. Sintoma → causa → o que fazer. A preencher com os erros reais da demo (token expirado, Moodle fora do ar, limite de chamadas).

## O Moodle recusou a consulta (token expirado ou inválido)

- **Sintoma:** uma tool falha com `O Moodle recusou <função>. O token expirou ou foi revogado. Entre de novo usando a tool entrar...` (ou erro de token expirado/inválido).
- **Causa:** o token de acesso do Moodle expirou, foi revogado ou deixou de ser aceito pela instituição.
- **Como resolver:**
  1. Peça ao agente para entrar de novo usando a tool `entrar`.
  2. Se a tool responder com um comando de terminal (`moodle-mcp entrar`), rode-o: o servidor passa a usar o token novo sem reiniciar. Se você usa a variável provisória `MOODLE_TOKEN`, gere um token novo, atualize a variável (veja [Configuração](../referencia/configuracao.md#token-do-moodle-provisório)) e reinicie o servidor MCP.
  3. Use a tool `quem_sou_eu` (ou pergunte ao agente "estou conectado no Moodle certo?") para confirmar que a conexão voltou a funcionar.

## Um material ou disciplina nova ainda não aparece
- **Causa:** a lista de disciplinas e o conteúdo de cada disciplina ficam guardados por até 5 minutos, para não sobrecarregar o Moodle da instituição.
- **O que fazer:** espere alguns minutos e peça de novo. Prazos, entregas e notas não passam por esse cache.

## "O Moodle está em manutenção"
- **Causa:** algumas instituições reservam um horário fixo para manutenção do Moodle (ex.: backup de madrugada). Nesse horário o plugin não chama o Moodle, para não atrapalhar a manutenção.
- **O que fazer:** tente de novo a partir do horário indicado na mensagem. O que foi consultado há poucos minutos (lista de disciplinas, conteúdo) ainda pode aparecer, porque vem do cache.

## Login

| Sintoma | Causa | O que fazer |
|---|---|---|
| "Este login é feito no terminal..." | O login precisa de senha ou do link do login manual, que o servidor nunca pede pelo chat | Rode o comando da mensagem no terminal: `uvx --from git+https://github.com/kauantpereira/mes-moodle-mcp moodle-mcp entrar --url <endereço do Moodle>`. |
| "Usuário ou senha incorretos." | Senha errada, ou o Moodle usa login da instituição (SSO) | Confira; com SSO, escolha o fluxo do app. |
| "O Moodle recusou o login por senha (o site pode usar só SSO)." | O site não aceita senha pelo app | Escolha o fluxo do app. |
| "O link não corresponde a este login" | Link de outra tentativa ou de outro endereço do Moodle | Gere um link novo pelo link mostrado agora; use o mesmo endereço configurado no plugin. |
| "MOODLE_TOKEN está definida no ambiente..." | Variável provisória de desenvolvimento | Remova `MOODLE_TOKEN` do ambiente e reinicie o servidor. |
| `entrar` responde `token_no_chaveiro: false` | Sem chaveiro do sistema (comum em Linux sem Secret Service) | Instale/ative um chaveiro (ex.: GNOME Keyring); sem ele, o login vale até o servidor reiniciar. |
