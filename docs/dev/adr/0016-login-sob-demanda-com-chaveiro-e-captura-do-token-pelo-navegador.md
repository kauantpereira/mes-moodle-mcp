---
status: accepted
date: 2026-11-24
decision-makers: grupo G15
---
# ADR-0016: Login sob demanda, token no chaveiro e captura do token pelo navegador

Complementa o [ADR-0002](0002-login-pelo-fluxo-oficial-do-app-e-token-individual.md) (como o token é obtido) e segue o [ADR-0009](0009-perfis-de-instituicao-isolados-e-reversiveis.md) (o que é de instituição fica no perfil).

## Contexto e problema
O servidor roda por stdio dentro do Claude Code / Claude Desktop. Não há tela própria nem login do MCP para stdio: o botão Reconnect do `/mcp` só reinicia o processo. O login leva minutos (o aluno passa pelo SSO), a senha e o token não podem passar pelo chat nem pelo modelo, e o aluno não deve precisar de terminal no caso comum. Na UFMG o login é por SSO; num Moodle local, por usuário e senha.

## Decisão
1. **Login sob demanda, em 3 peças.** (a) A primeira tool chamada sem token faz o login e continua a resposta (`nucleo.chamar`; um login só, mesmo com tools em paralelo). (b) A tool `entrar` refaz o login: troca de conta ou token expirado/revogado. (c) Reserva: login manual pelo fluxo do app, em que o aluno abre o `launch.php`, copia o `moodlemobile://token=...` e cola no terminal (`moodle-mcp entrar --manual`). Nada abre na inicialização do servidor; o mesmo fluxo vale para Claude Code e Claude Desktop.
2. **Token no chaveiro do sistema** (`keyring`), com a URL base do Moodle como chave. `MOODLE_TOKEN` continua tendo prioridade (provisório, desenvolvimento). Sem chaveiro (ex.: Linux sem Secret Service), o token fica só na memória do processo e o aluno é avisado. Antes de guardar, o núcleo confere o token com `core_webservice_get_site_info`; token recusado não é guardado.
3. **Quem escolhe o método:** `perfil_para(url).login`, se o perfil tiver um; senão `login.login_generico`. Contrato: `async login(base_url, interacao) -> token`, levantando `LoginFalhou` com mensagem segura. O genérico só funciona no terminal: pergunta ao aluno se entra com **senha** (`login/token.php`, serviço `moodle_mobile_app`) ou pelo **fluxo do app** (login manual). Ele não adivinha o tipo de login do site: isso exigiria chamar `tool_mobile_get_public_config` pelo AJAX sem token, fora do cliente e da lista de funções; fica como melhoria futura.
4. **Senha:** pedida só no terminal (`moodle-mcp entrar`, lida sem eco), enviada só ao `login/token.php` por HTTPS (HTTP só em localhost, a mesma regra `_url_segura` do cliente), sem seguir redirecionamentos; nunca guardada nem registrada. `login/token.php` não é função de web service e não entra em `FUNCOES_PERMITIDAS`. Erros viram mensagens fixas por `errorcode`, sem senha, token, URL ou texto do Moodle.
5. **Partes genéricas do fluxo do app no núcleo** (`login.py`): montar a URL do `launch.php` com `passport` aleatório e decodificar/validar o `moodlemobile://token=...` (assinatura md5(wwwroot + passport)). É API padrão do Moodle, igual em qualquer instituição.
6. **Captura automática do SSO com Playwright** (dependência normal do `pyproject.toml`; o `uv` instala no primeiro uso), entregue junto com o perfil que a usa (perfil `ufmg`, #23). Ordem: Chrome instalado (`channel="chrome"`) → Edge instalado (`channel="msedge"`) → Chromium do Playwright (avisar do download de ~150 MB, uma vez) → login manual. A janela abre, o aluno faz o SSO e ela fecha sozinha ao capturar o `moodlemobile://token=...`.
7. **Nada é perguntado pelo cliente MCP (sem elicitation).** Pelo chat, o servidor só manda avisos de progresso; o único login que roda ali é o que abre o navegador (perfil com SSO, item 6). Quando o login precisa de uma resposta do aluno (escolher o método, senha, link do login manual), a tool responde com o comando de terminal `moodle-mcp entrar` (ou `--manual`, para colar o link), que lê senha e link sem eco e guarda no mesmo chaveiro. Motivos: (a) a especificação MCP desaconselha pedir dado sensível por formulário, e o link do login manual carrega o token; (b) o SDK `mcp` 2.3 só pede formulário no meio da tool em protocolo até 2025-11-25 (a partir de 2026-07-28 a pergunta vira `InputRequiredResult`, com a tool chamada de novo a cada resposta), então o formulário dependeria da versão negociada pelo cliente; (c) o público é a UFMG, cujo caminho normal é o navegador, e o terminal é só a reserva.
8. **Tempo de login.** Claude Code: `MCP_TOOL_TIMEOUT` padrão de ~28 h e, para stdio, timeout por inatividade de 30 min (`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`), que notificações de progresso renovam. O login espera no máximo 10 min e manda progresso enquanto espera o navegador.

## Opções consideradas
- **Escolhida:** a decisão acima.
- CDP escrito à mão (abrir o Chrome com `--remote-debugging` e ler a rede sem dependência): código novo sem teste real e pipes frágeis no Windows.
- Registrar o esquema `moodlemobile://` no sistema: o navegador mostra diálogo, a aba não fecha e conflita com o app desktop do Moodle.
- Navegador embutido do cliente (Claude Desktop): inacessível ao MCP, e o token passaria pelo modelo.
- MCP remoto com OAuth: viola os ADRs 0002/0004/0007; um servidor nosso guardaria tokens de alunos.
- Login por QR code do app: depende de a DTI habilitar e configurar.
- Senha e link do login manual por formulário do cliente MCP (elicitation de form): depende da versão do protocolo negociada pelo cliente e contraria a recomendação da especificação MCP para dado sensível. Descartada em 24/11/2026, depois da primeira versão deste ADR.
- Senha por elicitation de URL (página local que recebe a senha): mais aderente à recomendação do MCP de não pedir dado sensível em formulário, mas exige um servidor HTTP local; a senha só é usada em Moodle sem SSO (local/dev), e o formulário vai para o cliente, não para o modelo.
- Abrir o login na inicialização do servidor: abriria janelas sem o aluno pedir e travaria o handshake (`MCP_TIMEOUT` de 30 s).

## Consequências
- Bom: o aluno instala, pergunta e o login aparece quando precisa; senha e token nunca passam pelo chat; reverter o perfil `ufmg` deixa o login genérico (senha/manual) funcionando.
- Bom: o mesmo código serve ao servidor e ao terminal (`Interacao`: avisos pelo MCP, perguntas só no terminal); não depende da versão do protocolo MCP nem de suporte a elicitation.
- Ruim / a acompanhar: Moodle sem perfil (login por senha) e o login manual exigem abrir o terminal; aceitável porque o público é a UFMG, que usa o navegador.
- Ruim / a acompanhar: Playwright aumenta a instalação; o Chromium só é baixado se não houver Chrome nem Edge.

## Fontes
- [Moodle — login/token.php e serviço moodle_mobile_app](https://docs.moodle.org/dev/Creating_a_web_service_client) e [Moodle app — launch.php](https://moodledev.io/general/app/development/setup)
- [Especificação MCP — elicitation](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation) (form e URL; dado sensível só por URL), motivo de não usar formulário
- [Claude Code — MCP](https://code.claude.com/docs/en/mcp) (elicitation, limites de tempo das tools) e [variáveis de ambiente](https://code.claude.com/docs/en/env-vars) (`MCP_TOOL_TIMEOUT`, `MCP_TIMEOUT`)
- SDK `mcp` 2.3: `Context.elicit`, `mcp.server.mcpserver.resolve` (MRTR a partir de 2026-07-28)
- [keyring](https://pypi.org/project/keyring/), [Playwright para Python](https://playwright.dev/python/)
- Código da demo (`auth.py`), testado contra o Moodle real
