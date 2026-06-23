#!/bin/bash

# DementiaCare Coach Run Backend Script
# Starts the FastAPI backend using uvicorn.

WORKSPACE_DIR="/workspaces/dementia_care_assist"
echo "=== Starting DementiaCare Coach Backend ==="
cd "$WORKSPACE_DIR/backend"

if [ ! -d "venv" ]; then
    echo "Error: Virtual environment 'venv' not found. Please run scripts/setup.sh first."
    exit 1
fi

source venv/bin/activate
exec uvicorn app.main:app --reload --port 8000
