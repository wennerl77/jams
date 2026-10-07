#!/usr/bin/env bash
# =============================================================================
# Benchmark Database Reset & Seeder Runner (Docker Compose Controlled Environment)
# Restores Helium (MySQL) to Clean Initial Benchmark State.
# Flags:
#   --helium   : Reset Helium (default)
#   --systems  : Start Docker Compose services if not running
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

START_SYSTEMS=false

for arg in "$@"; do
  case $arg in
    --systems|-s)
      START_SYSTEMS=true
      ;;
    --helium)
      ;;
  esac
done

# Resolve docker command
if docker ps >/dev/null 2>&1; then
    DOCKER_CMD="docker"
else
    DOCKER_CMD="sudo docker"
fi

echo "================================================================="
echo " Restoring Helium Database Benchmark Seeds (Controlled Reset)"
echo " Environment: Local Docker Compose"
echo " Reset Helium: true | Start Systems: $START_SYSTEMS"
echo "================================================================="

# Optional: Start Docker Compose services locally if --systems flag is passed
if [ "$START_SYSTEMS" = true ]; then
    echo "[1/2] Starting Docker Compose services locally (--systems active)..."
    (cd "$ROOT_DIR" && $DOCKER_CMD compose up -d)
    echo "  Waiting for databases and caches to be healthy..."
    sleep 5
fi

# Reset Helium Database (MySQL)
echo "[*] Seeding Helium database..."
HELIUM_APP_CID=$($DOCKER_CMD ps -q --filter name=helium-app | head -n 1)
HELIUM_DB_CID=$($DOCKER_CMD ps -q --filter name=helium-db | head -n 1)
HELIUM_JUDGE_CID=$($DOCKER_CMD ps -q --filter name=helium-autojudge | head -n 1)

if [ -n "$HELIUM_DB_CID" ]; then
    if [ -n "$HELIUM_APP_CID" ]; then
        $DOCKER_CMD exec -i "$HELIUM_APP_CID" php artisan db:seed --force 2>/dev/null || true
    fi
    $DOCKER_CMD exec -i "$HELIUM_DB_CID" mysql -u microhelium -psecret microhelium < "$SCRIPT_DIR/helium/01_seed_benchmark.sql"
    if [ -n "$HELIUM_JUDGE_CID" ]; then
        $DOCKER_CMD exec "$HELIUM_JUDGE_CID" bash -c 'rm -rf /var/www/html/storage/app/judge/* /tmp/safeexec* 2>/dev/null || true' 2>/dev/null || true
    fi
    echo "  ✔ Helium MySQL seeded and judge storage cleared successfully."
else
    echo "  ⚠ Container 'helium-db' is not running. Use 'make helium-up' or 'make up' to start."
fi

echo "================================================================="
echo " Helium Reset Complete!"
echo "================================================================="
