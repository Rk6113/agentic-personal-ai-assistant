"""Integration tests for the /memory/* endpoints.

Requires a live Postgres database via DATABASE_URL.
Skips gracefully when DATABASE_URL is not set.
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set — skipping DB integration tests",
)


@pytest.fixture(scope="module")
def client():
    from src.orchestrator.app import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _cleanup_test_memories():
    """Delete any test-prefixed memories after each test."""
    yield
    try:
        from src.orchestrator import db

        user_id = db.ensure_default_user()
        pool = db.get_pool()
        with pool.connection() as conn:
            conn.execute(
                "DELETE FROM memories WHERE user_id = %s AND mem_key LIKE %s",
                (user_id, "_test_%"),
            )
            conn.commit()
    except Exception:
        pass


def test_memory_store_and_get(client: TestClient) -> None:
    resp = client.post(
        "/memory/store",
        json={
            "memory_key": "_test_city",
            "memory_value": "Denton",
            "memory_type": "preference",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "stored"

    resp = client.get("/memory/_test_city")
    assert resp.status_code == 200
    body = resp.json()
    assert body["memory_key"] == "_test_city"
    assert body["memory_value"] == "Denton"
    assert body["memory_type"] == "preference"
    assert body["scope"] == "global"


def test_memory_upsert_overwrites(client: TestClient) -> None:
    client.post(
        "/memory/store",
        json={"memory_key": "_test_color", "memory_value": "blue"},
    )
    client.post(
        "/memory/store",
        json={"memory_key": "_test_color", "memory_value": "green"},
    )

    resp = client.get("/memory/_test_color")
    assert resp.status_code == 200
    assert resp.json()["memory_value"] == "green"


def test_memory_not_found(client: TestClient) -> None:
    resp = client.get("/memory/_test_nonexistent")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Memory not found"
