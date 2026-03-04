"""Pydantic models for the orchestration API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ── Planner models ───────────────────────────────────────────────────────────


class ToolCall(BaseModel):
    tool_name: str = Field(description="Name of the tool to invoke")
    parameters: dict = Field(default_factory=dict, description="Tool input parameters")
    reason: str = Field(default="", description="Why the planner chose this tool")


class PlanRequest(BaseModel):
    user_input: str = Field(description="Raw user query or trigger context")
    context: dict = Field(default_factory=dict, description="Extra context (preferences, time, etc.)")


class PlanResponse(BaseModel):
    plan_id: str = Field(description="Unique plan identifier")
    steps: list[ToolCall] = Field(default_factory=list, description="Ordered tool calls")
    reasoning: str = Field(default="", description="High-level explanation of the plan")


# ── Memory models ────────────────────────────────────────────────────────────


class MemoryStoreRequest(BaseModel):
    memory_key: str = Field(description="Short identifier, e.g. 'home_city'")
    memory_value: str = Field(description="Value to persist, e.g. 'Denton'")
    memory_type: str = Field(default="preference", description="Category: preference, fact, note")
    scope: str = Field(default="global", description="Scope qualifier")


class MemoryResponse(BaseModel):
    memory_key: str
    memory_value: str
    memory_type: str
    scope: str
    created_at: datetime
    updated_at: datetime
