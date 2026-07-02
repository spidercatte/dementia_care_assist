#!/bin/bash
set -e

# DementiaCare Coach Seed RAG Script
# Seeds ChromaDB with local dementia care guidelines from the markdown file.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
echo "=== Seeding DementiaCare Coach RAG Guidelines ==="
cd "$WORKSPACE_DIR/backend"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed."
    exit 1
fi

export PYTHONPATH="$WORKSPACE_DIR"
poetry run python -c "from app.rag import seed_default_guidelines; seed_default_guidelines()"
echo "=== Seeding Completed! ==="
