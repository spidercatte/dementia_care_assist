#!/bin/bash
set -euo pipefail

# ==============================================================================
# DementiaCare Coach — Patient Profile Vertex AI Search Deployment Script
# Deploys patient profile documents to Google Cloud Vertex AI Search.
# Safe to re-run: existing datastore/bucket resources are reused.
# ==============================================================================

WORKSPACE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS_DIR="$WORKSPACE_DIR/scripts"
PATIENTS_DIR="$WORKSPACE_DIR/backend/data/patients"

# --- Configuration (override via environment variables) ---
PROJECT_ID="${GCP_PROJECT_ID:-adi-researc}"
LOCATION="${VERTEX_SEARCH_LOCATION:-global}"
DATASTORE_ID="${VERTEX_PATIENT_DATASTORE_ID:-dementia-care-patients}"
GCS_BUCKET="${GCS_BUCKET:-${PROJECT_ID}-dementia-rag}"
GCS_PREFIX="patients"

echo "============================================================"
echo " DementiaCare Coach — Patient Profile Vertex AI Search"
echo "============================================================"
echo " Project ID  : $PROJECT_ID"
echo " Location    : $LOCATION"
echo " Datastore ID: $DATASTORE_ID"
echo " GCS Bucket  : gs://$GCS_BUCKET"
echo " GCS Prefix  : $GCS_PREFIX"
echo "============================================================"
echo ""

# --- Dependency checks ---
for cmd in gcloud python3; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: '$cmd' is required but not installed."
        exit 1
    fi
done

if ! python3 -c "import google.cloud.discoveryengine_v1" 2>/dev/null; then
    echo "Installing google-cloud-discoveryengine..."
    pip3 install --quiet "google-cloud-discoveryengine>=0.11.0"
fi

# --- GCP auth check ---
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q "@"; then
    echo "Error: No active gcloud credentials. Run: gcloud auth application-default login"
    exit 1
fi

gcloud config set project "$PROJECT_ID" --quiet

# --- Enable required APIs ---
echo "--> Enabling required Google Cloud APIs..."
gcloud services enable \
    discoveryengine.googleapis.com \
    storage.googleapis.com \
    --project="$PROJECT_ID" \
    --quiet
echo "    APIs enabled."
echo ""

# --- Create GCS bucket if it doesn't exist ---
echo "--> Setting up GCS bucket: gs://$GCS_BUCKET"
if ! gcloud storage buckets describe "gs://$GCS_BUCKET" --project="$PROJECT_ID" &>/dev/null; then
    gcloud storage buckets create "gs://$GCS_BUCKET" \
        --project="$PROJECT_ID" \
        --location="US" \
        --uniform-bucket-level-access \
        --quiet
    echo "    Created bucket: gs://$GCS_BUCKET"
else
    echo "    Bucket already exists, reusing."
fi
echo ""

# --- Upload patient profile files to GCS ---
echo "--> Uploading patient profile documents to GCS..."
TXT_COUNT=$(find "$PATIENTS_DIR" -name "*.txt" | wc -l | tr -d ' ')
if [ "$TXT_COUNT" -eq 0 ]; then
    echo "Error: No patient profile files found in $PATIENTS_DIR"
    exit 1
fi

for f in "$PATIENTS_DIR"/*.txt; do
    gcloud storage cp "$f" "gs://$GCS_BUCKET/$GCS_PREFIX/$(basename "$f")" \
        --project="$PROJECT_ID" \
        --content-type="text/plain" \
        --quiet
done
echo "    Uploaded $TXT_COUNT patient profile files to gs://$GCS_BUCKET/$GCS_PREFIX/"
echo ""

# --- Create datastore and import documents via Python ---
echo "--> Creating Vertex AI Search datastore and importing documents..."
GCP_PROJECT_ID="$PROJECT_ID" \
VERTEX_SEARCH_LOCATION="$LOCATION" \
VERTEX_PATIENT_DATASTORE_ID="$DATASTORE_ID" \
GCS_BUCKET="$GCS_BUCKET" \
GCS_PREFIX="$GCS_PREFIX" \
python3 "$SCRIPTS_DIR/create_patient_datastore.py"

echo ""
echo "============================================================"
echo " Deployment Complete!"
echo "------------------------------------------------------------"
echo " Datastore path:"
echo "   projects/$PROJECT_ID/locations/$LOCATION/collections/default_collection/dataStores/$DATASTORE_ID"
echo ""
echo " Add to backend/.env.example or Terraform:"
echo "   VERTEX_PATIENT_DATASTORE_ID=$DATASTORE_ID"
echo "============================================================"
