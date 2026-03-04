"""Database client — Postgres connection pool and memory CRUD."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)

_pool: ConnectionPool | None = None
_default_user_id: str | None = None

DEFAULT_USER_EMAIL = "default@local"


# ── .env discovery ───────────────────────────────────────────────────────────


def _find_dotenv() -> Path | None:
    """Walk up from this file's directory to find the repo-root .env."""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        candidate = parent / ".env"
        if candidate.is_file():
            return candidate
    return None


def load_env() -> None:
    """Load the repo-root .env (if present) into ``os.environ``."""
    from dotenv import load_dotenv

    dotenv_path = _find_dotenv()
    if dotenv_path:
        load_dotenv(dotenv_path, override=False)
        logger.info("Loaded .env from %s", dotenv_path.parent)
    else:
        logger.warning("No .env found walking up from %s", Path(__file__).parent)


# ── Connection pool ──────────────────────────────────────────────────────────


def get_pool() -> ConnectionPool:
    """Return (and lazily create) the module-level connection pool."""
    global _pool
    if _pool is not None:
        return _pool

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    _pool = ConnectionPool(
        conninfo=database_url,
        min_size=1,
        max_size=5,
        kwargs={"row_factory": dict_row},
    )
    _pool.open()
    logger.info("Connection pool opened")
    return _pool


def close_pool() -> None:
    """Close the pool and reset module-level state."""
    global _pool, _default_user_id
    if _pool is not None:
        _pool.close()
        _pool = None
        _default_user_id = None
        logger.info("Connection pool closed")


# ── Default user ─────────────────────────────────────────────────────────────


def ensure_default_user() -> str:
    """Ensure exactly one default user row exists. Returns its UUID as a string."""
    global _default_user_id
    if _default_user_id is not None:
        return _default_user_id

    pool = get_pool()
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE email = %s", (DEFAULT_USER_EMAIL,)
        ).fetchone()

        if row:
            _default_user_id = str(row["id"])
        else:
            row = conn.execute(
                "INSERT INTO users (email, display_name) VALUES (%s, %s) RETURNING id",
                (DEFAULT_USER_EMAIL, "Default User"),
            ).fetchone()
            conn.commit()
            _default_user_id = str(row["id"])  # type: ignore[index]
            logger.info("Created default user %s", _default_user_id)

    return _default_user_id  # type: ignore[return-value]


# ── Memory CRUD ──────────────────────────────────────────────────────────────


def memory_store(
    *,
    mem_key: str,
    mem_value: str,
    mem_type: str = "general",
    scope: str = "global",
) -> None:
    """Upsert a memory row for the default user."""
    user_id = ensure_default_user()
    pool = get_pool()
    with pool.connection() as conn:
        conn.execute(
            """
            INSERT INTO memories (user_id, mem_key, mem_value, mem_type, scope)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, mem_key, scope)
            DO UPDATE SET mem_value  = EXCLUDED.mem_value,
                          mem_type   = EXCLUDED.mem_type,
                          updated_at = now()
            """,
            (user_id, mem_key, mem_value, mem_type, scope),
        )
        conn.commit()


def memory_get(*, mem_key: str, scope: str = "global") -> dict[str, Any] | None:
    """Fetch a single memory row for the default user. Returns ``None`` if missing."""
    user_id = ensure_default_user()
    pool = get_pool()
    with pool.connection() as conn:
        return conn.execute(
            """
            SELECT mem_key, mem_value, mem_type, scope, created_at, updated_at
            FROM memories
            WHERE user_id = %s AND mem_key = %s AND scope = %s
            """,
            (user_id, mem_key, scope),
        ).fetchone()
