"""Gmail OAuth 2.0 (read-only) — auth flow, token management, service builder."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from base64 import urlsafe_b64encode
from datetime import datetime, timezone
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from . import db

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
SCOPE_STR = " ".join(SCOPES)
AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
PKCE_TTL_SECONDS = 600  # 10 minutes

_PKCE: dict[str, dict[str, Any]] = {}
_pkce_lock = threading.Lock()


# ── Config helpers ───────────────────────────────────────────────────────────


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set. Add it to the repo-root .env file.")
    return value


# ── PKCE ─────────────────────────────────────────────────────────────────────


def _code_challenge(verifier: str) -> str:
    """BASE64URL(SHA256(code_verifier)) without padding."""
    digest = hashlib.sha256(verifier.encode()).digest()
    return urlsafe_b64encode(digest).rstrip(b"=").decode()


def _pkce_cleanup() -> None:
    """Remove expired entries from _PKCE."""
    now = time.time()
    expired = [s for s, v in _PKCE.items() if (v.get("ts") or 0) + PKCE_TTL_SECONDS < now]
    for s in expired:
        _PKCE.pop(s, None)


# ── OAuth flow ───────────────────────────────────────────────────────────────


def build_auth_url() -> str:
    """Generate the Google OAuth consent URL with PKCE (read-only Gmail scope)."""
    state = secrets.token_urlsafe(24)
    code_verifier = secrets.token_urlsafe(48)
    code_challenge = _code_challenge(code_verifier)

    with _pkce_lock:
        _pkce_cleanup()
        _PKCE[state] = {"verifier": code_verifier, "ts": time.time()}

    client_id = _require_env("GMAIL_CLIENT_ID")
    redirect_uri = _require_env("GMAIL_REDIRECT_URI")

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": SCOPE_STR,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent",
    }
    return f"{AUTH_URI}?{urllib.parse.urlencode(params)}"


def exchange_code_for_token(code: str, state: str) -> dict[str, Any]:
    """Exchange authorization code for tokens using PKCE code_verifier.

    Returns dict with access_token, refresh_token, expires_in, scope, token_type.
    """
    with _pkce_lock:
        entry = _PKCE.pop(state, None)
        if not entry:
            raise RuntimeError(
                "Missing/expired PKCE verifier; restart /gmail/connect and try again."
            )
        ts = entry.get("ts") or 0
        if ts + PKCE_TTL_SECONDS < time.time():
            raise RuntimeError(
                "Missing/expired PKCE verifier; restart /gmail/connect and try again."
            )
        code_verifier = entry["verifier"]

    client_id = _require_env("GMAIL_CLIENT_ID")
    client_secret = _require_env("GMAIL_CLIENT_SECRET")
    redirect_uri = _require_env("GMAIL_REDIRECT_URI")

    body = urllib.parse.urlencode({
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
        "code_verifier": code_verifier,
    }).encode()

    req = urllib.request.Request(
        TOKEN_URI,
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"Token exchange failed: {e.code} {body}") from e
    except OSError as e:
        raise RuntimeError(f"Token exchange failed: {e}") from e

    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token"),
        "expires_in": data.get("expires_in", 3600),
        "scope": data.get("scope", SCOPE_STR),
        "token_type": data.get("token_type", "Bearer"),
    }


def credentials_from_token_response(token_response: dict[str, Any]) -> Credentials:
    """Build Credentials from a token exchange response (for one-off API calls)."""
    from datetime import timedelta

    expiry = datetime.now(timezone.utc)
    if token_response.get("expires_in"):
        expiry = expiry + timedelta(seconds=int(token_response["expires_in"]))
    expiry_naive = expiry.replace(tzinfo=None)

    return Credentials(
        token=token_response["access_token"],
        refresh_token=token_response.get("refresh_token"),
        token_uri=TOKEN_URI,
        client_id=_require_env("GMAIL_CLIENT_ID"),
        client_secret=_require_env("GMAIL_CLIENT_SECRET"),
        scopes=SCOPES,
        expiry=expiry_naive,
    )


# ── Credentials from DB ─────────────────────────────────────────────────────


def credentials_from_db(row: dict[str, Any]) -> Credentials:
    """Reconstruct a ``Credentials`` object from a gmail_tokens DB row."""
    expiry = row.get("token_expiry")
    if expiry is not None and expiry.tzinfo is not None:
        expiry = expiry.astimezone(timezone.utc).replace(tzinfo=None)

    return Credentials(
        token=row["access_token"],
        refresh_token=row["refresh_token"],
        token_uri=TOKEN_URI,
        client_id=_require_env("GMAIL_CLIENT_ID"),
        client_secret=_require_env("GMAIL_CLIENT_SECRET"),
        scopes=SCOPES,
        expiry=expiry,
    )


def _refresh_if_needed(creds: Credentials, provider_email: str) -> Credentials:
    """Refresh the token if expired and persist the new one."""
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        db.gmail_token_upsert(
            provider_email=provider_email,
            access_token=creds.token,
            refresh_token=creds.refresh_token,
            token_expiry=creds.expiry,
            scope=",".join(creds.scopes or []),
        )
        logger.info("Refreshed Gmail token for %s", provider_email)
    return creds


# ── Gmail service ────────────────────────────────────────────────────────────


def build_gmail_service(creds: Credentials) -> Any:
    """Build a Gmail API service client (v1, read-only)."""
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def get_gmail_service() -> tuple[Any, str]:
    """Load stored credentials, refresh if needed, return ``(service, email)``.

    Raises ``RuntimeError`` if no Gmail account is connected.
    """
    row = db.gmail_token_get()
    if row is None:
        raise RuntimeError("Gmail not connected. Call /gmail/connect first.")

    creds = credentials_from_db(row)
    creds = _refresh_if_needed(creds, row["provider_email"])
    service = build_gmail_service(creds)
    return service, row["provider_email"]


# ── Message helpers ──────────────────────────────────────────────────────────


def list_latest_messages(max_results: int = 5) -> tuple[str, list[dict[str, str]]]:
    """Fetch the latest messages. Returns ``(email, messages)``."""
    service, email = get_gmail_service()

    result = (
        service.users()
        .messages()
        .list(userId="me", maxResults=max_results)
        .execute()
    )

    messages: list[dict[str, str]] = []
    for meta in result.get("messages", []):
        msg = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=meta["id"],
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            )
            .execute()
        )
        headers = {
            h["name"]: h["value"]
            for h in msg.get("payload", {}).get("headers", [])
        }
        messages.append(
            {
                "id": msg["id"],
                "subject": headers.get("Subject", "(no subject)"),
                "from": headers.get("From", ""),
                "date": headers.get("Date", ""),
                "snippet": msg.get("snippet", ""),
            }
        )

    return email, messages
