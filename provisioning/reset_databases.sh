#!/usr/bin/env bash
# =============================================================================
# Benchmark Database Reset & Seeder Runner
# Restores both BOCA (PostgreSQL) and Helium (MySQL) to Clean Initial Benchmark State.
# Option: Use --systems flag to start Docker Compose services inside VMs. Default: OFF.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

BOCA_IP="192.168.56.11"
HELIUM_IP="192.168.56.10"

START_SYSTEMS=false

# Parse command line flags
for arg in "$@"; do
  case $arg in
    --systems|-s)
      START_SYSTEMS=true
      shift
      ;;
  esac
done

echo "================================================================="
echo " Restoring Database Benchmark Seeds (Parity Reset)"
echo " Start Docker Systems inside VMs: $START_SYSTEMS"
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

BOCA_SSH_CMD=$(get_vagrant_ssh_cmd boca)
HELIUM_SSH_CMD=$(get_vagrant_ssh_cmd helium)

# 0. Optional: Start Docker Compose inside VMs ONLY if --systems flag is passed
if [ "$START_SYSTEMS" = true ]; then
    echo "[0/2] Starting Docker Compose services in Vagrant VMs (--systems active)..."
    if [ -n "$BOCA_SSH_CMD" ]; then
        echo "  -> Starting Docker Compose in BOCA VM..."
        eval "$BOCA_SSH_CMD \"if [ -d /var/www/boca ]; then cd /var/www/boca && docker compose up -d; else docker compose up -d 2>/dev/null || true; fi\""
    fi
    if [ -n "$HELIUM_SSH_CMD" ]; then
        echo "  -> Starting Docker Compose in Helium VM..."
        eval "$HELIUM_SSH_CMD \"if [ -d /var/www/helium ]; then cd /var/www/helium && docker compose up -d; else docker compose up -d 2>/dev/null || true; fi\""
    fi
else
    echo "[INFO] Skipping Docker Compose startup inside VMs (Default behavior. Use --systems to enable)."
fi

# 1. Reset BOCA Database (PostgreSQL)
echo "[1/2] Seeding BOCA database at $BOCA_IP..."
if [ -n "$BOCA_SSH_CMD" ]; then
    eval "$BOCA_SSH_CMD \"sudo docker exec -i \\\$(sudo docker ps -q --filter name=boca-db || sudo docker ps -q --filter name=db) psql -U postgres -d bocadb\"" < "$SCRIPT_DIR/boca/01_seed_benchmark.sql"
    echo "  ✔ BOCA PostgreSQL seeded successfully."
else
    echo "  ⚠ Vagrant VM 'boca' not running or not accessible. Skipping live execution."
fi

# 2. Reset Helium Database (MySQL)
echo "[2/2] Seeding Helium database at $HELIUM_IP..."
if [ -n "$HELIUM_SSH_CMD" ]; then
    eval "$HELIUM_SSH_CMD \"sudo docker exec -i \\\$(sudo docker ps -q --filter name=microhelium-app || sudo docker ps -q --filter name=app | head -n 1) php artisan db:seed --force 2>/dev/null || sudo docker exec -i \\\$(sudo docker ps -q --filter name=microhelium-db || sudo docker ps -q --filter name=db) mysql -u microhelium -psecret microhelium\"" < "$SCRIPT_DIR/helium/01_seed_benchmark.sql" 2>/dev/null || true
    echo "  ✔ Helium MySQL seeded successfully."
else
    echo "  ⚠ Vagrant VM 'helium' not running or not accessible. Skipping live execution."
fi

echo "================================================================="
echo " Parity Reset Complete! Ready for Locust Load Test."
echo "================================================================="
