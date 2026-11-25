---
status: proposed
date: 2026-11-24
decision-makers: grupo G15
---
# ADR-0019: Rotina diária com permissões mínimas e registro das mudanças

## Contexto e problema
A história #3 quer o calendário atualizado todo dia, sem o aluno presente. Sem ninguém para confirmar, uma instrução escondida num aviso (injeção de prompt, `docs/dev/pesquisa.md`) poderia levar o agente a criar, mudar ou apagar eventos. O servidor é somente leitura (regra 1), mas o `~~calendário` não é dele: as permissões de escrita ali são do agente.

## Decisão
A rotina é a skill `novidades-da-faculdade` em **modo rotina**. Nesse modo:

- **Moodle:** só as tools de leitura (`novidades_desde`, `avisos_recentes`, `mudancas_de_cronograma`).
- **`~~calendário`:** só ajusta **data, horário e título de eventos que já existem** e correspondem, de forma única, a um prazo que mudou (início igual ao prazo anterior e título com o nome da atividade). Nunca cria nem apaga evento, nem mexe em descrição, convidados, lembretes ou local.
- **Título:** só para igualar ao nome oficial da atividade devolvido por `mudancas_de_cronograma`; nunca a partir de texto de aviso.
- **`~~tarefas`:** nada. Avisos que pedem ação só entram no registro, para o aluno decidir depois.
- **Dúvida, ausência ou mais de um evento candidato:** não altera; lista em "precisam de você". Prazos novos ou removidos também só são listados.
- **Login:** nunca usa `entrar`. Se uma tool pedir login ou o Moodle estiver em manutenção, a rotina para e registra.
- **Registro:** toda execução termina com um registro em Markdown (alterados com antes e depois, pendências, assuntos e links dos avisos, disciplinas não consultadas), mostrado ao aluno e gravado em `log-da-rotina.md` na pasta `moodle-mcp` do diretório de dados do usuário, quando o agente tem acesso a arquivos. Só nomes de atividades e disciplinas, assuntos e datas: nunca o texto dos avisos, token ou URL. A data da última execução no registro é o `desde` da próxima.
- **Ordem:** a referência de prazos só avança (`registrar=true`) depois que o registro foi produzido.

O plugin não agenda a rotina: quem agenda é o agente do aluno, no horário que ele escolher (`horario_rito`).

## Opções consideradas
- **Escolhida:** a decisão acima
- Rotina com confirmação a cada mudança: inviável sem o aluno presente.
- Rotina que também cria e apaga eventos: aumenta o estrago possível de uma injeção bem-sucedida.
- Nenhuma escrita automática (só resumo): seguro, mas não entrega "o calendário atualizado todo dia".
- Registro dentro do evento (descrição): mexe num campo que a rotina não deve tocar.

## Consequências
- Bom: o pior caso de uma injeção é mudar a data de um evento já existente, e o registro mostra exatamente o que mudou.
- Ruim / a acompanhar: as regras de permissão são instruções à skill, não uma trava do servidor: o `~~calendário` é do agente, e o eval de injeção (#15) é quem mede se elas são seguidas. Se o token tiver expirado, o login sob demanda do servidor ainda pode abrir uma janela do navegador. Codex e Gemini podem não ter agendador próprio. Sem acesso a arquivos, o registro fica só no chat e a próxima execução usa "ontem" como `desde`.

## Fontes
- [ADR-0006](0006-aviso-de-uso-de-ia-em-dois-niveis-sem-bloqueio.md), [ADR-0010](0010-skills-por-categoria-nao-por-produto.md), [ADR-0018](0018-estado-local-so-com-ids-e-datas-para-o-cronograma.md)
- `docs/dev/pesquisa.md` (mitigações de injeção de prompt: rotinas com o mínimo de permissões, log das mudanças)
