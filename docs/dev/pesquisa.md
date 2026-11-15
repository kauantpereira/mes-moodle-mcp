# Pesquisa que embasou as decisões

Levantamento feito no planejamento (15/11/2026). As decisões estão em [adr/](adr/); aqui ficam os achados e as fontes.

## Regras institucionais (UFMG)
| Fonte | Achado relevante |
|---|---|
| [Termo de Compromisso de Uso dos Recursos de TI](https://sistemas.ufmg.br/termos-de-uso) (20/10/2025) | 3.3: conta individual, não compartilhável. 3.6: o usuário responde pelo que é feito com a conta. 3.9: robôs/scrapers que autenticam e extraem dados exigem **autorização expressa**; também é infração esgotar recursos e violar propriedade intelectual ou privacidade. |
| [Moodle — Políticas de Uso (DTI)](https://www.ufmg.br/dti/moodle-politicas-de-uso/) | Nada sobre API ou direitos autorais; trata de carga: backup diário 01h30–06h00, uploads até 20 MB, casos especiais via suporte@dti.ufmg.br. |
| [POSIN-UFMG v1.0](https://www.ufmg.br/dti/wp-content/uploads/2022/11/posin.pdf) | Princípios gerais (controle de acesso, confidencialidade); as regras práticas estão no Termo. |
| [Guia de IA da UFMG (ago/2026)](https://www.ufmg.br/ia/wp-content/uploads/2026/08/Guia-de-Inteligencia-Artificial_Principios-e-diretrizes-para-o-uso-responsavel-na-UFMG.pdf) | Recomendação, não resolução. p. 9/18: LGPD, não enviar dados pessoais a IA não preparada. p. 10/23: só humanos são autores. p. 19: discernimento com documentos internos não públicos. p. 23: aluno só usa IA onde o plano de ensino permitir. |
| [Recomendações de uso de IA na UFMG (mai/2026)](https://www.ufmg.br/ia/wp-content/uploads/2026/05/Uso-de-Ferramentas-de-IA-na-UFMG-2.pdf) | Disciplinas devem divulgar riscos (direitos autorais, privacidade) e regras de uso. |

## Boas práticas de MCP
| Fonte | Achado |
|---|---|
| [Anthropic — Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) | Tools orientadas à tarefa; filtros, paginação e corte com padrões sensatos; erros que dizem o que fazer; evals. |
| [Anthropic — Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) | O agente escreve código que chama as tools e filtra fora do contexto; caso relatado de 150 mil → 2 mil tokens. |
| [MCP 2025-06-18](https://dev.to/forgecode/mcp-2025-06-18-spec-update-security-structured-output-elicitation-1pin) e [2025-11-25](https://workos.com/blog/mcp-2025-11-25-spec-update) | Saída estruturada (`outputSchema`), anotações de leitura, elicitation por URL, Tasks. |
| [MCP 2026-07-28 (RC)](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) | Transporte sem sessão, cache com `ttlMs`/`cacheScope`, Tasks como extensão, MCP Apps; Roots, Sampling e Logging deprecados. |

### Medições na demo (Moodle UFMG 4.1, 12 disciplinas)
| O quê | Tamanho |
|---|---|
| Conteúdo de todas as disciplinas | 122.821 caracteres (~35 mil tokens); maior curso: 48.139 |
| Avisos (5 por disciplina) | 16.175 |
| `core_course_get_updates_since`, 7 dias, maior curso | 555 |

## Moodle MCPs open source (só README)
| Projeto | Escreve? | Login | Observação |
|---|---|---|---|
| [Jawadh-Salih/moodle-mcp-server](https://github.com/Jawadh-Salih/moodle-mcp-server) | sim | senha/token/app | sem limite nem economia de tokens |
| [tosuki/moodle-mcp](https://github.com/tosuki/moodle-mcp) | sim | cookie de sessão + AJAX | próximo de raspagem |
| [sonstellar969/open-moodle](https://github.com/sonstellar969/open-moodle) | não | senha/SSO/token | briefing consolidado; índice local com cópia dos materiais |
| [csmediapro/moodle-mcp-server](https://github.com/csmediapro/moodle-mcp-server) | não | token de admin | público: admins |
| [duck-5/moodle-mcp](https://github.com/duck-5/moodle-mcp) | sim | SSO/cookie/token | 27+ tools, cache |

Nenhum trata limite de chamadas, avisos de uso de IA, só dados próprios ou regras institucionais.

## Segurança: injeção de prompt
Texto escrito por pessoas (avisos, enunciados, materiais) pode conter instruções. Mitigações: marcar como dado não confiável em todas as tools; separar texto de terceiros dos metadados; rotinas com o mínimo de permissões (só ajustar eventos existentes); log das mudanças; evals com cliente falso devolvendo avisos maliciosos.

## Distribuição: local × remoto
| Cliente | MCP local (stdio) | MCP remoto | Skills |
|---|---|---|---|
| Claude Code / Desktop | sim | sim | via plugin |
| claude.ai | não | sim | via plugin |
| OpenAI Codex | sim | sim | via plugin |
| ChatGPT (web) | não | sim (Developer Mode, planos pagos) | a confirmar |
| Gemini CLI | sim | sim | via extensão |
| App Gemini | não | sim, mas em out/2026 só EUA, 18+ | a confirmar |

Fontes: [Claude — conectores remotos](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp), [ChatGPT MCP](https://coworker.ai/blog/chatgpt-mcp), [Gemini Apps Help](https://support.google.com/gemini/answer/17209137?hl=en&co=GENIE.Platform%3DDesktop), [Codex — plugins](https://developers.openai.com/plugins/build/plugins.md), [Gemini CLI — extensões](https://google-gemini.github.io/gemini-cli/docs/extensions/).

## Conectores de destino
Oficiais: Google Agenda (conector; servidor próprio do Google em preview), Notion ([MCP oficial](https://github.com/makenotion/notion-mcp-server)), Todoist, Outlook (Microsoft Work IQ Calendar, preview). Sem MCP oficial: Trello, Apple Calendar/CalDAV. Fontes: [ChatForest — calendários](https://chatforest.com/guides/best-calendar-scheduling-mcp-servers/), [ChatForest — produtividade](https://chatforest.com/guides/best-productivity-mcp-servers/), [Reassign](https://reassign.ai/resources/day-planners-with-an-mcp-server).

## Trabalho futuro avaliado
- **Tecnologias:** code execution (alta para análise), cache com TTL (média), elicitation por URL para o login (média); tool search, resources com assinatura, Tasks e MCP Apps (baixa).
- **NotebookLM:** não se conecta a MCP; sem API pública para contas pessoais (só Enterprise); MCPs comunitários automatizam o navegador ([PleasePrompto/notebooklm-mcp](https://github.com/PleasePrompto/notebooklm-mcp), [jacob-bd/notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli)). Todos os caminhos copiam o material dos professores para fora do Moodle (contra o ADR-0003); só com autorização. Fonte: [MCP.Directory](https://mcp.directory/blog/notebooklm-mcp-complete-guide-2026).
- **Apps web:** só com MCP remoto, que exigiria custodiar tokens (ADR-0007); possível se hospedado pela própria instituição.

## GitHub Projects: o que dá para automatizar (15/11/2026)
| O quê | Por API? | Como |
|---|---|---|
| Criar projeto, ligar ao repo | sim | `gh project create`, `gh project link` |
| Campos, opções de Status, iterações (sprints) | sim | GraphQL (`updateProjectV2Field`, `createProjectV2Field`) |
| **Views** (board, tabela, roadmap, com filtro e campos visíveis) | **sim**, desde set/2025 | REST `POST /users/<login>/projectsV2/<n>/views`; testado neste board |
| Automações nativas (item fechado → Done etc.) | **não** | só ler e apagar (`deleteProjectV2Workflow`); ligar é pela interface |
| Copiar um board inteiro | sim | `gh project copy` / `copyProjectV2`: campos, views e automações (menos auto-add); não copia itens nem vínculos |
| Auto-add de issues do repo | não (nativo) | alternativa oficial: action [`actions/add-to-project`](https://github.com/actions/add-to-project) |
| Merge só por squash, apagar branch | sim | `gh api -X PATCH repos/<dono>/<repo>` (aplicado aqui) |

MCPs de terceiros para Projects (ex.: [jersonmartinez/mcp-github-projects](https://github.com/jersonmartinez/mcp-github-projects)) usam a mesma API e têm o mesmo limite nas automações nativas.

Fontes: [changelog da API REST de Projects](https://github.blog/changelog/2025-09-11-a-rest-api-for-github-projects-sub-issues-improvements-and-more/), [REST — views](https://docs.github.com/en/enterprise-server@3.22/rest/projects/views), [GraphQL — Projects](https://docs.github.com/en/graphql/reference/projects), [discussão #153532](https://github.com/orgs/community/discussions/153532), [Gitsu — templates de board](https://gitsu.app/guides/github-project-board-templates).
