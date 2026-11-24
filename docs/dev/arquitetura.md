# Arquitetura

```
agente (Claude Code / Codex / Gemini CLI)
  ├── skills/ (SKILL.md)            como usar: rotinas e regras
  └── MCP local (stdio) ── src/moodle_mcp/
        ├── núcleo: cliente da API REST do Moodle, tools, avisos, limite de chamadas
        └── perfis/<instituicao>.py  URL, login e regras específicas (isolado; ADR-0009)
              └── API de web services do Moodle (só funções get)
```

## Núcleo
- `client.py`: cliente da API REST. Recebe só URL + token. Só chama funções explicitamente listadas em `FUNCOES_PERMITIDAS`; funções fora da lista são barradas antes da rede. O token vai no corpo do POST. Downloads usam GET separado, limitado ao host do Moodle, com token apenas na requisição. Mensagens brutas, corpos inválidos e detalhes de transporte são descartados.
- `nucleo.py`: ponto usado pelas tools. `cliente()` reutiliza um cliente por processo. `obter_token` lê `MOODLE_TOKEN` (provisório, tem prioridade) ou o chaveiro. Sem token, `chamar()` faz o login antes (login sob demanda, um só mesmo com tools em paralelo) e continua; `entrar()` refaz o login, confere o token com `core_webservice_get_site_info`, guarda no chaveiro e troca o cliente (mantendo o limite de chamadas). O método é `perfil_para(url).login` ou o genérico. `chamar()` expõe mensagens genéricas sem conteúdo bruto do Moodle, URL ou detalhes de exceção. O transporte HTTP é encerrado por `aclose()` no cliente.
- `login.py`: login genérico (ADR-0016), só API padrão do Moodle. Senha por `login/token.php` (serviço `moodle_mobile_app`, só HTTPS, senha nunca guardada; não é função de web service, fica fora de `FUNCOES_PERMITIDAS`) e fluxo do app (`launch.php` com `passport`, validação do `moodlemobile://token=...`, login manual). Conversa com o aluno por uma `Interacao`: `InteracaoMCP` (formulário por elicitation, só em protocolo MCP até 2025-11-25) ou terminal. Contrato de `Perfil.login`: `async (base_url, interacao) -> token`, levantando `LoginFalhou`.
- `chaveiro.py`: token no chaveiro do sistema (`keyring`), chave = URL base do Moodle; sem chaveiro, `ler`/`salvar` não levantam erro e o token fica só na memória.
- `server.py`: `ServidorMoodle` (um `MCPServer` que passa o contexto da tool ao núcleo, para o login sob demanda pedir formulário) e a tool `entrar`.
- `cli.py`: `moodle-mcp entrar` / `moodle-mcp sair` no terminal, para clientes sem formulário. Mesmo login e mesmo chaveiro do servidor.
- `limite.py`: contador e limite de chamadas (ADR-0005). Janelas deslizantes, padrão de 60 chamadas por minuto e 600 por hora; `call()` e `baixar()` registram antes da rede, e a recusa vira `ToolError` com o tempo de espera. O contador é por processo: sessões simultâneas contam separado.

## Perfis (`perfis/`)
- `perfis/__init__.py`: contrato `Perfil` (hosts, fuso, janelas de manutenção, login próprio no contrato de `login.py`) e `perfil_para(base_url)`. Cada instituição é um módulo `perfis/<inst>.py` com `PERFIL = Perfil(...)`, descoberto sozinho; sem módulo (ou com o PR revertido), vale o `GENERICO`. O núcleo nunca importa um perfil pelo nome (ADR-0009).

Decisões: ver [adr/](adr/).
