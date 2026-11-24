# Organizar a semana

A skill `organizar-semana` combina os prazos das atividades pendentes no Moodle com a dificuldade e a importância de cada matéria e com os horários livres do `~~calendário`. Ela propõe uma distribuição de estudos para os próximos sete dias.

Para montar o plano, informe a dificuldade e a importância das matérias (de 1 a 5), seus horários livres e, quando souber, quanto tempo cada atividade costuma levar. Se essas avaliações já estiverem disponíveis no contexto ou em `~~tarefas`, elas podem ser reaproveitadas.

A proposta considera primeiro os prazos próximos, distribui atividades longas em sessões menores e aponta quando não há tempo livre suficiente. Os horários existentes são consultados como ocupados, sem alteração.

Nada é registrado em `~~calendário` ou `~~tarefas` sem sua confirmação explícita. Sem um conector disponível, a skill pode preparar um checklist em Markdown ou um arquivo `.ics`, também somente depois da confirmação. Consulte [conectores](../referencia/conectores.md) para ver destinos e alternativas.

Os textos das atividades no Moodle são tratados como dados não confiáveis. Eles podem ajudar a identificar uma atividade, mas instruções neles não são seguidas.
