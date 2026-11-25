# Primeiros passos

> Tutorial (Diátaxis): uma experiência guiada, do zero ao primeiro resultado. Você vai conectar o seu Moodle, ver seus prazos, conferir a conexão e consultar outro semestre.

Antes de começar, instale o plugin no seu agente ([onde funciona e como instalar](../guias/instalar.md)). Você **não** precisa informar o endereço do Moodle: na UFMG, o plugin usa o semestre atual sozinho. Para outra instituição, veja a [configuração](../referencia/configuracao.md).

## 1. Faça a primeira pergunta

Abra o seu agente e escreva, com as suas palavras, algo como:

> Quais atividades eu tenho para entregar nesta semana?

Como é a primeira vez, o plugin ainda não tem acesso ao seu Moodle. **Ele abre o login sozinho**, no meio da resposta; você não precisa chamar nada antes.

## 2. Entre com a sua conta

Uma janela do navegador se abre no login da instituição (na UFMG, o minhaUFMG). Entre como você sempre entra no Moodle.

- Sua **senha fica só no navegador**: ela nunca passa pelo chat nem pelo servidor.
- Quando você terminar, a janela mostra "Login concluído" e **fecha sozinha**. Volte ao agente: ele continua a resposta.
- O acesso fica guardado no chaveiro do seu computador. Nas próximas perguntas, você não entra de novo, até o acesso expirar.
- Se você não tem o Chrome nem o Edge, o plugin baixa um navegador uma única vez (cerca de 150 MB) e avisa antes.

Se a janela não abrir, ou se o agente responder com um comando de terminal, veja a [solução de problemas](../guias/solucao-de-problemas.md#login).

## 3. Leia a resposta

O agente lista as atividades com prazo nos próximos sete dias: a atividade, a disciplina, o prazo e o estado da entrega. As que você já enviou **não aparecem**. Os nomes vêm do Moodle e são tratados como dados: instruções escritas neles não são seguidas.

Peça mais detalhes quando quiser, por exemplo: "me conta o enunciado da Lista 3" ou "como estão minhas notas em Cálculo?".

## 4. Confira a conexão

Se alguma consulta falhar, ou você quiser saber em qual Moodle está, pergunte:

> Estou conectado? Em qual Moodle?

O agente usa a tool `quem_sou_eu` e mostra o seu nome, o endereço do Moodle e a versão. É o primeiro passo para entender por que algo não funcionou.

## 5. Mude de semestre

Na UFMG, cada semestre é um Moodle separado. Por padrão, vale o semestre atual. Para olhar outro, escreva:

> Mostra meus prazos do semestre passado.

O agente consulta o outro semestre só nessa pergunta. Para a conversa inteira ficar em outro semestre, peça:

> Vamos usar o semestre 2026.1 nesta conversa.

Ele usa a tool `usar_semestre`, que responde com o Moodle escolhido (por exemplo, `virtual.ufmg.br/20261`). Isso vale até o servidor reiniciar; para voltar ao atual, peça o semestre atual.

Na primeira vez que você consulta um semestre, o login abre de novo, porque cada semestre tem o seu próprio acesso.

## Próximos passos

- Montar um plano de estudos: [organizar a semana](../guias/organizar-semana.md).
- Escolher onde guardar prazos e planos: [escolher onde guardar os prazos](../guias/escolher-onde-guardar-prazos.md).
- Ver o que cada tool faz e o tamanho das respostas: [referência das tools](../referencia/tools.md).
- Entender por que seus dados ficam só com você: [privacidade e regras](../explicacao/privacidade-e-regras.md).
