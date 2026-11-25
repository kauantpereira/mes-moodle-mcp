# Instalar no Gemini CLI

> Guia (Diátaxis): passos para quem já sabe o que quer.

Pré-requisitos: [uv](https://docs.astral.sh/uv/) instalado e o comando `uv` disponível no `PATH` de quem inicia o Gemini CLI, e o `git` autenticado no GitHub com acesso ao repositório (por exemplo, com `gh auth login`).

```bash
git clone https://github.com/kauantpereira/mes-moodle-mcp
gemini extensions install ./mes-moodle-mcp
```

Enquanto o repositório for privado, **a instalação direta pela URL** (`gemini extensions install https://github.com/...`) **não funciona**: o clone feito pelo Gemini CLI não usa as suas credenciais do GitHub, mesmo com o `git` autenticado. Por isso o guia clona primeiro e instala a partir da pasta. Os passos foram testados com o Gemini CLI 0.58.0.

O Gemini faz três perguntas antes de instalar; responda `y`:

1. se você confia na pasta da extensão (ele pergunta porque o repositório traz um `.gemini/settings.json`);
2. se confia no diretório em que você está;
3. se quer continuar, depois de mostrar as três skills e o servidor que serão instalados, com o aviso sobre extensões de terceiros.

A opção `--consent` pula as duas últimas, mas não a primeira.

Para conferir:

```bash
gemini extensions list   # moodle-mcp (0.1.0), habilitada, com o servidor `moodle` e as 3 skills
gemini mcp list          # ✓ moodle (from moodle-mcp)
```

As skills são `organizar-semana`, `novidades-da-faculdade` e `regras-de-ia-da-disciplina`. O servidor roda a partir da cópia da extensão, com `uv run`; na primeira vez, o `uv` baixa as dependências, o que leva alguns instantes.

O Gemini **não pergunta** na instalação onde guardar os prazos: essa opção (`destino_calendario`) existe só no plugin do Claude. Com o Gemini, diga o destino na conversa, ou a skill usa um arquivo `.ics`, um checklist em Markdown ou o resumo no chat. O endereço do Moodle também não é pedido: na UFMG vale o semestre atual ([configuração](../referencia/configuracao.md)).

## Outro Moodle, que não seja o da UFMG

A extensão não define variáveis de ambiente para o servidor. Para apontar outro Moodle, registre o servidor à parte, sem a extensão (só as tools, sem as skills):

```bash
gemini mcp add -s user -e MOODLE_URL=https://seu.moodle.edu moodle uvx -- --from git+https://github.com/kauantpereira/mes-moodle-mcp moodle-mcp
```

Se já instalou a extensão, remova-a antes (veja abaixo), para não ficarem dois servidores com o mesmo nome `moodle`. Esse servidor usa `git+https`, então também precisa do `git` autenticado enquanto o repositório for privado.

## Remover

```bash
gemini extensions uninstall moodle-mcp
```

Se algo não funcionar, veja [solução de problemas](solucao-de-problemas.md).
