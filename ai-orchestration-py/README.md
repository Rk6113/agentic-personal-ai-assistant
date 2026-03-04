# AI Orchestration Service

Python-based LLM planning and prompt layer for the Agentic Personal AI Assistant.

## Prerequisites

- Python 3.11+
- A Postgres database (Neon or local). Set `DATABASE_URL` in the **repo-root** `.env`.
- An OpenWeatherMap API key. Set `OPENWEATHER_API_KEY` in the **repo-root** `.env`.
- Gmail OAuth credentials (for email features). See [Gmail Setup](#gmail-setup) below.

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

| Method | Path                     | Description                                       |
|--------|--------------------------|---------------------------------------------------|
| GET    | `/healthz`               | Health check — returns `{"status": "ok"}`          |
| POST   | `/plan`                  | Accepts `PlanRequest`, returns a tool-call plan    |
| POST   | `/memory/store`          | Upsert a memory (key/value) for the default user   |
| GET    | `/memory/{memory_key}`   | Retrieve a memory by key (404 if missing)           |
| GET    | `/weather?lat=&lon=`     | Current weather + clothing advice (cached 15 min)  |
| GET    | `/gmail/connect`         | Returns Google OAuth consent URL                    |
| GET    | `/gmail/oauth/callback`  | OAuth callback — exchanges code, stores tokens      |
| GET    | `/gmail/messages/latest` | List latest Gmail messages (requires connected acct)|

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

# Weather + clothing advice (Denton, TX coordinates)
curl -s "http://localhost:8001/weather?lat=33.21&lon=-97.13" | python3 -m json.tool

# Plan with weather context (lat/lon provided)
curl -s -X POST http://localhost:8001/plan \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Do I need a jacket today?", "context": {"lat": 33.21, "lon": -97.13}}' \
  | python3 -m json.tool
```

## Gmail Setup

1. Go to [Google Cloud Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials).
2. Create an **OAuth 2.0 Client ID** (type: Web application).
3. Add `http://localhost:8001/gmail/oauth/callback` as an **Authorized redirect URI**.
4. Enable the **Gmail API** in your project.
5. Copy Client ID and Client Secret into the repo-root `.env`:
   ```
   GMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GMAIL_CLIENT_SECRET=your-client-secret
   GMAIL_REDIRECT_URI=http://localhost:8001/gmail/oauth/callback
   ```

### Manual Verification

```bash
# 1. Start the server
uvicorn src.orchestrator.app:app --reload --port 8001

# 2. Get the consent URL
curl -s http://localhost:8001/gmail/connect | python3 -m json.tool
# → open the "auth_url" in your browser and approve

# 3. After approval, Google redirects to /gmail/oauth/callback
#    which stores tokens and returns:
#    { "status": "connected", "email": "you@gmail.com" }

# 4. Fetch latest messages
curl -s "http://localhost:8001/gmail/messages/latest?max=3" | python3 -m json.tool
```

## Tests

Tests run with `pytest`. Weather-advice tests are pure functions (no API key needed).
Integration tests require a live Postgres database and skip when `DATABASE_URL` is not set.

```bash
# Make sure .env exists at the repo root with a valid DATABASE_URL
# (and the schema has been applied: psql "$DATABASE_URL" -f ../database/schema.sql)

pytest tests/ -v
```
