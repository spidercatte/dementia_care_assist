#!/bin/bash
set -e

# DementiaCare Coach Setup Script
# Installs backend virtual environment, backend dependencies, and frontend packages.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
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
else
    echo ".env file already exists."
fi

# Auto-copy GEMINI_API_KEY from root .env to backend/.env if root .env exists
python3 -c "
import os
root_env = '$WORKSPACE_DIR/.env'
backend_env = '$WORKSPACE_DIR/backend/.env'
if os.path.exists(root_env) and os.path.exists(backend_env):
    with open(root_env, 'r') as f:
        root_lines = f.readlines()
    key = None
    for line in root_lines:
        if line.strip().startswith('GEMINI_API_KEY='):
            key = line.strip().split('=', 1)[1].strip('\"\'')
            break
    if key and key != 'your_gemini_api_key_here':
        with open(backend_env, 'r') as f:
            content = f.read()
        if 'GEMINI_API_KEY=your_gemini_api_key_here' in content:
            content = content.replace('GEMINI_API_KEY=your_gemini_api_key_here', f'GEMINI_API_KEY={key}')
            with open(backend_env, 'w') as f:
                f.write(content)
            print('--> Automatically copied GEMINI_API_KEY from root .env to backend/.env')
"

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
