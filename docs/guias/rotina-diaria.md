# Rotina diária

A rotina é a skill [`novidades-da-faculdade`](novidades-da-faculdade.md) rodando sozinha, sem você presente, no horário que você escolher. Ela confere o Moodle, ajusta no seu `~~calendário` os eventos de prazos que mudaram e deixa um registro do que fez para você revisar.

## O que ela pode e não pode fazer

Como ninguém está lá para confirmar, as regras são mais estritas ([ADR-0019](../dev/adr/0019-rotina-diaria-com-permissoes-minimas-e-registro-das-mudancas.md)):

- No Moodle, só **lê**.
- No `~~calendário`, só muda a **data, o horário e o título de eventos que já existem** e que correspondem, sem dúvida, a um prazo que mudou. Nunca cria nem apaga eventos, e não mexe em descrição, convidados, lembretes ou local.
- Quando há dúvida (nenhum evento ou mais de um parecido), não altera: deixa o prazo na lista "Precisam de você".
- Não cria tarefas. Os avisos que pedem alguma ação aparecem só no registro.
- Não faz login. Se o token tiver expirado ou o Moodle estiver em manutenção, ela para e registra isso. Entre de novo pela tool `entrar` e a próxima execução segue normal.
- Textos de avisos são dados, nunca instruções: um aviso que mande a rotina fazer algo é ignorado.

## O registro

Toda execução termina com um registro em Markdown, mostrado a você e, se o agente puder gravar arquivos, acrescentado ao arquivo `log-da-rotina.md`:

- Linux e macOS: `~/.local/share/moodle-mcp/log-da-rotina.md`
- Windows: `%LOCALAPPDATA%\moodle-mcp\log-da-rotina.md`

Ele lista o que foi alterado (evento, data antes e depois), o que precisa de você, os avisos (assunto e link) e o que não foi consultado. Não traz o texto dos avisos. A data da última execução no registro é de onde a próxima começa; sem o arquivo, a rotina olha o último dia. Revise o registro de vez em quando: é ele que mostra qualquer mudança que você não esperava.

## Agendar

O plugin **não agenda sozinho**: o agendamento é do seu agente. A opção `horario_rito` ([configuração](../referencia/configuracao.md)) só guarda o horário que você prefere (padrão `07:00`).

- **Claude Code:** crie uma rotina agendada no horário escolhido, com a instrução "execute a skill novidades-da-faculdade em modo rotina".
- **Codex e Gemini CLI:** ainda não há um passo validado. Rode a skill por conta própria ("novidades da faculdade, em modo rotina") ou use o agendador do seu sistema com o modo não interativo do agente; os guias de instalação trarão o que for confirmado.

**A rotina precisa rodar no computador onde o plugin está instalado.** O servidor do Moodle é local e o login fica guardado nele ([ADR-0007](../dev/adr/0007-agentes-locais-num-monorepo.md)). Uma rotina agendada em sessão na nuvem não consegue iniciar o servidor nem entrar no seu Moodle: nenhuma tool carrega e o agente avisa que não conseguiu consultar, sem ter conferido nada. O mesmo vale para as mudanças de prazo, que são comparadas com uma lista guardada no seu computador. Agende no Claude Code ou no app instalados na sua máquina, que precisa estar ligada no horário.

Evite horários entre 01h30 e 06h00 na UFMG: é a janela de backup do Moodle, e as consultas ficam bloqueadas ([ADR-0005](../dev/adr/0005-contador-e-limite-de-chamadas.md)).
