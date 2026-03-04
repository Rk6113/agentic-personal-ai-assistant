# Database

Postgres schema for the Agentic Personal AI Assistant (v1).

## Tables

| Table | Purpose |
|---|---|
| `users` | User accounts |
| `preferences` | Key-value user preferences (JSONB) |
| `memories` | Key-value facts the assistant learns (mem_key/mem_value, upsert by user+key+scope) |
| `email_sources` | Gmail OAuth tokens and sync state |
| `events` | Calendar events extracted from email |
| `weather_cache` | Cached weather forecasts |
| `audit_logs` | Every tool invocation and policy decision |

## Apply Schema

```bash
# Ensure Postgres is running and DATABASE_URL is set
psql "$DATABASE_URL" -f database/schema.sql
```

## Notes

- UUID primary keys via `uuid-ossp`.
- pgvector extension will be added in v2 for embedding-based memory search.
- Migrations tooling (e.g. dbmate) will be introduced once schema is stable.
