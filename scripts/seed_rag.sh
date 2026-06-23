#!/bin/bash
set -e

# DementiaCare Coach Seed RAG Script
# Seeds ChromaDB with local dementia care guidelines from the markdown file.

WORKSPACE_DIR="/workspaces/dementia_care_assist"
echo "=== Seeding DementiaCare Coach RAG Guidelines ==="
cd "$WORKSPACE_DIR/backend"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed."
    exit 1
fi

export PYTHONPATH=.
poetry run python -c "from app.rag import seed_default_guidelines; seed_default_guidelines()"
echo "=== Seeding Completed! ==="
