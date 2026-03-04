"""FastAPI application — orchestration endpoints."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException

from . import db
from .llm_client import extract_memory, generate_plan
from .models import MemoryResponse, MemoryStoreRequest, PlanRequest, PlanResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    db.load_env()
    db.get_pool()
    db.ensure_default_user()
    logger.info("Orchestration service ready")
    yield
    db.close_pool()


app = FastAPI(
    title="AI Orchestration Service",
    version="0.1.0",
    description="LLM planning layer for the Agentic Personal AI Assistant",
    lifespan=lifespan,
)


# ── Health ───────────────────────────────────────────────────────────────────


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


# ── Planning ─────────────────────────────────────────────────────────────────


@app.post("/plan", response_model=PlanResponse)
def plan(request: PlanRequest) -> PlanResponse:
    """Accept user text + context, return a tool-call plan.

    When the plan includes ``memory_store`` and a 'remember X is Y' pattern is
    detected, the memory is persisted to Postgres as a side-effect.
    """
    result = generate_plan(request.user_input, request.context)

    if any(step.tool_name == "memory_store" for step in result.steps):
        extracted = extract_memory(request.user_input)
        if extracted:
            key, value = extracted
            db.memory_store(mem_key=key, mem_value=value, mem_type="preference")
            logger.info("Persisted memory: %s", key)

    return result


# ── Memory ───────────────────────────────────────────────────────────────────


@app.post("/memory/store", status_code=200)
def memory_store(request: MemoryStoreRequest) -> dict[str, str]:
    """Upsert a memory row for the default user."""
    db.memory_store(
        mem_key=request.memory_key,
        mem_value=request.memory_value,
        mem_type=request.memory_type,
        scope=request.scope,
    )
    return {"status": "stored"}


@app.get("/memory/{memory_key}", response_model=MemoryResponse)
def memory_get(memory_key: str, scope: str = "global") -> MemoryResponse:
    """Retrieve a single memory by key + scope."""
    row = db.memory_get(mem_key=memory_key, scope=scope)
    if row is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return MemoryResponse(
        memory_key=row["mem_key"],
        memory_value=row["mem_value"],
        memory_type=row["mem_type"],
        scope=row["scope"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
