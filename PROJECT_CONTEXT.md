# Project Context — Agentic Personal AI Assistant

## Goal

Build a privacy-first AI assistant that extracts schedule context from Gmail,
checks the weather via OpenWeatherMap, and delivers a morning brief with
actionable recommendations (outfit, commute, prep reminders).

## Architecture

- **Rust core** — policy enforcement, tool registry, scheduler, connectors.
- **Python orchestration** — LLM planning (OpenAI API), prompt/template layer.
- **Postgres** — user preferences, schedule cache, audit logs (pgvector in v2).

## Version 1 Scope

Email schedule extraction (Gmail read-only) · weather-aware suggestions ·
user preferences stored in Postgres · on-demand + scheduled morning brief ·
read-only external access · audit logging.

## What's Done

- Six design docs live in `/docs`:
  PRD, system architecture, data & memory design, tool/skills contract,
  security & privacy spec, test plan.
- Repo initialised with README, .gitignore, .env.example, this file.

## What's Next

1. Repo scaffolding — create `rust-core/`, `python-ai/`, `migrations/`, `scripts/`.
2. `.env` setup — copy `.env.example` → `.env`, add real keys locally.
3. Postgres schema — users, preferences, schedule_cache, audit_log tables.
4. Tool skeletons — Gmail connector, weather connector (Rust side).
5. Gmail OAuth — implement OAuth 2.0 flow, token storage.
6. Weather tool — OpenWeatherMap integration.
7. CLI — `brief` command that runs the full morning-brief pipeline.

## How to Continue in a New Chat

Paste this file into the new chat and add:

```
Current step: <number from "What's Next" above>
Error (if any): <paste the error or "none">
```

The assistant will pick up where you left off.
