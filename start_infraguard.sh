#!/usr/bin/env bash
set -e

echo "============================================================================"
echo "  INFRAGUARD // AUTONOMOUS STRUCTURAL INTEGRITY & DIGITAL TWIN PLATFORM"
echo "============================================================================"

cd "$(dirname "$0")"

if [ ! -f "sample_data/test_images/span_ab_crack_critical.jpg" ]; then
    echo "[1/2] Generating benchmark structural sample datasets..."
    python3 -m sample_data.generate_demo_data
fi

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

echo "[2/2] Launching INFRAGUARD Server on http://${HOST}:${PORT} ..."
exec python3 -m uvicorn backend.main:app --host "${HOST}" --port "${PORT}"
