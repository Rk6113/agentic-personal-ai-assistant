# AI Orchestration Service

Python-based LLM planning and prompt layer for the Agentic Personal AI Assistant.

## Setup

```bash
cd ai-orchestration-py

# Create a virtual environment (Python 3.11+)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

## Run

```bash
uvicorn src.orchestrator.app:app --reload --port 8001
```

## Endpoints

| Method | Path       | Description                              |
|--------|-----------|------------------------------------------|
| GET    | `/healthz` | Health check — returns `{"status": "ok"}` |
| POST   | `/plan`    | Accepts `PlanRequest`, returns a tool-call plan |

## Example

```bash
curl -s http://localhost:8001/healthz

curl -s -X POST http://localhost:8001/plan \
  -H "Content-Type: application/json" \
  -d '{"user_input": "What is my schedule and weather today?"}' | python3 -m json.tool
```
