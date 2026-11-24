# Configuração

| Opção | Descrição | Padrão |
|---|---|---|
| `moodle_url` | Endereço do Moodle da sua instituição | — (obrigatório) |
| `destino_calendario` | `google`, `outlook`, `notion`, `todoist`, `obsidian`, `ics` ou `nenhum` | `google` |
| `horario_rito` | Horário da rotina diária (HH:MM) | `07:00` |

## Login e token

Não há opção de login: na primeira pergunta sem token, o servidor abre o login sozinho (ver a tool [`entrar`](tools.md#entrar)). O token fica no **chaveiro do sistema** (Keychain no macOS, Cofre de Credenciais no Windows, Secret Service no Linux), com o endereço do Moodle como chave. A senha nunca é guardada.

### Pelo terminal

Para clientes MCP que não mostram formulário (elicitation):

```bash
uvx --from git+https://github.com/kauantpereira/mes-moodle-mcp moodle-mcp entrar --url https://moodle.exemplo.edu
```

`moodle-mcp sair --url ...` apaga o token do chaveiro. Sem `--url`, vale a variável `MOODLE_URL`. Use o mesmo endereço configurado no plugin.

### `MOODLE_TOKEN` (provisório, desenvolvimento)

Se `MOODLE_TOKEN` estiver definida no ambiente do processo que inicia o servidor MCP, ela tem prioridade sobre o chaveiro e a tool `entrar` não troca de conta. Não é uma opção do manifesto do plugin. O token é sensível: não o coloque em arquivos versionados, não o registre em logs e não o compartilhe.
