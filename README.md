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
├── docs/                    # Design documents (PRD, architecture, data, security, tests)
│   ├── 01_prd_v1.md
│   ├── 02_system_architecture_v1.md
│   ├── 03_data_memory_design_v1.md
│   ├── 04_tool_skills_contract_v1.md
│   ├── 05_security_privacy_spec_v1.md
│   └── 06_test_plan_v1.md
├── rust-core/               # (planned) Rust assistant core crate
├── python-ai/               # (planned) Python orchestration package
├── migrations/              # (planned) SQL / dbmate migrations
├── scripts/                 # (planned) Dev helper scripts
├── .env.example             # Safe env template — copy to .env
├── .gitignore
├── PROJECT_CONTEXT.md       # One-page handoff for new chat sessions
└── README.md
```

---

## Quickstart

> Full setup instructions will be added once scaffolding is complete.

```bash
# 1. Clone the repo
git clone https://github.com/<your-org>/agentic-personal-ai-assistant.git
cd agentic-personal-ai-assistant

# 2. Copy the env template and fill in your keys
cp .env.example .env
# edit .env with your API keys

# 3. Start Postgres (example using Docker)
docker compose up -d db

# 4. Build the Rust core
cd rust-core && cargo build --release && cd ..

# 5. Set up the Python environment
cd python-ai && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cd ..

# 6. Run the morning brief
cargo run -- brief
```

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
