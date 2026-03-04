# AI Orchestration Service

Python-based LLM planning and prompt layer for the Agentic Personal AI Assistant.

## Prerequisites

- Python 3.11+
- A Postgres database (Neon or local). Set `DATABASE_URL` in the **repo-root** `.env`.

## Setup

```bash
cd ai-orchestration-py

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

## Run

The service automatically loads the repo-root `.env` on startup.

```bash
uvicorn src.orchestrator.app:app --reload --port 8001
```

## Endpoints

| Method | Path                     | Description                                      |
|--------|--------------------------|--------------------------------------------------|
| GET    | `/healthz`               | Health check — returns `{"status": "ok"}`         |
| POST   | `/plan`                  | Accepts `PlanRequest`, returns a tool-call plan   |
| POST   | `/memory/store`          | Upsert a memory (key/value) for the default user  |
| GET    | `/memory/{memory_key}`   | Retrieve a memory by key (404 if missing)          |

## Examples

```bash
# Health check
curl -s http://localhost:8001/healthz

# Plan (keyword-based mock planner)
curl -s -X POST http://localhost:8001/plan \
  -H "Content-Type: application/json" \
  -d '{"user_input": "What is my schedule and weather today?"}' | python3 -m json.tool

# Store a memory
curl -s -X POST http://localhost:8001/memory/store \
  -H "Content-Type: application/json" \
  -d '{"memory_key": "home_city", "memory_value": "Denton", "memory_type": "preference"}'

# Retrieve a memory
curl -s http://localhost:8001/memory/home_city | python3 -m json.tool

# Plan with real persistence ("remember" triggers a DB write)
curl -s -X POST http://localhost:8001/plan \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Remember my favorite color is blue"}' | python3 -m json.tool
```

## Tests

Integration tests require a live Postgres database. They skip automatically when
`DATABASE_URL` is not set.

```bash
# Make sure .env exists at the repo root with a valid DATABASE_URL
# (and the schema has been applied: psql "$DATABASE_URL" -f ../database/schema.sql)

pytest tests/ -v
```
