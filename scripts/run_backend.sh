#!/bin/bash

# DementiaCare Coach Run Backend Script
# Starts the FastAPI backend using uvicorn.

WORKSPACE_DIR="/workspaces/dementia_care_assist"
echo "=== Starting DementiaCare Coach Backend ==="
cd "$WORKSPACE_DIR/backend"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed."
    exit 1
fi

exec poetry run uvicorn app.main:app --reload --port 8000
