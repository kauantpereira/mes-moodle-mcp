# Configuração

| Opção | Descrição | Padrão |
|---|---|---|
| `destino_calendario` | `google`, `outlook`, `notion`, `todoist`, `obsidian`, `ics` ou `nenhum` | `google` |
| `horario_rito` | Horário da rotina diária (HH:MM) | `07:00` |

## Endereço do Moodle e semestre

O plugin não pede o endereço do Moodle (ADR-0017):

- **Instituição com perfil** (ex.: UFMG): o perfil monta o endereço do semestre atual sozinho (`virtual.ufmg.br/20262` no 2º semestre de 2026).
  - Para outro semestre numa consulta, peça ao agente; as tools aceitam o parâmetro `semestre`.
  - Para a conversa toda, use a tool [`usar_semestre`](tools.md#usar_semestre).
- **Outro Moodle**, ou para fixar um endereço: defina a variável `MOODLE_URL` no ambiente que inicia o servidor. Ela tem prioridade sobre o perfil.
  - No Claude Code: `env` no `.mcp.json`/`claude mcp add -e MOODLE_URL=...`.
  - No Codex: `codex mcp add ... --env MOODLE_URL=...`.
  - No Claude Desktop (chat): `env` no `claude_desktop_config.json`.

Cada semestre é um Moodle separado, com login e token próprios: o primeiro acesso a um semestre abre o login daquele Moodle.

## Login e token

Não há opção de login: na primeira pergunta sem token, o servidor abre o login sozinho (ver a tool [`entrar`](tools.md#entrar)). O token fica no **chaveiro do sistema** (Keychain no macOS, Cofre de Credenciais no Windows, Secret Service no Linux), com o endereço do Moodle como chave. A senha nunca é guardada.

### Pelo terminal

Senha e login manual são só no terminal (o servidor não pergunta nada pelo chat):

```bash
uvx --from git+https://github.com/kauantpereira/mes-moodle-mcp moodle-mcp entrar
```

`--manual` pula o navegador automático: mostra o link do fluxo do app, você faz o login no seu navegador e cola o `moodlemobile://token=...` (não aparece na tela). `moodle-mcp sair` apaga o token do chaveiro. Sem opções, vale o mesmo endereço do servidor (`MOODLE_URL` ou o semestre atual do perfil); `--semestre 2026.1` escolhe outro semestre e `--url` outro Moodle.

### `MOODLE_TOKEN` (provisório, desenvolvimento)

Se `MOODLE_TOKEN` estiver definida no ambiente do processo que inicia o servidor MCP, ela tem prioridade sobre o chaveiro e a tool `entrar` não troca de conta. Não é uma opção do manifesto do plugin. O token é sensível: não o coloque em arquivos versionados, não o registre em logs e não o compartilhe.
