---
status: proposed
date: 2026-11-24
decision-makers: grupo G15
---
# ADR-0018: Estado local só com ids e datas para o cronograma

## Contexto e problema
O Moodle não guarda o histórico dos prazos: ele só diz o prazo de hoje. Para avisar que um prazo foi adiado ("o calendário atualizado todo dia", história #3), `mudancas_de_cronograma` precisa lembrar o prazo da leitura anterior. O ADR-0003 manda não guardar cópia nem índice local do material dos professores; o ADR-0004 limita os dados aos do próprio aluno.

## Decisão
O servidor guarda localmente, em `cronograma.json` no diretório de dados do usuário (permissão 0600, escrita atômica), apenas **ids de tarefas e timestamps de prazo**, por Moodle e por aluno. Nunca nomes, descrições, mensagens nem qualquer texto do Moodle: os nomes mostrados vêm sempre da leitura atual.

- Uma consulta avulsa não muda a referência. Só `registrar=true`, usado pela rotina diária, guarda a leitura como nova referência; a primeira leitura cria a referência sozinha. Assim, perguntar no chat "o que mudou?" não esconde a mudança da rotina das 7h.
- Arquivo ausente, corrompido ou de outra versão vale como "sem leitura anterior". Falha ao gravar não derruba a tool: a resposta diz `registrada: false`.
- Só se guardam prazos de até 30 dias atrás.
- Tarefa que some da resposta aparece como `removido` com o id e a data antiga, sem nome (o nome não foi guardado).

## Opções consideradas
- **Escolhida:** a decisão acima
- Tool sem estado, com a skill guardando a lista anterior: obriga cada agente a guardar e comparar datas, e a rotina deixa de funcionar onde a skill não tem onde escrever.
- Guardar também nomes: facilitaria falar de tarefas removidas, mas é conteúdo do Moodle em disco (ADR-0003).
- Guardar no chaveiro do sistema: serve para segredos pequenos, não para uma tabela de datas.

## Consequências
- Bom: detecta adiamentos, antecipações e atividades novas sem reler tudo; nenhum conteúdo do Moodle fica em disco.
- Ruim / a acompanhar: o estado é por computador (outro computador começa uma referência nova); `moodle-mcp sair` não apaga o arquivo, que só tem ids e datas e é separado por aluno; uma tarefa removida não tem nome; só vale para o prazo oficial das tarefas (`mod_assign_get_assignments`), sem prorrogações individuais.

## Fontes
- [ADR-0003](0003-material-dos-professores-lido-sob-demanda-sem-copia.md) e [ADR-0004](0004-so-dados-do-proprio-aluno.md)
- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/)
