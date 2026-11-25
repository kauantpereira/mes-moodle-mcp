# Changelog

Formato [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versões em [SemVer](https://semver.org/).

## [Não lançado]
### Alterado
- O plugin não pede mais o endereço do Moodle (ADR-0017): vem da variável `MOODLE_URL` ou do perfil da instituição (semestre atual). Sem `user_config` no `.mcp.json`, o servidor também sobe no Claude Desktop.
- Mensagem de erro para `invalidtoken` em `nucleo.chamar` agora orienta como entrar de novo (tool `entrar` e alternativa provisória `MOODLE_TOKEN`).
- Template de PR: `Closes #N` no lugar de `Fecha #N`, reversão como escolha única e itens não aplicáveis marcados como `N/A`.

### Adicionado
- Guias: como instalar o `uv` no Windows (`docs/guias/instalar.md`) e o aviso de que a rotina diária precisa rodar no computador onde o plugin está instalado, não em sessão na nuvem (`docs/guias/rotina-diaria.md`).
- Skill `regras-de-ia-da-disciplina`: antes de ajudar numa atividade avaliativa, o agente confere ou pergunta se a disciplina permite IA e ajuda conforme a resposta, sem bloquear e sem tratar texto do Moodle como permissão (ADR-0006). Guia em `docs/guias/regras-de-ia-da-disciplina.md`.
- Semestre nas tools (ADR-0017): parâmetro opcional `semestre` (só aquela chamada), tool `usar_semestre` (até o servidor reiniciar) e `moodle-mcp entrar|sair --semestre`; um token por semestre, o mesmo limite de chamadas para todos.
- Entrada sobre token expirado/inválido no guia de solução de problemas (`docs/guias/solucao-de-problemas.md`).
- Tool `quem_sou_eu`: verifica a conexão e informa nome do aluno, site, URL e versão do Moodle (sem expor token ou dados sensíveis).
- Janela de manutenção definida pelo perfil da instituição: nessa faixa de horário o Moodle não é chamado e a mensagem diz a partir de quando tentar; o que já está em cache continua disponível (ADR-0005).
- Cache curto (5 min) da lista de disciplinas e do conteúdo das disciplinas: menos chamadas ao Moodle, sem contar no limite (ADR-0005).
- Login sob demanda (ADR-0016): a primeira tool sem token abre o login e continua; tool `entrar` para trocar de conta ou renovar token expirado; token no chaveiro do sistema (`MOODLE_TOKEN` continua com prioridade).
- Login genérico por senha (`login/token.php`, Moodle sem SSO) ou pelo fluxo do app com o link colado (login manual), só no terminal; senha nunca guardada nem registrada, e nada é pedido pelo chat.
- Comandos de terminal `moodle-mcp entrar` (`--manual` para colar o link do fluxo do app) e `moodle-mcp sair`.
- Perfil `ufmg`: endereço do Moodle do semestre atual sem configurar nada (`virtual.ufmg.br/AAAAS`), outro semestre como `2026.1` ou `anterior` (ADR-0017).
- Perfil `ufmg`: login SSO pelo fluxo do app, com o navegador (Playwright: Chrome, Edge ou Chromium baixado uma vez; sem navegador, login manual pelo terminal), fuso de Brasília e janela de backup 01h30–06h00.
- Contador e limite de chamadas ao Moodle (60/min e 600/h), com mensagem de quando tentar de novo (ADR-0005).
- Marcação de texto do Moodle como dado não confiável (`aviso` + campo `nao_confiavel`), com limpeza de HTML oculto e caracteres invisíveis.
- Núcleo: cliente da API REST do Moodle (URL + token), com lista de funções só de leitura e proteção do token.
- Esqueleto do monorepo: servidor MCP, 3 skills, manifestos para Claude Code, Codex e Gemini CLI.
- Documentação do usuário (Diátaxis) e de desenvolvimento (ADRs, pesquisa, processo, fluxo git).

### Corrigido
- No Windows, todas as tools falhavam com `Error executing tool`: o pacote `tzdata` não era dependência e o sistema não tem banco de fusos horários. Agora é declarado, com teste que simula a falta do banco.
- Login pelo navegador no Claude Desktop (Linux): o servidor acha a tela da sessão do aluno quando o app não repassa `DISPLAY`; antes, a tool dizia que não havia navegador.
- Login pelo navegador: a janela abre no Minhas Turmas (UFMG) ou no login do Moodle, o aluno entra como sempre e o token é pedido por baixo com a sessão; acaba com a página de erro e o diálogo para abrir `moodlemobile://` com outro programa (xdg-open) no fim do SSO.
- `detalhes_da_tarefa`: os tipos de arquivo aceitos vêm da config real do Moodle (`filetypeslist`); antes vinham sempre vazios. A tool não faz mais uma chamada extra para o `userid`.
- `detalhes_da_tarefa` e `notas_da_disciplina`: sem token, abrem o login como as outras tools, em vez de pedir para usar `entrar`.
