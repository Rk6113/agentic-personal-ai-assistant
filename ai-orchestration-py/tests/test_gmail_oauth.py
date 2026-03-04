"""Unit tests for Gmail OAuth helpers (no real credentials needed)."""

from __future__ import annotations


def test_build_auth_url_contains_google_and_scope(monkeypatch) -> None:
    monkeypatch.setenv("GMAIL_CLIENT_ID", "test-id.apps.googleusercontent.com")
    monkeypatch.setenv("GMAIL_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("GMAIL_REDIRECT_URI", "http://localhost:8001/gmail/oauth/callback")

    from src.orchestrator.gmail_oauth import build_auth_url

    url = build_auth_url()

    assert "accounts.google.com" in url
    assert "gmail.readonly" in url
    assert "test-id.apps.googleusercontent.com" in url
    assert "redirect_uri=" in url
    assert "code_challenge=" in url
    assert "code_challenge_method=S256" in url
    assert "state=" in url
