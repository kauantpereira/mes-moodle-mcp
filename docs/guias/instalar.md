# Instalar: onde funciona

> Guia (Diátaxis): para escolher o seu agente e ir ao passo a passo.

O plugin funciona onde o agente consegue **iniciar um servidor MCP local** na sua máquina ([ADR-0007](../dev/adr/0007-agentes-locais-num-monorepo.md)). O servidor roda com o [uv](https://docs.astral.sh/uv/), que precisa estar instalado e no `PATH` de quem inicia o agente.

> **Repositório privado.** Enquanto ele não for público, só quem tem acesso ao repositório consegue instalar, e o `git` da sua máquina precisa estar autenticado no GitHub (por exemplo, com `gh auth login`). Cada guia mostra como isso afeta o comando.

## Plugin completo (skills e tools)

Instala as três skills (`organizar-semana`, `novidades-da-faculdade` e `regras-de-ia-da-disciplina`) e o servidor MCP com as tools.

| Agente | Skills | Servidor MCP | Onde guardar os prazos | Guia |
|---|---|---|---|---|
| Claude Desktop (Cowork, local) e Claude Code | sim | sim | escolhido na instalação (`destino_calendario`) | [Claude](instalar-no-claude.md) |
| OpenAI Codex | sim | sim | dito na conversa (a instalação não pergunta) | [Codex](instalar-no-codex.md) |
| Gemini CLI | sim | sim | dito na conversa (a instalação não pergunta) | [Gemini CLI](instalar-no-gemini.md) |

Quando a instalação não pergunta, as skills usam o destino que você disser na conversa; sem conector, caem para um arquivo `.ics`, um checklist em Markdown ou o resumo no chat ([escolher onde guardar os prazos](escolher-onde-guardar-prazos.md)).

## Só as tools (sem skills)

| Agente | Skills | Servidor MCP | Como |
|---|---|---|---|
| Chat do Claude Desktop | não | sim | Registre o servidor no `claude_desktop_config.json` ([configuração](../referencia/configuracao.md)) |

Você tem as tools (prazos, notas, enunciados, conexão), mas não as rotinas que as skills trazem.

## Não funciona

| Onde | Por quê |
|---|---|
| claude.ai no navegador | Só aceita servidor MCP **remoto**; este plugin é local ([ADR-0007](../dev/adr/0007-agentes-locais-num-monorepo.md)) |
| ChatGPT | Só aceita MCP remoto |
| App Gemini | Só aceita MCP remoto |

Um servidor remoto exigiria hospedar e guardar o token de cada aluno, o que o projeto evita de propósito (sem custódia de credenciais).

## Depois de instalar

Siga o [tutorial de primeiros passos](../tutorial/primeiros-passos.md). Para trocar o endereço do Moodle ou o semestre, veja a [configuração](../referencia/configuracao.md). Se algo falhar, a [solução de problemas](solucao-de-problemas.md).
