# Project Context — Agentic Personal AI Assistant

## Goal
Build a privacy-first AI assistant that extracts schedule context from Gmail,
checks the weather via OpenWeatherMap, and delivers a morning brief with
actionable recommendations (outfit, commute, prep reminders).

## Architecture
- **Rust core** — policy enforcement, tool registry, scheduler, connectors.
- **Python orchestration** — LLM planning (OpenAI API later), prompt/template layer, tool routing.
- **Postgres (Neon)** — user preferences, memories, schedule cache, weather cache, audit logs (pgvector in v2).

## Version 1 Scope
- Email schedule extraction (Gmail read-only)
- Weather-aware suggestions
- User preferences & memories stored in Postgres
- On-demand + scheduled morning brief
- Read-only external access in v1 (no sending email / no destructive actions)
- Audit logging

## What’s Done
- Six design docs in `/docs`:
  PRD, system architecture, data & memory design, tool/skills contract,
  security & privacy spec, test plan.
- Repo bootstrapped: `README.md`, `.gitignore`, `.env.example`, `PROJECT_CONTEXT.md`
- **Rust core scaffold**: CLI health + tool registry + policy gate stubs
- **Python orchestration scaffold**: FastAPI `/healthz` + `/plan` mock tool planner
- **Neon Postgres connected** (DATABASE_URL from repo-root `.env`)
- **Memory v1 complete**:
  - `POST /memory/store`
  - `GET /memory/{memory_key}`
  - DB upsert + integration tests
- **Weather v1 complete**:
  - `GET /weather?lat=&lon=`
  - deterministic advice engine (Cold/Cool/Mild/Warm/Hot + rain/wind overrides)
  - Postgres caching (15-min TTL)
  - advice unit tests
- **Smoke testing added**: `./scripts/smoke_test.sh` (schema apply + API up + curl store/get + PASS/FAIL)

## Running Locally (current)
**Terminal 1 (Python API)**
- `cd ai-orchestration-py`
- `source .venv/bin/activate`
- `uvicorn src.orchestrator.app:app --reload --port 8001 --reload-exclude ".venv/*"`

**Terminal 2 (curl tests)**
- `curl http://localhost:8001/healthz`
- `curl "http://localhost:8001/weather?lat=...&lon=..."`
- `curl -X POST http://localhost:8001/memory/store ...`

**End-to-end**
- `./scripts/smoke_test.sh`

## What’s Next (next milestone)
1. **Gmail OAuth setup (Google Cloud)**:
   - Create OAuth client (Desktop/Web)
   - Add redirect URI for local callback
   - Store credentials locally in `.env` (never commit)
2. **Token storage (v1)**:
   - Store refresh token securely (v1: in DB; v1.1+: encrypt at rest)
3. **Gmail read-only connector (Python first)**:
   - Implement Gmail auth + minimal email fetch
   - Add tool: `email_event_reader` returning extracted schedule candidates
4. **Schedule extraction v1**:
   - Parse simple patterns (dates/times/locations) from emails
   - Store extracted events in `events` table
5. **Morning brief v1 (on-demand)**:
   - Combine: next event + weather advice + key preferences
   - Add `POST /brief` or CLI trigger (Python first, Rust later)
6. (Optional hardening) Improve `.env` docs:
   - remind quoting DATABASE_URL if it contains `&`

## How to Continue in a New Chat
Paste this file and add:

Current step: <number from "What’s Next">
Status: <what you tried / what worked>
Error (if any): <paste error or "none">