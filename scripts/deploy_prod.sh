#!/bin/bash
set -e

# ==============================================================================
# DementiaCare Coach Production Deployment Script
# ==============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
TERRAFORM_DIR="$WORKSPACE_DIR/adk-agent-scaffold/deployment/terraform/single-project"
VARS_FILE="$TERRAFORM_DIR/vars/env.tfvars"

echo "=== Starting DementiaCare Coach Production Deployment ==="

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

# 4. Enable Google Cloud Services APIs
echo "--> Enabling required GCP APIs..."
gcloud services enable \
    discoveryengine.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    aiplatform.googleapis.com \
    iam.googleapis.com \
    compute.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com

# Load keys and generate secure production credentials if not provided
if [ -z "$USER_API_KEY" ]; then
    USER_API_KEY=$(openssl rand -hex 16)
    echo "--> Generated secure User Access Key: $USER_API_KEY"
fi
if [ -z "$ADMIN_API_KEY" ]; then
    ADMIN_API_KEY=$(openssl rand -hex 16)
    echo "--> Generated secure Admin Access Key: $ADMIN_API_KEY"
fi

if [ -z "$GEMINI_API_KEY" ]; then
    if [ -f "$WORKSPACE_DIR/backend/.env" ]; then
        GEMINI_API_KEY=$(grep -E '^\s*GEMINI_API_KEY\s*=' "$WORKSPACE_DIR/backend/.env" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    fi
fi

if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_gemini_api_key_here" ]; then
    echo "Error: GEMINI_API_KEY must be set in your environment or in backend/.env to deploy."
    exit 1
fi

# 5. Prepare production.tf for single-project deployment
echo "--> Preparing Terraform configuration..."
cp "$WORKSPACE_DIR/adk-agent-scaffold/deployment/terraform/production.tf" "$TERRAFORM_DIR/production.tf"
# Replace var.prod_project_id with var.project_id in single-project production.tf
sed -i '' 's/var.prod_project_id/var.project_id/g' "$TERRAFORM_DIR/production.tf"

# 6. Build and push the Backend & MCP Docker images via Cloud Build
echo "--> Creating temporary Cloud Build config for Backend..."
cat <<'EOF' > "$WORKSPACE_DIR/backend_cloudbuild.yaml"
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-f', 'backend/Dockerfile',
      '-t', 'gcr.io/$_PROJECT_ID/$_PROJECT_NAME-backend:latest',
      '.'
    ]
images:
  - 'gcr.io/$_PROJECT_ID/$_PROJECT_NAME-backend:latest'
EOF

echo "--> Building Backend Docker Image via Cloud Build..."
gcloud builds submit \
    --config="$WORKSPACE_DIR/backend_cloudbuild.yaml" \
    --substitutions=_PROJECT_ID="$PROJECT_ID",_PROJECT_NAME="$PROJECT_NAME" \
    "$WORKSPACE_DIR"
rm "$WORKSPACE_DIR/backend_cloudbuild.yaml"

echo "--> Creating temporary Cloud Build config for MCP..."
cat <<'EOF' > "$WORKSPACE_DIR/mcp_cloudbuild.yaml"
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-f', 'mcp_server/Dockerfile',
      '-t', 'gcr.io/$_PROJECT_ID/$_PROJECT_NAME-mcp:latest',
      '.'
    ]
images:
  - 'gcr.io/$_PROJECT_ID/$_PROJECT_NAME-mcp:latest'
EOF

echo "--> Building MCP Server Docker Image via Cloud Build..."
gcloud builds submit \
    --config="$WORKSPACE_DIR/mcp_cloudbuild.yaml" \
    --substitutions=_PROJECT_ID="$PROJECT_ID",_PROJECT_NAME="$PROJECT_NAME" \
    "$WORKSPACE_DIR"
rm "$WORKSPACE_DIR/mcp_cloudbuild.yaml"

# 7. Initialize Terraform and Deploy Backend/MCP/PostgreSQL to retrieve URL
echo "--> Bootstrapping Terraform database, backend & mcp..."
cd "$TERRAFORM_DIR"
terraform init

echo "--> Applying PostgreSQL, Backend, and MCP Cloud Run configurations..."
terraform apply \
    -target=google_service_account.app_sa \
    -target=google_project_iam_member.app_sa_roles \
    -target=google_project_iam_member.app_sa_secret_accessor \
    -target=google_sql_database_instance.postgres \
    -target=google_sql_database.dementia_care_db \
    -target=google_sql_user.db_user \
    -target=google_secret_manager_secret_version.gemini_api_key_version \
    -target=google_secret_manager_secret_version.user_api_key_version \
    -target=google_secret_manager_secret_version.admin_api_key_version \
    -target=google_secret_manager_secret_version.db_password_version \
    -target=google_cloud_run_v2_service.backend_service \
    -target=google_cloud_run_v2_service.mcp_service \
    -var="gemini_api_key=$GEMINI_API_KEY" \
    -var="user_api_key=$USER_API_KEY" \
    -var="admin_api_key=$ADMIN_API_KEY" \
    -var-file=vars/env.tfvars \
    -auto-approve

# Retrieve the active Backend and MCP URLs from Terraform outputs
echo "--> Retrieving Service URLs..."
BACKEND_URL=$(terraform output -raw backend_url)
MCP_URL=$(terraform output -raw mcp_url)
echo "    Backend URL resolved to: $BACKEND_URL"
echo "    MCP URL resolved to:     $MCP_URL"

# 8. Build and push the Frontend Docker image using the Backend URL and User API Key via Cloud Build
echo "--> Creating temporary Cloud Build config for Frontend..."
cat <<'EOF' > "$WORKSPACE_DIR/frontend/frontend_cloudbuild.yaml"
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t', 'gcr.io/$_PROJECT_ID/$_PROJECT_NAME-frontend:latest',
      '--build-arg', 'VITE_BACKEND_URL=$_VITE_BACKEND_URL',
      '--build-arg', 'VITE_USER_API_KEY=$_VITE_USER_API_KEY',
      '.'
    ]
images:
  - 'gcr.io/$_PROJECT_ID/$_PROJECT_NAME-frontend:latest'
EOF

echo "--> Building Frontend Docker Image via Cloud Build with Backend URL: $BACKEND_URL..."
gcloud builds submit \
    --config="$WORKSPACE_DIR/frontend/frontend_cloudbuild.yaml" \
    --substitutions=_PROJECT_ID="$PROJECT_ID",_PROJECT_NAME="$PROJECT_NAME",_VITE_BACKEND_URL="$BACKEND_URL",_VITE_USER_API_KEY="$USER_API_KEY" \
    "$WORKSPACE_DIR/frontend"
rm "$WORKSPACE_DIR/frontend/frontend_cloudbuild.yaml"

# 9. Complete full Terraform Apply
echo "--> Finalizing deployment of all services (including Frontend Cloud Run)..."
terraform apply \
    -var="gemini_api_key=$GEMINI_API_KEY" \
    -var="user_api_key=$USER_API_KEY" \
    -var="admin_api_key=$ADMIN_API_KEY" \
    -var-file=vars/env.tfvars \
    -auto-approve

FRONTEND_URL=$(terraform output -raw frontend_url)

# 10. Deploy the ADK Agent (Vertex AI Reasoning Engine)
echo "--> Deploying ADK Agent to Vertex AI Reasoning Engine..."
cd "$WORKSPACE_DIR/adk-agent-scaffold"
# Set environment variable BACKEND_URL for the deployed agent to the MCP Server URL
export BACKEND_URL="$MCP_URL"
agents-cli deploy --no-confirm-project

echo ""
echo "=== Deployment Completed Successfully! ==="
echo "    Frontend URL:      $FRONTEND_URL"
echo "    Backend URL:       $BACKEND_URL"
echo "    MCP URL:           $MCP_URL"
echo "    User Access Key:   $USER_API_KEY"
echo "    Admin Access Key:  $ADMIN_API_KEY"
echo "=========================================================================="
