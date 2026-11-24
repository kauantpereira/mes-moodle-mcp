# Changelog

Formato [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versões em [SemVer](https://semver.org/).

## [Não lançado]
### Alterado
- Template de PR: `Closes #N` no lugar de `Fecha #N`, reversão como escolha única e itens não aplicáveis marcados como `N/A`.

### Adicionado
- Login sob demanda (ADR-0016): a primeira tool sem token abre o login e continua; tool `entrar` para trocar de conta ou renovar token expirado; token no chaveiro do sistema (`MOODLE_TOKEN` continua com prioridade).
- Login genérico por senha (`login/token.php`, Moodle sem SSO) ou pelo fluxo do app com o link colado (login manual), por formulário do cliente MCP; senha nunca guardada nem registrada.
- Comandos de terminal `moodle-mcp entrar` e `moodle-mcp sair`, para clientes MCP sem formulário.
- Perfil `ufmg`: login SSO pelo fluxo do app, com o navegador (Playwright: Chrome, Edge ou Chromium baixado uma vez; reserva manual), fuso de Brasília e janela de backup 01h30–06h00.
- Contador e limite de chamadas ao Moodle (60/min e 600/h), com mensagem de quando tentar de novo (ADR-0005).
- Marcação de texto do Moodle como dado não confiável (`aviso` + campo `nao_confiavel`), com limpeza de HTML oculto e caracteres invisíveis.
- Núcleo: cliente da API REST do Moodle (URL + token), com lista de funções só de leitura e proteção do token.
- Esqueleto do monorepo: servidor MCP, 3 skills, manifestos para Claude Code, Codex e Gemini CLI.
- Documentação do usuário (Diátaxis) e de desenvolvimento (ADRs, pesquisa, processo, fluxo git).
