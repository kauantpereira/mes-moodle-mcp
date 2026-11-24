# Privacidade e regras da instituição

> Explicação (Diátaxis): o porquê. Resume para o usuário as decisões de conformidade, com link para os ADRs.

- **Só leitura** e **só os seus dados** ([ADR-0004](../dev/adr/0004-so-dados-do-proprio-aluno.md)).
- **Sua senha e o token nunca passam pelo chat.** No login da instituição (SSO), a senha fica só no navegador; num Moodle com usuário e senha próprios, ela vai do formulário direto ao Moodle e não é guardada. O token fica no chaveiro do seu computador ([ADR-0002](../dev/adr/0002-login-pelo-fluxo-oficial-do-app-e-token-individual.md), [ADR-0016](../dev/adr/0016-login-sob-demanda-com-chaveiro-e-captura-do-token-pelo-navegador.md)).
- **O material dos professores não é copiado** ([ADR-0003](../dev/adr/0003-material-dos-professores-lido-sob-demanda-sem-copia.md)).
- **Limite de chamadas** para não sobrecarregar o Moodle ([ADR-0005](../dev/adr/0005-contador-e-limite-de-chamadas.md)).
- **Regras de IA de cada disciplina** ([ADR-0006](../dev/adr/0006-aviso-de-uso-de-ia-em-dois-niveis-sem-bloqueio.md)).
