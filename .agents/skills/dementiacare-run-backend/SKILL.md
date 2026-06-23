---
name: dementiacare-run-backend
description: Use when starting the FastAPI backend development server for the DementiaCare Coach application.
metadata:
  category: automation
  triggers: run backend, start backend, start fastapi backend
---

# DementiaCare Coach Run Backend Skill

This skill automates starting the FastAPI backend server using the run script.

## Instructions

1. Start the backend by executing the run backend script using the `run_command` tool.
   Use a `WaitMsBeforeAsync` value of `500` ms (or let it run in the background as an asynchronous task):
   ```bash
   /workspaces/dementia_care_assist/scripts/run_backend.sh
   ```
2. Verify that the server is up by checking the health endpoint or uvicorn logs:
   - Check http://localhost:8000/health
