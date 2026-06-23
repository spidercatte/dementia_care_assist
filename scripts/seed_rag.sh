#!/bin/bash
set -e

# DementiaCare Coach Seed RAG Script
# Seeds ChromaDB with local dementia care guidelines from the markdown file.

WORKSPACE_DIR="/workspaces/dementia_care_assist"
echo "=== Seeding DementiaCare Coach RAG Guidelines ==="
cd "$WORKSPACE_DIR/backend"

if [ ! -d "venv" ]; then
    echo "Error: Virtual environment 'venv' not found. Please run scripts/setup.sh first."
    exit 1
fi

source venv/bin/activate
export PYTHONPATH=.
python -c "from app.rag import seed_default_guidelines; seed_default_guidelines()"
echo "=== Seeding Completed! ==="
