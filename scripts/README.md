# Scripts

Developer helper scripts for the Agentic Personal AI Assistant.

| Script | Purpose |
|---|---|
| `check_health.sh` | Runs health checks against Rust CLI and Python API |
| `setup_db.sh` | Applies `database/schema.sql` to the configured Postgres instance |

## Usage

```bash
chmod +x scripts/*.sh

# Health check (start the Python server first)
./scripts/check_health.sh

# Apply database schema
./scripts/setup_db.sh
```
