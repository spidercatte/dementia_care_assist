---
name: dementiacare-run-frontend
description: Use when starting the Vite React frontend web application for the DementiaCare Coach application.
metadata:
  category: automation
  triggers: run frontend, start frontend, start vite frontend
---

# DementiaCare Coach Run Frontend Skill

This skill automates starting the Vite development server using the run script.

## Instructions

1. Start the frontend by executing the run frontend script using the `run_command` tool.
   Use a `WaitMsBeforeAsync` value of `500` ms (or let it run in the background as an asynchronous task):
   ```bash
   ./scripts/run_frontend.sh
   ```
2. Verify that the server is up:
   - Check http://localhost:5173
