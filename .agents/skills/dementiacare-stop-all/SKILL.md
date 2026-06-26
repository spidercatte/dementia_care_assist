---
name: dementiacare-stop-all
description: Use when stopping both the backend and frontend for the DementiaCare Coach application in one go.
metadata:
  category: automation
  triggers: stop dementia care app, stop all dementia care, kill dementia care, shut down dementia care
---

# DementiaCare Coach Stop All Skill

This skill stops all running DementiaCare Coach services: the FastAPI backend (port 8000) and the Vite frontend dev server (port 5173).

## Instructions

Run the existing cleanup script from the project root:

```bash
bash /workspaces/dementia_care_assist/scripts/cleanup_ports.sh
```

If the script is unavailable, stop each service manually:

1. **Stop backend (port 8000)**
   ```bash
   lsof -t -i:8000 | xargs kill -9 2>/dev/null || echo "Nothing running on port 8000"
   ```

2. **Stop frontend (port 5173)**
   ```bash
   lsof -t -i:5173 | xargs kill -9 2>/dev/null || echo "Nothing running on port 5173"
   ```

3. **Verify both ports are free**
   ```bash
   lsof -i :8000 -i :5173
   ```
   No output means both services have stopped successfully.
