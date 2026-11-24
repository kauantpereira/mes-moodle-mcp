---
status: accepted
date: 2026-11-24
decision-makers: grupo G15
---
# ADR-0017: Endereço do Moodle vindo do perfil e semestre escolhido pelas tools

## Contexto e problema
O plugin pedia o endereço do Moodle na instalação (`moodle_url`, obrigatório) e o repassava ao servidor por `${user_config.moodle_url}` no `.mcp.json`. Três problemas:

- **O Claude Desktop descarta o servidor.** Instalado pela página de plugins do Desktop, o servidor some e as skills ficam sem tools. O log registra: "config references plugin user configuration (moodle_url) — user_config is not supported on the desktop host bridge; dropping server".
- **Codex e Gemini CLI não passam variáveis ao servidor de um plugin.** Por isso o `user_config` não chega lá.
- **Na UFMG, cada semestre é um Moodle separado** (`virtual.ufmg.br/20262`, `/20261`…). Um endereço fixo envelhece a cada semestre. Uma lista de semestres nas opções do manifesto também envelheceria e seria código da UFMG fora de `perfis/` (regra 4).

## Decisão
1. **O plugin não pede mais o endereço.**
   - O `.mcp.json` não cita `user_config`.
   - O endereço vem, nesta ordem:
     1. da variável `MOODLE_URL`, se definida;
     2. senão, do **perfil padrão**: o único perfil carregado que sabe montar a URL (`Perfil.url_do_semestre`, `perfis.padrao()`).
   - Sem perfil padrão (ex.: perfil `ufmg` revertido), a tool explica como definir `MOODLE_URL`.
2. **O semestre é escolhido pelas tools, não pela config.**
   - Sem escolha, vale o semestre atual (o perfil calcula pela data).
   - Parâmetro opcional `semestre` nas tools: vale só para aquela chamada.
   - Tool `usar_semestre`: troca o semestre de todas as tools até o servidor reiniciar. Fica só na memória, para ninguém ficar preso num semestre velho sem perceber.
   - Também `moodle-mcp entrar|sair --semestre`.
3. **O formato do semestre pertence ao perfil.** O núcleo só repassa o texto do aluno a `url_do_semestre`, que devolve a URL ou levanta `ValueError` com a explicação. O que é "2026.1", "anterior" ou "atual" fica em `perfis/<inst>.py`.
4. **Cada semestre é um Moodle:** um cliente e um token no chaveiro por URL. O limite de chamadas (ADR-0005) é um só para o processo, somando todos.

## Opções consideradas
- **Escolhida:** a decisão acima.
- **Manter `moodle_url` obrigatório:** o Desktop descarta o servidor, e Codex e Gemini não recebem o valor.
- **Lista de semestres nas opções do plugin:** fere a regra 4, exige versão nova a cada semestre e também dependeria de `user_config`.
- **Opção "atual/anterior" na config:** genérica, mas depende de `user_config`, que o Desktop não suporta. A tool `usar_semestre` faz o mesmo pelo chat.
- **Guardar o semestre escolhido entre sessões:** fácil esquecer que ficou no semestre velho.

## Consequências
- Bom: na UFMG, o aluno instala sem digitar nada, e o mesmo plugin funciona no Claude Code, no Claude Desktop (Cowork local), no Codex e no Gemini CLI. Consultar outro semestre não exige reconfigurar nem reiniciar.
- Bom: reverter o perfil `ufmg` continua deixando o núcleo funcional, só que com `MOODLE_URL` obrigatória (ADR-0009).
- Ruim / a acompanhar:
  - Quem usa outro Moodle precisa definir `MOODLE_URL` no ambiente do servidor, porque não há mais campo no plugin.
  - Toda tool nova deve aceitar `semestre` e repassá-lo ao `nucleo.chamar`.
  - O semestre atual pela data pode errar na virada, se a instituição abrir o Moodle novo em outra data: `usar_semestre` resolve no momento.

## Fontes
- Log do Claude Desktop (`~/.config/Claude/logs/main.log`), 24/11/2026.
- [Claude Code: user configuration de plugins](https://code.claude.com/docs/en/plugins-reference) (`${user_config.*}` só é substituído no Claude Code; processos MCP não recebem `CLAUDE_PLUGIN_OPTION_*`).
- [cooklang/cooklang-skills](https://github.com/cooklang/cooklang-skills): no Codex, a config do plugin não define variáveis do servidor.
- ADR-0005, ADR-0009, ADR-0016.
