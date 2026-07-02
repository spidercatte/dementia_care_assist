---
name: dementiacare-deploy-frontend
description: Use when building and deploying only the frontend UI service to the production GCP environment.
metadata:
  category: deployment
  triggers: deploy frontend prod, redeploy frontend prod, deploy production frontend, deploy ui prod, deploy frontend to prod
---

# DementiaCare Coach Deploy Frontend Skill

This skill builds and deploys only the frontend UI container image to the Google Cloud Run production environment. It automatically resolves the active Backend URL and API Access Keys dependencies before building.

## Instructions

1. Run the frontend deployment script:
   ```bash
   ./scripts/deploy_prod_frontend.sh
   ```
