"""Stub LLM client — will be replaced with real OpenAI API calls."""

from __future__ import annotations

import re
import uuid

from .models import PlanResponse, ToolCall


KEYWORD_TOOL_MAP: dict[str, ToolCall] = {
    "schedule": ToolCall(
        tool_name="email_event_reader",
        reason="User query mentions schedule/calendar",
    ),
    "calendar": ToolCall(
        tool_name="email_event_reader",
        reason="User query mentions schedule/calendar",
    ),
    "weather": ToolCall(
        tool_name="weather_lookup",
        reason="User query mentions weather",
    ),
    "jacket": ToolCall(
        tool_name="weather_lookup",
        reason="User may need outfit advice",
    ),
    "cold": ToolCall(
        tool_name="weather_lookup",
        reason="User mentions temperature conditions",
    ),
    "hot": ToolCall(
        tool_name="weather_lookup",
        reason="User mentions temperature conditions",
    ),
    "remember": ToolCall(
        tool_name="memory_store",
        reason="User query asks to remember something",
    ),
    "preference": ToolCall(
        tool_name="memory_store",
        reason="User query involves preferences",
    ),
}

_REMEMBER_PATTERN = re.compile(
    r"remember\s+(?:that\s+)?(?:my\s+)?(.+?)\s+is\s+(.+)",
    re.IGNORECASE,
)


def extract_memory(user_input: str) -> tuple[str, str] | None:
    """Try to parse 'remember (my) <key> is <value>' from free text.

    Returns ``(normalised_key, value)`` or ``None``.
    """
    match = _REMEMBER_PATTERN.search(user_input)
    if match:
        key = match.group(1).strip().replace(" ", "_").lower()
        value = match.group(2).strip().rstrip(".")
        return key, value
    return None


def _enrich_weather_call(tc: ToolCall, context: dict | None) -> ToolCall:
    """Inject lat/lon from context into a weather_lookup tool call."""
    tc = tc.model_copy()
    if context and "lat" in context and "lon" in context:
        tc.parameters = {"lat": context["lat"], "lon": context["lon"]}
    else:
        tc.reason += " (provide lat/lon in context to get results)"
    return tc


def generate_plan(user_input: str, context: dict | None = None) -> PlanResponse:
    """Keyword-based mock planner. Will be replaced by LLM chain."""
    steps: list[ToolCall] = []
    lower = user_input.lower()

    seen: set[str] = set()
    for keyword, tool_call in KEYWORD_TOOL_MAP.items():
        if keyword in lower and tool_call.tool_name not in seen:
            tc = tool_call
            if tc.tool_name == "weather_lookup":
                tc = _enrich_weather_call(tc, context)
            steps.append(tc)
            seen.add(tc.tool_name)

    if not steps:
        steps.append(
            ToolCall(
                tool_name="email_event_reader",
                reason="Default: fetch today's events for the morning brief",
            )
        )

    return PlanResponse(
        plan_id=str(uuid.uuid4()),
        steps=steps,
        reasoning=f"Mock plan for: {user_input[:80]}",
    )
