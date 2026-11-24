# Changelog

Formato [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versões em [SemVer](https://semver.org/).

## [Não lançado]
### Alterado
- Template de PR: `Closes #N` no lugar de `Fecha #N`, reversão como escolha única e itens não aplicáveis marcados como `N/A`.

### Adicionado
- Tool `quem_sou_eu`: verifica a conexão e informa nome do aluno, site, URL e versão do Moodle (sem expor token ou dados sensíveis).
- Marcação de texto do Moodle como dado não confiável (`aviso` + campo `nao_confiavel`), com limpeza de HTML oculto e caracteres invisíveis.
- Núcleo: cliente da API REST do Moodle (URL + token), com lista de funções só de leitura e proteção do token.
- Esqueleto do monorepo: servidor MCP, 3 skills, manifestos para Claude Code, Codex e Gemini CLI.
- Documentação do usuário (Diátaxis) e de desenvolvimento (ADRs, pesquisa, processo, fluxo git).
