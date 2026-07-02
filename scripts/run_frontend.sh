#!/bin/bash

# DementiaCare Coach Run Frontend Script
# Starts the Vite development server for the React frontend.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
echo "=== Starting DementiaCare Coach Frontend ==="
cd "$WORKSPACE_DIR/frontend"

if [ -n "$CODESPACE_NAME" ]; then
    export VITE_BACKEND_URL="https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
    echo "Detected Codespace: setting VITE_BACKEND_URL to $VITE_BACKEND_URL"
fi

if [ ! -d "node_modules" ]; then
    echo "node_modules not found. Running npm install first..."
    npm install
fi

exec npm run dev
