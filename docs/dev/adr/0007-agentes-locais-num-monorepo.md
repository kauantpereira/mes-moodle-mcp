---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0007: Agentes locais num monorepo

## Contexto e problema
Apps web (claude.ai, ChatGPT, app Gemini) só aceitam MCP remoto, o que exigiria custodiar tokens de terceiros.

## Decisão
Atender Claude Code/Desktop, OpenAI Codex e Gemini CLI com o MCP local (stdio), num monorepo com um manifesto por plataforma e skills compartilhadas (padrão Agent Skills).

## Opções consideradas
- **Escolhida:** a decisão acima
- Servidor remoto hospedado
- Um repositório por plataforma

## Consequências
- Bom: Sem custódia de credenciais; um único código.
- Ruim / a acompanhar: Apps web ficam como trabalho futuro, só com autorização ou hospedagem institucional.
