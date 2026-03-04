#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ ! -f "$REPO_ROOT/.env" ]; then
  echo "Error: .env not found at repo root. Create it from .env.example." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$REPO_ROOT/.env"
set +a

if [ -z "${DATABASE_URL:-}" ]; then
  echo "Error: DATABASE_URL is not set in .env." >&2
  exit 1
fi

psql "$DATABASE_URL" -f "$REPO_ROOT/database/schema.sql" >/dev/null
echo "Schema applied successfully."

