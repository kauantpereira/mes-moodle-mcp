# Decisões do projeto

Registro curto das decisões tomadas no planejamento (15/11/2026).

| # | Decisão | Motivo |
|---|---|---|
| D1 | Pedir autorização à DTI (item 3.9 do Termo de Uso da UFMG) antes de qualquer divulgação. Se negar, ou não responder até 25/11, o projeto **não é publicado** e a demo usa um Moodle local. | O Termo exige autorização expressa para robôs que autenticam e extraem dados. |
| D2 | Login pelo fluxo oficial do app (serviço `moodle_mobile_app`), token individual no chaveiro do sistema. | Itens 3.3 e 3.6: conta individual e responsabilidade do usuário. |
| D3 | Material dos professores lido sob demanda, sem cópia nem redistribuição. | Guia de IA da UFMG (p. 19) e direitos autorais. |
| D4 | Só dados do próprio aluno. | LGPD; Guia de IA (p. 9 e 18). |
| D5 | Contador e limite de chamadas; evitar a janela de backup do Moodle UFMG (01h30–06h00). | Item 3.9 e Políticas de Uso do Moodle. |
| D6 | Aviso de uso de IA em dois níveis: instrução do servidor + campo `aviso` em atividades avaliativas. Sem bloqueio. | Guia de IA (p. 23); a decisão é do aluno. |
| D7 | Atender agentes locais (Claude Code/Desktop, Codex, Gemini CLI) num monorepo, com um manifesto por plataforma. Apps web ficam fora. | Apps web exigem MCP remoto, o que obrigaria a custodiar tokens de terceiros. |
| D8 | Tools orientadas à tarefa (ex.: `novidades_desde` com `core_course_get_updates_since`). | Linha de base medida na demo: ~123 mil caracteres para "o que mudou" lendo o conteúdo de 12 disciplinas, contra 555 com a função de diferenças no maior curso. |
| D9 | Autenticação específica da UFMG em perfil isolado e reversível. Moodle local e dados mockados só se D1 resultar em negativa. | Permitir reverter o acesso à UFMG sem perder a demo. |
| D10 | Skills por categoria (`~~calendário`, `~~tarefas`) com saídas universais (.ics, Markdown, chat). | Servir a quem não usa Google Agenda. |
