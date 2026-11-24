# Solução de problemas

> Guia. Sintoma → causa → o que fazer. A preencher com os erros reais da demo (Moodle fora do ar, limite de chamadas).

## Login

| Sintoma | Causa | O que fazer |
|---|---|---|
| "O Moodle recusou ... Faça login de novo." | Token expirado ou revogado | Peça ao agente para entrar de novo (tool `entrar`). |
| "Este cliente MCP não mostra formulários de login..." | O cliente não suporta elicitation no meio da tool | Entre pelo terminal: `uvx --from git+https://github.com/kauantpereira/mes-moodle-mcp moodle-mcp entrar --url <endereço do Moodle>`. |
| "Usuário ou senha incorretos." | Senha errada, ou o Moodle usa login da instituição (SSO) | Confira; com SSO, escolha o fluxo do app. |
| "O Moodle recusou o login por senha (o site pode usar só SSO)." | O site não aceita senha pelo app | Escolha o fluxo do app. |
| "O link não corresponde a este login" | Link de outra tentativa ou de outro endereço do Moodle | Gere um link novo pelo link mostrado agora; use o mesmo endereço configurado no plugin. |
| "A janela do navegador foi fechada antes de concluir o login." | A janela de login foi fechada | Peça ao agente para entrar de novo e conclua o login na janela que abrir. |
| "Tempo esgotado sem concluir o login no navegador." | O login levou mais de 10 minutos | Entre de novo. |
| "Não consegui abrir um navegador; vamos pelo login manual." | Sem Chrome/Edge e sem conseguir baixar o navegador do Playwright, ou sem tela | Siga o login manual (colar o link) ou instale o Chrome. |
| "MOODLE_TOKEN está definida no ambiente..." | Variável provisória de desenvolvimento | Remova `MOODLE_TOKEN` do ambiente e reinicie o servidor. |
| `entrar` responde `token_no_chaveiro: false` | Sem chaveiro do sistema (comum em Linux sem Secret Service) | Instale/ative um chaveiro (ex.: GNOME Keyring); sem ele, o login vale até o servidor reiniciar. |
