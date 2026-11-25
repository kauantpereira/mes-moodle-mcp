# Instalar no OpenAI Codex

> Guia (Diátaxis): passos para quem já sabe o que quer.

Pré-requisitos: [uv](https://docs.astral.sh/uv/) instalado e o comando `uv` disponível no `PATH` de quem inicia o Codex. Enquanto o repositório for privado, só quem tem acesso a ele consegue instalar: o `git` da sua máquina precisa estar autenticado no GitHub (por exemplo, com `gh auth login`).

```bash
codex plugin marketplace add kauantpereira/mes-moodle-mcp
codex plugin add moodle-mcp@mes-moodle-mcp
```

O primeiro comando registra o repositório como fonte de plugins; o segundo instala e habilita o plugin. Os dois foram testados com o Codex CLI 0.144.6.

Para conferir:

```bash
codex plugin list      # moodle-mcp@mes-moodle-mcp: installed, enabled
codex mcp get moodle   # servidor `moodle`, comando `uv run moodle-mcp`
```

O plugin traz as três skills (`moodle-mcp:organizar-semana`, `moodle-mcp:novidades-da-faculdade` e `moodle-mcp:regras-de-ia-da-disciplina`) e o servidor das tools. O servidor roda a partir da cópia do plugin que o Codex guarda, com `uv run`; na primeira vez, o `uv` baixa as dependências, o que leva alguns instantes.

O Codex **não pergunta** na instalação onde guardar os prazos: essa opção (`destino_calendario`) existe só no plugin do Claude. Com o Codex, diga o destino na conversa, ou a skill usa um arquivo `.ics`, um checklist em Markdown ou o resumo no chat. O endereço do Moodle também não é pedido: na UFMG vale o semestre atual ([configuração](../referencia/configuracao.md)).

## Outro Moodle, que não seja o da UFMG

O plugin não define variáveis de ambiente para o servidor. Para apontar outro Moodle, registre o servidor à parte, sem o plugin (só as tools, sem as skills):

```bash
codex mcp add moodle --env MOODLE_URL=https://seu.moodle.edu -- uvx --from git+https://github.com/kauantpereira/mes-moodle-mcp moodle-mcp
```

Se já instalou o plugin, remova-o antes (veja abaixo), para não ficarem dois servidores com o mesmo nome `moodle`.

## Remover

```bash
codex plugin remove moodle-mcp@mes-moodle-mcp
```

Se algo não funcionar, veja [solução de problemas](solucao-de-problemas.md).
