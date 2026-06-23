#!/bin/bash
set -e

# DementiaCare Coach Setup Script
# Installs backend virtual environment, backend dependencies, and frontend packages.

WORKSPACE_DIR="/workspaces/dementia_care_assist"
echo "=== Setting up DementiaCare Coach in $WORKSPACE_DIR ==="

# 1. Setup Backend
echo "--> Configuring Backend..."
cd "$WORKSPACE_DIR/backend"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

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
