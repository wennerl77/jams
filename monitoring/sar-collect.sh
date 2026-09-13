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

get_vagrant_ssh_cmd() {
    local target="$1"
    if [ -d "$ROOT_DIR/vagrant" ] && (cd "$ROOT_DIR/vagrant" && vagrant status "$target" 2>/dev/null | grep -q "running"); then
        echo "cd '$ROOT_DIR/vagrant' && vagrant ssh '$target' -c"
        return
    fi
    local global_id
    global_id=$(vagrant global-status 2>/dev/null | awk -v t="$target" '$2 == t && $4 == "running" {print $1; exit}')
    if [ -n "$global_id" ]; then
        echo "vagrant ssh $global_id -c"
        return
    fi
    echo ""
}

TARGET_SSH_CMD=$(get_vagrant_ssh_cmd "$TARGET")

if [ -z "$TARGET_SSH_CMD" ]; then
    echo "ERROR: Vagrant VM '$TARGET' is not running or not accessible."
    exit 1
fi

echo "Connecting via Vagrant SSH to $TARGET..."

# Collect sar data via Vagrant SSH
eval "$TARGET_SSH_CMD \"sar -u -r -b -w $INTERVAL 60\"" > "$RAW_LOG" 2>&1 &
SAR_PID=$!

echo "Collector started with PID $SAR_PID. Converting output to CSV..."
sleep 2

# Invoke Python parser to generate sar_metrics.csv
python3 "$ROOT_DIR/monitoring/parse_sar.py" "$RAW_LOG" "$CSV_OUT"

echo "Telemetry ready at: $CSV_OUT"
