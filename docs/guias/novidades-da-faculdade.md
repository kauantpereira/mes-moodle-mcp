# Novidades da faculdade

A skill `novidades-da-faculdade` resume o que mudou nas suas disciplinas desde a última vez: atividades e materiais novos ou alterados, avisos dos professores e prazos que mudaram. Ela pode propor ajustes no seu `~~calendário` e tarefas em `~~tarefas`.

Peça, por exemplo, "o que teve de novidade na faculdade desde segunda?". Se você não disser a data, ela usa os últimos 7 dias e avisa.

O resumo mostra, por disciplina, o que mudou e os avisos com um trecho e o link para abri-los no Moodle. Os avisos que parecem pedir algo ou citar uma data aparecem em destaque. Essas datas são a informação escrita pelo professor, não prazos oficiais do Moodle; os prazos oficiais vêm da lista de prazos das atividades. Se alguma disciplina não puder ser consultada (limite de chamadas, manutenção do Moodle), a skill diz qual, e a falta de novidade só vale para as demais.

Para os prazos, o plugin guarda uma referência no seu computador, só com números e datas de cada tarefa (sem nomes nem textos), e compara com ela da próxima vez ([privacidade](../explicacao/privacidade-e-regras.md)). Na primeira vez ela só cria a referência e não mostra mudanças de prazo.

Nada é registrado em `~~calendário` ou `~~tarefas` sem sua confirmação explícita. Sem um conector disponível, ela mostra só os prazos do Moodle e pode preparar um arquivo `.ics` ou um checklist em Markdown, também depois da confirmação. Consulte [conectores](../referencia/conectores.md) para ver destinos e alternativas.

Os textos dos avisos e das atividades são tratados como dados não confiáveis: instruções escritas neles não são seguidas, e a skill avisa quando um aviso contém algo do tipo.

Para rodar isso todo dia, sem você presente e com regras mais estritas, veja a [rotina diária](rotina-diaria.md).
