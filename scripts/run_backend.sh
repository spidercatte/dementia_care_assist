#!/bin/bash

# DementiaCare Coach Run Backend Script
# Starts the FastAPI backend using uvicorn.

WORKSPACE_DIR="/workspaces/dementia_care_assist"
echo "=== Starting DementiaCare Coach Backend ==="
cd "$WORKSPACE_DIR/backend"

# Check if poetry is installed
export PYTHONPATH="$WORKSPACE_DIR"
exec poetry run uvicorn app.main:app --reload --port 8000
