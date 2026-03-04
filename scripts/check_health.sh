#!/usr/bin/env bash
# Quick health-check for both services.
set -euo pipefail

echo "=== Rust assistant-core ==="
(cd assistant-core-rs && cargo run --quiet -- --health)

echo ""
echo "=== Python orchestration ==="
curl -sf http://localhost:8001/healthz | python3 -m json.tool
