# Configuração

| Opção | Descrição | Padrão |
|---|---|---|
| `moodle_url` | Endereço do Moodle da sua instituição | — (obrigatório) |
| `destino_calendario` | `google`, `outlook`, `notion`, `todoist`, `obsidian`, `ics` ou `nenhum` | `google` |
| `horario_rito` | Horário da rotina diária (HH:MM) | `07:00` |

## Token do Moodle (provisório)

Para usar o cliente Moodle no estado atual, defina `MOODLE_TOKEN` no ambiente do processo que inicia o servidor MCP. O núcleo lê essa variável diretamente do ambiente; ela não é uma opção configurada no manifesto do plugin.

Este mecanismo é provisório, usado enquanto o fluxo de login e o armazenamento do token no chaveiro do sistema, previstos no ADR-0002, não estão implementados. O token é sensível: não o coloque em arquivos versionados, não o registre em logs e não o compartilhe.
