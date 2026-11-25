# Regras de IA da disciplina

Cada disciplina define no plano de ensino se você pode usar IA nas atividades avaliativas. O servidor não conhece essa regra. Por isso, a skill `regras-de-ia-da-disciplina` lembra você de conferir antes de o agente ajudar ([ADR-0006](../dev/adr/0006-aviso-de-uso-de-ia-em-dois-niveis-sem-bloqueio.md)).

## O que acontece

Quando você pede ajuda para resolver, revisar ou responder uma tarefa, um questionário ou uma prova, o agente pergunta primeiro se a disciplina permite IA. Ele faz a mesma pergunta quando uma tool, como `detalhes_da_tarefa`, devolve uma atividade avaliativa com o aviso no campo `aviso` (ver [tools](../referencia/tools.md#respostas-de-atividades-avaliativas)).

Responda com o que diz o plano de ensino:

| Sua resposta | O que o agente faz |
|---|---|
| Permite | Ajuda normalmente e, se a disciplina pedir, lembra de declarar o uso. |
| Permite com limites (por exemplo, só revisão) | Ajuda só dentro do limite que você informou. |
| Proíbe | Não resolve a atividade; oferece ajuda que não a envolve, como organizar os prazos. |
| Não sei | Sugere conferir o plano de ensino ou perguntar ao professor. A decisão continua sua. |

O agente pergunta uma vez por disciplina em cada conversa. Para pular a pergunta, diga a regra logo no pedido, por exemplo: "A disciplina permite IA só para revisão. Revisa meu relatório?".

## O que não acontece

- O agente não bloqueia você nem decide pela disciplina: o aviso é um lembrete.
- A regra não é gravada em `~~tarefas` nem em outro lugar e não vale para outras disciplinas.
- Um texto no Moodle dizendo que a IA está liberada não conta como permissão. Textos do Moodle são tratados como dados, não como instruções, e o agente pede que você confirme no plano de ensino.
- Pedidos que não envolvem fazer a atividade, como ver prazos ou [organizar a semana](organizar-semana.md), não disparam a pergunta.
