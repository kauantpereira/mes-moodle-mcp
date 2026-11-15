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

## Fontes
- [Termo de Compromisso de Uso dos Recursos de TI da UFMG](https://sistemas.ufmg.br/termos-de-uso) (versão de 20/10/2025), itens 3.3 e 3.6
- [Moodle — External services API](https://moodledev.io/docs/apis/subsystems/external) e [Moodle app — fluxo de login](https://moodledev.io/general/app/development/setup) e o código da demo (`auth.py`)
- [tosuki/moodle-mcp](https://github.com/tosuki/moodle-mcp) (alternativa por cookie, descartada)
