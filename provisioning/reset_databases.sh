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

VAGRANT_DIR="$ROOT_DIR"
if [ -d "$ROOT_DIR/vagrant" ] && [ -f "$ROOT_DIR/vagrant/Vagrantfile" ]; then
    VAGRANT_DIR="$ROOT_DIR/vagrant"
fi

# 0. Optional: Start Docker Compose inside VMs ONLY if --systems flag is passed
if [ "$START_SYSTEMS" = true ]; then
    echo "[0/2] Starting Docker Compose services in Vagrant VMs (--systems active)..."
    if (cd "$VAGRANT_DIR" && vagrant status boca 2>/dev/null | grep -q "running"); then
        echo "  -> Starting Docker Compose in BOCA VM..."
        (cd "$VAGRANT_DIR" && vagrant ssh boca -c "if [ -d /var/www/boca ]; then cd /var/www/boca && docker compose up -d; else docker compose up -d 2>/dev/null || true; fi")
    fi
    if (cd "$VAGRANT_DIR" && vagrant status helium 2>/dev/null | grep -q "running"); then
        echo "  -> Starting Docker Compose in Helium VM..."
        (cd "$VAGRANT_DIR" && vagrant ssh helium -c "if [ -d /var/www/helium ]; then cd /var/www/helium && docker compose up -d; else docker compose up -d 2>/dev/null || true; fi")
    fi
else
    echo "[INFO] Skipping Docker Compose startup inside VMs (Default behavior. Use --systems to enable)."
fi

# 1. Reset BOCA Database (PostgreSQL)
echo "[1/2] Seeding BOCA database at $BOCA_IP..."
if command -v vagrant &> /dev/null && (cd "$VAGRANT_DIR" && vagrant status boca 2>/dev/null | grep -q "running"); then
    (cd "$VAGRANT_DIR" && vagrant ssh boca -c "docker exec -i boca-db psql -U boca boca") < "$SCRIPT_DIR/boca/01_seed_benchmark.sql"
    echo "  ✔ BOCA PostgreSQL seeded successfully."
else
    echo "  ⚠ Vagrant VM 'boca' not running or not accessible. Skipping live execution."
fi

# 2. Reset Helium Database (MySQL)
echo "[2/2] Seeding Helium database at $HELIUM_IP..."
if command -v vagrant &> /dev/null && (cd "$VAGRANT_DIR" && vagrant status helium 2>/dev/null | grep -q "running"); then
    (cd "$VAGRANT_DIR" && vagrant ssh helium -c "docker exec -i helium-db mysql -u helium -psecret helium") < "$SCRIPT_DIR/helium/01_seed_benchmark.sql"
    echo "  ✔ Helium MySQL seeded successfully."
else
    echo "  ⚠ Vagrant VM 'helium' not running or not accessible. Skipping live execution."
fi

echo "================================================================="
echo " Parity Reset Complete! Ready for Locust Load Test."
echo "================================================================="
