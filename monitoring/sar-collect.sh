#!/usr/bin/env bash
# =============================================================================
# Benchmark Telemetry Collector (Docker Compose Controlled Environment)
# Collects CPU, RAM, Disk I/O, and Verdicts directly from Helium Docker containers.
# Usage: ./monitoring/sar-collect.sh [helium] [scenario] [interval_seconds]
#    or: ./monitoring/sar-collect.sh [scenario] [interval_seconds]
# =============================================================================

set -euo pipefail

TARGET="helium"
SCENARIO="burst"
INTERVAL="1"

if [ $# -ge 1 ]; then
    if [ "$1" = "helium" ] || [ "$1" = "boca" ]; then
        TARGET="helium"
        SCENARIO="${2:-burst}"
        INTERVAL="${3:-1}"
    else
        TARGET="helium"
        SCENARIO="$1"
        INTERVAL="${2:-1}"
    fi
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="python3"
if [ -f "$ROOT_DIR/venv/bin/python" ]; then
    PYTHON_BIN="$ROOT_DIR/venv/bin/python"
fi

exec "$PYTHON_BIN" "$ROOT_DIR/monitoring/docker-collect.py" "$TARGET" "$SCENARIO" "$INTERVAL"
