#!/bin/bash
set -e

# DementiaCare Coach Setup Script
# Installs backend virtual environment, backend dependencies, and frontend packages.

WORKSPACE_DIR="/workspaces/dementia_care_assist"
echo "=== Setting up DementiaCare Coach in $WORKSPACE_DIR ==="

# Check if environment is already setup to skip installation
if [ "$1" != "--force" ] && [ "$1" != "-f" ]; then
    if [ -f "$WORKSPACE_DIR/backend/.env" ] && [ -d "$WORKSPACE_DIR/frontend/node_modules" ] && command -v poetry &>/dev/null && (cd "$WORKSPACE_DIR/backend" && poetry run python -c "import fastapi, pydantic_settings, chromadb, google.genai" &>/dev/null); then
        echo "=== Environment already setup. Skipping dependency installation. ==="
        echo "Use '--force' or '-f' flag to force reinstall."
        exit 0
    fi
fi

# 1. Setup Backend
echo "--> Configuring Backend..."
cd "$WORKSPACE_DIR/backend"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed."
    exit 1
fi

echo "Setting up Poetry environment and installing dependencies..."
poetry env use 3.12
poetry run pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Note: Please update the GEMINI_API_KEY inside backend/.env if you want to use the live AI features instead of Mock Mode."
else
    echo ".env file already exists."
fi

# 2. Setup Frontend
echo "--> Configuring Frontend..."
cd "$WORKSPACE_DIR/frontend"

if [ -f "package.json" ]; then
    echo "Installing frontend dependencies..."
    npm install
else
    echo "Error: package.json not found in frontend directory!"
    exit 1
fi

echo "=== Setup Completed Successfully! ==="
