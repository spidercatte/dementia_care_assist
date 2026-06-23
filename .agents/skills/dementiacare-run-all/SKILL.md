---
name: dementiacare-run-all
description: Use when setting up, seeding, and starting both the backend and frontend for the DementiaCare Coach application in one go.
metadata:
  category: automation
  triggers: start dementia care app, run all dementia care, boot dementia care, setup and run dementia care
---

# DementiaCare Coach Run All Skill

This skill automates the full boot sequence of the DementiaCare Coach application: setting up environments, starting the backend, seeding the RAG database, and starting the frontend.

## Instructions

1. **Step 1: Environment Setup**
   Run the setup script synchronously:
   ```bash
   /workspaces/dementia_care_assist/scripts/setup.sh
   ```

2. **Step 2: Start backend**
   Run the backend start script asynchronously. Use `WaitMsBeforeAsync` value of `500` ms (or let it run in the background as an asynchronous task):
   ```bash
   /workspaces/dementia_care_assist/scripts/run_backend.sh
   ```

3. **Step 3: Seed Guidelines (RAG)**
   Run the seed RAG script synchronously to populate ChromaDB:
   ```bash
   /workspaces/dementia_care_assist/scripts/seed_rag.sh
   ```

4. **Step 4: Start frontend**
   Run the frontend start script asynchronously. Use `WaitMsBeforeAsync` value of `500` ms (or let it run in the background as an asynchronous task):
   ```bash
   /workspaces/dementia_care_assist/scripts/run_frontend.sh
   ```

5. **Step 5: Verification**
   Verify the services are live:
   - Check http://localhost:8000/health (Backend health check)
   - Check http://localhost:5173 (Frontend home page)
