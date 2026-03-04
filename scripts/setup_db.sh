#!/usr/bin/env bash
# Apply the v1 Postgres schema.
# Requires DATABASE_URL to be set (or source .env first).
set -euo pipefail

if [ -z "${DATABASE_URL:-}" ]; then
  echo "Error: DATABASE_URL is not set. Run: source .env" >&2
  exit 1
fi

echo "Applying schema to $DATABASE_URL ..."
psql "$DATABASE_URL" -f database/schema.sql
echo "Done."
