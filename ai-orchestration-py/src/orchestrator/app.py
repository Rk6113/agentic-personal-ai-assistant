"""FastAPI application — orchestration endpoints."""

from __future__ import annotations

from fastapi import FastAPI

from .llm_client import generate_plan
from .models import PlanRequest, PlanResponse

app = FastAPI(
    title="AI Orchestration Service",
    version="0.1.0",
    description="LLM planning layer for the Agentic Personal AI Assistant",
)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/plan", response_model=PlanResponse)
async def plan(request: PlanRequest) -> PlanResponse:
    """Accept user text + context, return a tool-call plan."""
    return generate_plan(request.user_input, request.context)
