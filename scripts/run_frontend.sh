#!/bin/bash

# DementiaCare Coach Run Frontend Script
# Starts the Vite development server for the React frontend.

WORKSPACE_DIR="/workspaces/dementia_care_assist"
echo "=== Starting DementiaCare Coach Frontend ==="
cd "$WORKSPACE_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "node_modules not found. Running npm install first..."
    npm install
fi

exec npm run dev
