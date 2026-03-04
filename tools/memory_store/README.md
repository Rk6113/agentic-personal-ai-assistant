# memory_store

Persists and retrieves user preferences, facts, and learned context
in Postgres. Will support pgvector similarity search in v2.

## Status

Skeleton — `spec.json` defines the contract. Implementation pending.

## Risk Level

**Medium** — writes to the database (user-scoped, audited).
