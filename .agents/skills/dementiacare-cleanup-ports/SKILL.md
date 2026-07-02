---
name: dementiacare-cleanup-ports
description: Use when you need to free up local ports (8000 and 5173) by killing any active processes running on them.
metadata:
  category: utility
  triggers: cleanup ports, kill ports, free ports, stop local server, clean ports, release ports
---

# DementiaCare Coach Cleanup Ports Skill

This skill stops any running processes listening on port 8000 (backend) or port 5173 (frontend) to allow for a clean local redeployment.

## Instructions

1. Run the port cleanup script:
   ```bash
   ./scripts/cleanup_ports.sh
   ```
