#!/usr/bin/env bash
# End-to-end smoke test: schema → server → store → get → cleanup.
set -euo pipefail

PASS=0
FAIL=0
PORT=8001
PID=""
ORCH_DIR="$(cd "$(dirname "$0")/../ai-orchestration-py" && pwd)"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cleanup() {
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        kill "$PID" 2>/dev/null || true
        wait "$PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

log()  { echo "  $*"; }
pass() { log "✓ $*"; PASS=$((PASS + 1)); }
fail() { log "✗ $*"; FAIL=$((FAIL + 1)); }

# ── Preflight ────────────────────────────────────────────────────────────────

if [ -f "$REPO_ROOT/.env" ]; then
    set -a; source "$REPO_ROOT/.env"; set +a
fi

if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: DATABASE_URL is not set. Create .env at repo root." >&2
    exit 1
fi

if [ ! -d "$ORCH_DIR/.venv" ]; then
    echo "ERROR: $ORCH_DIR/.venv not found." >&2
    echo "  Run:  cd ai-orchestration-py && python3 -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'" >&2
    exit 1
fi

echo "=== Smoke Test ==="
echo ""

# ── 1. Apply schema ─────────────────────────────────────────────────────────

echo "[1/4] Applying database schema …"
if psql "$DATABASE_URL" -f "$REPO_ROOT/database/schema.sql" >/dev/null 2>&1; then
    pass "Schema applied"
else
    log  "(schema may already exist — continuing)"
fi

# ── 2. Start uvicorn ─────────────────────────────────────────────────────────

echo "[2/4] Starting uvicorn on port $PORT …"
UVICORN_LOG="$(mktemp)"
(
    cd "$ORCH_DIR"
    source .venv/bin/activate
    uvicorn src.orchestrator.app:app --port "$PORT" \
        --log-level warning \
        --reload-exclude ".venv/*" \
        >"$UVICORN_LOG" 2>&1
) &
PID=$!

# Wait up to 15 s for /healthz
STARTED=false
for i in $(seq 1 30); do
    if curl -sf "http://localhost:$PORT/healthz" >/dev/null 2>&1; then
        STARTED=true
        break
    fi
    sleep 0.5
done

if $STARTED; then
    pass "Server healthy"
else
    fail "Server failed to start"
    echo "  Last logs:"
    tail -20 "$UVICORN_LOG" | sed 's/^/    /'
    rm -f "$UVICORN_LOG"
    exit 1
fi

# ── 3. POST /memory/store ───────────────────────────────────────────────────

echo "[3/4] Storing test memory …"
STORE_RESP=$(curl -sf -X POST "http://localhost:$PORT/memory/store" \
    -H "Content-Type: application/json" \
    -d '{"memory_key":"_smoke_test_key","memory_value":"smoke_ok","memory_type":"preference"}')

if echo "$STORE_RESP" | grep -q '"stored"'; then
    pass "POST /memory/store returned stored"
else
    fail "POST /memory/store unexpected response: $STORE_RESP"
fi

# ── 4. GET /memory/_smoke_test_key ───────────────────────────────────────────

echo "[4/4] Retrieving test memory …"
GET_RESP=$(curl -sf "http://localhost:$PORT/memory/_smoke_test_key")

if echo "$GET_RESP" | grep -q '"smoke_ok"'; then
    pass "GET /memory/_smoke_test_key returned correct value"
else
    fail "GET /memory/_smoke_test_key unexpected response: $GET_RESP"
fi

# ── Summary ──────────────────────────────────────────────────────────────────

rm -f "$UVICORN_LOG"
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
