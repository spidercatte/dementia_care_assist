#!/bin/bash
set -e

# ==============================================================================
# DementiaCare Coach Production Frontend Deployment Script
# ==============================================================================

WORKSPACE_DIR="/workspaces/dementia_care_assist"
TERRAFORM_DIR="$WORKSPACE_DIR/adk-agent-scaffold/deployment/terraform/single-project"
VARS_FILE="$TERRAFORM_DIR/vars/env.tfvars"

echo "=== Starting DementiaCare Coach Production Frontend Redeployment ==="

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

# 4. Automatically retrieve backend URL and User API Key
echo "--> Retrieving active Backend URL from Terraform outputs..."
if [ -d "$TERRAFORM_DIR" ]; then
    cd "$TERRAFORM_DIR"
    BACKEND_URL=$(terraform output -raw backend_url)
    cd "$WORKSPACE_DIR"
else
    echo "Error: Terraform directory not found."
    exit 1
fi

if [ -z "$BACKEND_URL" ]; then
    echo "Error: Could not retrieve Backend URL from Terraform output."
    exit 1
fi
echo "    Backend URL: $BACKEND_URL"

echo "--> Retrieving User API Key from Google Secret Manager..."
USER_API_KEY=$(gcloud secrets versions access latest --secret="$PROJECT_NAME-user-api-key" 2>/dev/null || true)

if [ -z "$USER_API_KEY" ]; then
    # Fallback to backend/.env if secret lookup fails
    if [ -f "$WORKSPACE_DIR/backend/.env" ]; then
        USER_API_KEY=$(grep -E '^\s*USER_API_KEY\s*=' "$WORKSPACE_DIR/backend/.env" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    fi
fi

if [ -z "$USER_API_KEY" ]; then
    echo "Error: USER_API_KEY could not be retrieved from Secret Manager or backend/.env"
    exit 1
fi

# 5. Build and push the Frontend Docker image
echo "--> Building Frontend Docker Image..."
docker build \
    --build-arg VITE_BACKEND_URL="$BACKEND_URL" \
    --build-arg VITE_USER_API_KEY="$USER_API_KEY" \
    -t "gcr.io/$PROJECT_ID/$PROJECT_NAME-frontend:latest" \
    "$WORKSPACE_DIR/frontend"

echo "--> Pushing Frontend Docker Image to GCR..."
docker push "gcr.io/$PROJECT_ID/$PROJECT_NAME-frontend:latest"

# 6. Direct Deployment to Cloud Run
echo "--> Triggering Cloud Run update for Frontend..."
gcloud run deploy "$PROJECT_NAME-frontend" \
    --image="gcr.io/$PROJECT_ID/$PROJECT_NAME-frontend:latest" \
    --region="$REGION"

echo "=== Frontend Deployment Completed Successfully! ==="
