# WoW Companion App

Companion app para jogadores de World of Warcraft focado em tracking semanal multi-char.

## O problema

WoW é um jogo de gestão de checklist semanal (vault, crests, weekly quests, profession knowledge...). Para jogadores com tempo limitado e múltiplos chars, acompanhar o progresso de cada objetivo por char é cognitivamente pesado e não há ferramenta boa que resolva isso.

## Status

🚧 Em desenvolvimento — MVP em construção.

## Stack

- **Backend:** Python + FastAPI
- **Banco de dados:** SQLite (MVP) → Postgres (produção)
- **Frontend:** Next.js + Tailwind + shadcn/ui
- **APIs consumidas:** Battle.net, Raider.io

## Roadmap

- [x] Bloco 1 — Setup de ambiente
- [x] Bloco 2 — Git + GitHub
- [ ] Bloco 3 — Primeira chamada à Battle.net API
- [ ] Bloco 4 — Lógica do Great Vault
- [ ] Bloco 5 — Persistência de snapshots