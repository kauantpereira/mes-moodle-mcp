# Solução de problemas

> Guia. Sintoma → causa → o que fazer. A preencher com os erros reais da demo (token expirado, Moodle fora do ar, limite de chamadas).

## Um material ou disciplina nova ainda não aparece
- **Causa:** a lista de disciplinas e o conteúdo de cada disciplina ficam guardados por até 5 minutos, para não sobrecarregar o Moodle da instituição.
- **O que fazer:** espere alguns minutos e peça de novo. Prazos, entregas e notas não passam por esse cache.

## "O Moodle está em manutenção"
- **Causa:** algumas instituições reservam um horário fixo para manutenção do Moodle (ex.: backup de madrugada). Nesse horário o plugin não chama o Moodle, para não atrapalhar a manutenção.
- **O que fazer:** tente de novo a partir do horário indicado na mensagem. O que foi consultado há poucos minutos (lista de disciplinas, conteúdo) ainda pode aparecer, porque vem do cache.
