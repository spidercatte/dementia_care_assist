#!/bin/bash
set -e

# ==============================================================================
# DementiaCare Coach Production Backend Deployment Script
# ==============================================================================

WORKSPACE_DIR="/workspaces/dementia_care_assist"
TERRAFORM_DIR="$WORKSPACE_DIR/adk-agent-scaffold/deployment/terraform/single-project"
VARS_FILE="$TERRAFORM_DIR/vars/env.tfvars"

echo "=== Starting DementiaCare Coach Production Backend Redeployment ==="

# 1. Parse configuration from tfvars
if [ ! -f "$VARS_FILE" ]; then
    echo "Error: env.tfvars not found at $VARS_FILE"
    exit 1
fi

PROJECT_NAME=$(grep -E '^\s*project_name\s*=' "$VARS_FILE" | cut -d'"' -f2)
PROJECT_ID=$(grep -E '^\s*project_id\s*=' "$VARS_FILE" | cut -d'"' -f2)
REGION=$(grep -E '^\s*region\s*=' "$VARS_FILE" | cut -d'"' -f2)

if [ -z "$PROJECT_ID" ] || [ -z "$PROJECT_NAME" ] || [ -z "$REGION" ]; then
    echo "Error: Failed to parse project details from $VARS_FILE"
    exit 1
fi

echo "--> Configuration Parsed:"
echo "    Project Name: $PROJECT_NAME"
echo "    Project ID:   $PROJECT_ID"
echo "    Region:       $REGION"
echo ""

# 2. Check GCP Authentication & Project Setting
echo "--> Configuring gcloud project..."
gcloud config set project "$PROJECT_ID"

# 3. Configure Docker credential helper
echo "--> Authenticating Docker with GCR..."
gcloud auth configure-docker -q

# 4. Build and push the Backend Docker image
echo "--> Building Backend Docker Image..."
docker build -t "gcr.io/$PROJECT_ID/$PROJECT_NAME-backend:latest" "$WORKSPACE_DIR/backend"

echo "--> Pushing Backend Docker Image to GCR..."
docker push "gcr.io/$PROJECT_ID/$PROJECT_NAME-backend:latest"

# 5. Direct Deployment to Cloud Run
echo "--> Triggering Cloud Run update for Backend..."
gcloud run deploy "$PROJECT_NAME-backend" \
    --image="gcr.io/$PROJECT_ID/$PROJECT_NAME-backend:latest" \
    --region="$REGION"

echo "=== Backend Deployment Completed Successfully! ==="
