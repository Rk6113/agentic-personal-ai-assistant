"""Shared test fixtures — loads repo-root .env and fixes sys.path."""

from __future__ import annotations

import sys
from pathlib import Path

# Add ai-orchestration-py/ to sys.path so `src.orchestrator` imports resolve
_AI_ORCH_ROOT = Path(__file__).resolve().parent.parent
if str(_AI_ORCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_AI_ORCH_ROOT))


def _load_root_dotenv() -> None:
    """Walk up from this file to find the repo-root .env and load it."""
    from dotenv import load_dotenv

    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        candidate = parent / ".env"
        if candidate.is_file():
            load_dotenv(candidate, override=False)
            return


_load_root_dotenv()
