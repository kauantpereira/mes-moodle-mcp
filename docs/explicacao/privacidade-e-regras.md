# Privacidade e regras da instituição

> Explicação (Diátaxis): o porquê. Resume para o usuário as decisões de conformidade, com link para os ADRs.

- **Só leitura** e **só os seus dados** ([ADR-0004](../dev/adr/0004-so-dados-do-proprio-aluno.md)).
- **Sua senha e o token nunca passam pelo chat.** No login da instituição (SSO), a senha fica só no navegador; num Moodle com usuário e senha próprios, ela é digitada só no terminal (`moodle-mcp entrar`), vai direto ao Moodle e não é guardada. O token fica no chaveiro do seu computador ([ADR-0002](../dev/adr/0002-login-pelo-fluxo-oficial-do-app-e-token-individual.md), [ADR-0016](../dev/adr/0016-login-sob-demanda-com-chaveiro-e-captura-do-token-pelo-navegador.md)).
- **Um único arquivo local, só com ids e datas.** Para dizer que um prazo foi adiado, o servidor lembra o prazo anterior de cada tarefa (número e data, nunca nomes nem textos) em `moodle-mcp/cronograma.json`, na pasta de dados do seu usuário. Apague o arquivo quando quiser ([ADR-0018](../dev/adr/0018-estado-local-so-com-ids-e-datas-para-o-cronograma.md)).
- **O material dos professores não é copiado** ([ADR-0003](../dev/adr/0003-material-dos-professores-lido-sob-demanda-sem-copia.md)).
- **Limite de chamadas** para não sobrecarregar o Moodle ([ADR-0005](../dev/adr/0005-contador-e-limite-de-chamadas.md)).
- **Regras de IA de cada disciplina**: antes de ajudar numa atividade avaliativa, o agente pergunta se a disciplina permite IA. Ele lembra, mas não bloqueia; a decisão é sua ([ADR-0006](../dev/adr/0006-aviso-de-uso-de-ia-em-dois-niveis-sem-bloqueio.md), [guia](../guias/regras-de-ia-da-disciplina.md)).
