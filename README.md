# Agentic Personal AI Assistant

A privacy-first, agentic AI assistant that reads your email for schedule context,
checks the weather, and delivers a concise morning brief — so you start every day prepared.

---

## Key Features (Version 1)

| Feature | Details |
|---|---|
| **Email-based schedule extraction** | Gmail read-only OAuth; parses calendar invites, deadlines, and reminders |
| **Weather-aware recommendations** | OpenWeatherMap integration; outfit and commute suggestions |
| **Preferences & memory** | Postgres-backed user profile, location, and history |
| **Morning brief workflow** | On-demand CLI command + optional scheduled delivery |
| **Safe by design** | Read-only external access in v1; full audit logging |

---

## Architecture (Option B — Hybrid Rust + Python)

```
┌─────────────────────────────────────────────────┐
│                   CLI / API                     │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│            Rust Assistant Core                  │
│  ┌────────────┬────────────┬──────────────────┐ │
│  │  Policy /  │   Tool     │   Scheduler /    │ │
│  │  Guard     │  Registry  │   Connectors     │ │
│  └────────────┴────────────┴──────────────────┘ │
└────────────────────┬────────────────────────────┘
                     │ FFI / HTTP
┌────────────────────▼────────────────────────────┐
│         Python AI Orchestration                 │
│  ┌────────────────┬───────────────────────────┐ │
│  │  LLM Planner   │   Prompt / Template Layer │ │
│  │  (OpenAI API)  │                           │ │
│  └────────────────┴───────────────────────────┘ │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              Postgres (pgvector later)          │
└─────────────────────────────────────────────────┘
```

**Rust core** — policy enforcement, tool registry, scheduler, external connectors.
**Python orchestration** — LLM planning via OpenAI API, prompt/template layer.
**Postgres** — user preferences, schedule cache, audit logs (pgvector planned for v2+).

---

## Repo Structure

```
agentic-personal-ai-assistant/
├── assistant-core-rs/       # Rust assistant core (CLI, policy, tool registry, scheduler)
│   ├── Cargo.toml
│   └── src/
│       ├── main.rs          # CLI: --health, --list-tools, --brief
│       ├── lib.rs
│       └── core/
│           ├── mod.rs
│           ├── types.rs     # ToolRequest, ToolResponse, RiskLevel
│           ├── tool_registry.rs
│           ├── policy.rs    # v1: allow Low/Medium, block High/Critical
│           └── scheduler.rs
├── ai-orchestration-py/     # Python AI orchestration (FastAPI)
│   ├── pyproject.toml
│   ├── README.md
│   └── src/orchestrator/
│       ├── app.py           # /healthz, /plan endpoints
│       ├── models.py        # PlanRequest, PlanResponse, ToolCall
│       ├── llm_client.py    # Stub keyword planner (LLM later)
│       └── prompts/         # System & planner prompt templates
├── database/                # Postgres DDL
│   ├── schema.sql           # v1 tables (users, events, audit_logs, …)
│   └── README.md
├── tools/                   # Tool contracts (spec.json + README per tool)
│   ├── email_event_reader/
│   ├── weather_lookup/
│   └── memory_store/
├── scripts/                 # Dev helper scripts
│   ├── check_health.sh
│   └── setup_db.sh
├── docs/                    # Design documents (PRD, architecture, data, security, tests)
├── .env.example             # Safe env template — copy to .env
├── .gitignore
├── PROJECT_CONTEXT.md       # One-page handoff for new chat sessions
└── README.md
```

---

## Quickstart

```bash
# 1. Clone the repo
git clone https://github.com/<your-org>/agentic-personal-ai-assistant.git
cd agentic-personal-ai-assistant

# 2. Copy the env template and fill in your keys
cp .env.example .env
# edit .env with your API keys

# 3. Start Postgres and apply schema
docker compose up -d db          # (docker-compose.yml coming soon)
./scripts/setup_db.sh

# 4. Build & sanity-check the Rust core
cd assistant-core-rs
cargo build
cargo run -- --health            # prints "ok"
cargo run -- --list-tools        # lists registered tools
cd ..

# 5. Set up & run the Python orchestration service
cd ai-orchestration-py
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn src.orchestrator.app:app --reload --port 8001
# In another terminal:
#   curl http://localhost:8001/healthz
cd ..
```

---

## Smoke Test

Run the end-to-end smoke test (requires a `.env` with `DATABASE_URL` and the Python venv set up):

```bash
./scripts/smoke_test.sh
```

This applies the schema, starts uvicorn, writes a memory via the API, reads it back, and reports PASS/FAIL.

---

## Environment Variables

All secrets live in a `.env` file at the repo root (git-ignored).
A safe template is provided in **`.env.example`** — copy it and fill in real values locally.

| Variable | Purpose |
|---|---|
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key |
| `OPENAI_API_KEY` | OpenAI API key for LLM calls |
| `GMAIL_CLIENT_ID` | Google OAuth 2.0 client ID |
| `GMAIL_CLIENT_SECRET` | Google OAuth 2.0 client secret |
| `GMAIL_REDIRECT_URI` | OAuth callback URL |
| `DATABASE_URL` | Postgres connection string |

---

## Roadmap

| Version | Focus |
|---|---|
| **v1** | Morning brief — Gmail schedule extraction, weather, CLI, Postgres persistence |
| **v2** | Memory & learning — pgvector embeddings, user preference refinement, feedback loop |
| **v3** | Proactive actions — calendar write-back, reminders, multi-channel delivery |
| **v4** | Multi-agent — delegated sub-agents, plugin ecosystem, voice interface |

---

## License

This project will be released under the [MIT License](https://opensource.org/licenses/MIT).
A `LICENSE` file will be added before the first public release.
