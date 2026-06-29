# Project-Scoped Rules for DementiaCare Coach

## Production Deployment Rules
- **Do not read all files**: When the user requests a deployment to production, do NOT read, scan, or analyze frontend, backend, or database source files.
- **Use the deployment script**: Run the existing deployment script at [deploy_prod.sh](file:///workspaces/dementia_care_assist/scripts/deploy_prod.sh) directly.
- **Verification**: If you need to verify changes, only inspect files explicitly mentioned by the user in the prompt.

## Context & Token Efficiency Rules
- **Avoid Directory Scans**: Do not run recursive directory listings or read large blocks of source files from scratch unless explicitly necessary.
- **Direct Entry Points**:
  - Frontend: [App.jsx](file:///workspaces/dementia_care_assist/frontend/src/App.jsx)
  - FastAPI Backend: [main.py](file:///workspaces/dementia_care_assist/backend/app/main.py)
  - Orchestrator/Agents: [orchestrator.py](file:///workspaces/dementia_care_assist/backend/app/agents/orchestrator.py)
- **Codebase Orientation**: Always read [DESIGN.md](file:///workspaces/dementia_care_assist/DESIGN.md) first to understand the architecture, database schema, and data flows before reading any other codebase files.
