"""Pydantic models for the orchestration API."""

from __future__ import annotations

from pydantic import BaseModel, Field


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
