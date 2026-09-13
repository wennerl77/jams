#!/usr/bin/env bash
# =============================================================================
# Benchmark Telemetry Collector (sar / sysstat)
# Collects CPU, RAM, Disk I/O, and Context Switches via Vagrant SSH
# Usage: ./monitoring/sar-collect.sh [boca|helium] [scenario] [interval_seconds]
# Example: ./monitoring/sar-collect.sh boca burst 1
# =============================================================================

set -euo pipefail

TARGET="${1:-boca}"
SCENARIO="${2:-burst}"
INTERVAL="${3:-1}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$ROOT_DIR/results/$TARGET/$SCENARIO"
mkdir -p "$OUTPUT_DIR"

RAW_LOG="$OUTPUT_DIR/sar_raw.txt"
CSV_OUT="$OUTPUT_DIR/sar_metrics.csv"

echo "================================================================="
echo " Starting Telemetry Collection"
echo " Target VM:   $TARGET"
echo " Scenario:    $SCENARIO"
echo " Interval:    ${INTERVAL}s (Runtime Configurable)"
echo " Output Log:  $RAW_LOG"
echo "================================================================="

VAGRANT_DIR="$ROOT_DIR"
if [ -d "$ROOT_DIR/vagrant" ] && [ -f "$ROOT_DIR/vagrant/Vagrantfile" ]; then
    VAGRANT_DIR="$ROOT_DIR/vagrant"
fi

if ! command -v vagrant &> /dev/null; then
    echo "ERROR: Vagrant CLI is not installed or not in PATH."
    exit 1
fi

echo "Connecting via Vagrant SSH to $TARGET (directory: $VAGRANT_DIR)..."

# Collect sar data via Vagrant SSH
(cd "$VAGRANT_DIR" && vagrant ssh "$TARGET" -c "sar -u -r -b -w $INTERVAL 60") > "$RAW_LOG" 2>&1 &
SAR_PID=$!

echo "Collector started with PID $SAR_PID. Converting output to CSV..."
sleep 2

# Invoke Python parser to generate sar_metrics.csv
python3 "$ROOT_DIR/monitoring/parse_sar.py" "$RAW_LOG" "$CSV_OUT"

echo "Telemetry ready at: $CSV_OUT"
