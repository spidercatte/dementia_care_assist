---
name: dementiacare-setup
description: Use when setting up the environment or installing dependencies for the DementiaCare Coach application.
metadata:
  category: automation
  triggers: setup dementia care, install dementia care dependencies, prepare dementia care env
---

# DementiaCare Coach Setup Skill

This skill automates the installation of dependencies and initialization of environments for both the backend and frontend components.

## Instructions

1. Execute the workspace setup script using the `run_command` tool:
   ```bash
   ./scripts/setup.sh
   ```
2. Verify that:
   - `backend/venv` exists and contains the python packages.
   - `backend/.env` exists.
   - `frontend/node_modules` exists.
