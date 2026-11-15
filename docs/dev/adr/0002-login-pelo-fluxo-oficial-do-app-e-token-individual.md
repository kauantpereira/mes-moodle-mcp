---
status: accepted
date: 2026-11-15
decision-makers: grupo G15
---
# ADR-0002: Login pelo fluxo oficial do app e token individual

## Contexto e problema
Itens 3.3 (conta individual) e 3.6 (responsabilidade) do Termo; a UFMG usa SSO (minhaUFMG).

## Decisão
Obter o token pelo serviço `moodle_mobile_app` (fluxo `admin/tool/mobile/launch.php`), com login no navegador. Token guardado no chaveiro do sistema; senha nunca vista pelo servidor.

## Opções consideradas
- **Escolhida:** a decisão acima
- Usuário e senha via `login/token.php` (não funciona com SSO)
- Cookie de sessão + chamadas AJAX internas (mais próximo de raspagem)

## Consequências
- Bom: Funciona com SSO e usa a API pública que o próprio app oficial usa.
- Ruim / a acompanhar: A DTI pode preferir outro serviço; a mudança fica restrita ao perfil da instituição (ADR-0009).
