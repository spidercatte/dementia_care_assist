#!/bin/bash

# DementiaCare Coach Run Backend Script
# Starts the FastAPI backend using uvicorn.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
echo "=== Starting DementiaCare Coach Backend ==="
cd "$WORKSPACE_DIR/backend"

# Check if poetry is installed
export PYTHONPATH="$WORKSPACE_DIR"
exec poetry run uvicorn app.main:app --reload --port 8000
