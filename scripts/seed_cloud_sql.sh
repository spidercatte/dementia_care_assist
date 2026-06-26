#!/bin/bash
set -euo pipefail

# ==============================================================================
# DementiaCare Coach — Cloud SQL Seed Script
# Seeds the production PostgreSQL database with patient profiles.
# Connects via Cloud SQL Auth Proxy (started automatically via gcloud).
# Safe to re-run: uses upsert logic (INSERT ... ON CONFLICT DO UPDATE).
# ==============================================================================

WORKSPACE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS_DIR="$WORKSPACE_DIR/scripts"

# --- Configuration (override via environment variables) ---
PROJECT_ID="${GCP_PROJECT_ID:-adi-researc}"
REGION="${GCP_REGION:-us-east1}"
DB_NAME="${DB_NAME:-dementia_care}"
DB_USER="${DB_USER:-dementia_admin}"
PROXY_PORT="${PROXY_PORT:-5433}"

echo "============================================================"
echo " DementiaCare Coach — Cloud SQL Seed"
echo "============================================================"
echo " Project ID : $PROJECT_ID"
echo " Region     : $REGION"
echo " DB Name    : $DB_NAME"
echo " DB User    : $DB_USER"
echo "============================================================"
echo ""

# --- Dependency checks ---
for cmd in gcloud python3 psql; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Warning: '$cmd' not found (optional for this script)."
    fi
done

# --- GCP auth check ---
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q "@"; then
    echo "Error: No active gcloud credentials. Run: gcloud auth application-default login"
    exit 1
fi

# --- Discover Cloud SQL instance ---
echo "--> Discovering Cloud SQL instance in project $PROJECT_ID..."
INSTANCE_NAME=$(gcloud sql instances list \
    --project="$PROJECT_ID" \
    --format="value(name)" \
    --filter="databaseVersion:POSTGRES_15" \
    2>/dev/null | head -1)

if [ -z "$INSTANCE_NAME" ]; then
    echo "Error: No PostgreSQL Cloud SQL instance found in project $PROJECT_ID."
    echo "       Deploy infrastructure first: scripts/deploy_prod.sh"
    exit 1
fi

CONNECTION_NAME=$(gcloud sql instances describe "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --format="value(connectionName)")

echo "    Found instance: $INSTANCE_NAME"
echo "    Connection name: $CONNECTION_NAME"
echo ""

# --- Get DB password from Secret Manager ---
echo "--> Fetching DB password from Secret Manager..."
PROJECT_NAME=$(gcloud sql instances describe "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --format="value(name)" | sed 's/-postgres-.*//')

SECRET_ID="${PROJECT_NAME}-db-password"
DB_PASSWORD=$(gcloud secrets versions access latest \
    --secret="$SECRET_ID" \
    --project="$PROJECT_ID" 2>/dev/null || echo "")

if [ -z "$DB_PASSWORD" ]; then
    echo "Warning: Could not fetch DB password from Secret Manager."
    echo "         Set DB_PASSWORD environment variable manually."
    DB_PASSWORD="${DB_PASSWORD:-}"
fi
echo "    Password retrieved."
echo ""

# --- Start Cloud SQL Auth Proxy ---
echo "--> Starting Cloud SQL Auth Proxy on port $PROXY_PORT..."
PROXY_PID=""

if command -v cloud-sql-proxy &>/dev/null; then
    cloud-sql-proxy "$CONNECTION_NAME" --port="$PROXY_PORT" &
    PROXY_PID=$!
    echo "    Proxy started (PID: $PROXY_PID)"
    sleep 3
else
    echo "    cloud-sql-proxy not found — trying gcloud sql connect fallback..."
    echo "    Install cloud-sql-proxy: https://cloud.google.com/sql/docs/postgres/connect-auth-proxy"
    echo ""
    echo "    Alternatively, run the seed script directly with env vars:"
    echo "      DB_HOST=127.0.0.1 DB_PORT=5432 DB_USER=$DB_USER DB_PASSWORD=<pass> DB_NAME=$DB_NAME \\"
    echo "      python3 $SCRIPTS_DIR/seed_cloud_sql.py"
    exit 1
fi

# --- Ensure proxy is killed on exit ---
cleanup() {
    if [ -n "$PROXY_PID" ]; then
        echo ""
        echo "--> Stopping Cloud SQL Auth Proxy (PID: $PROXY_PID)..."
        kill "$PROXY_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

# --- Run seed script ---
echo "--> Running patient data seed script..."
DB_HOST="127.0.0.1" \
DB_PORT="$PROXY_PORT" \
DB_USER="$DB_USER" \
DB_PASSWORD="$DB_PASSWORD" \
DB_NAME="$DB_NAME" \
python3 "$SCRIPTS_DIR/seed_cloud_sql.py"

echo ""
echo "============================================================"
echo " Seeding Complete!"
echo " Patient profiles (Maria, Arthur) are now in Cloud SQL."
echo "============================================================"
