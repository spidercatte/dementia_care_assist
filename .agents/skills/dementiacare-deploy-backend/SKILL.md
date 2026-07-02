---
name: dementiacare-deploy-backend
description: Use when building and deploying only the backend service to the production GCP environment.
metadata:
  category: deployment
  triggers: deploy backend prod, redeploy backend prod, deploy production backend, deploy backend to prod
---

# DementiaCare Coach Deploy Backend Skill

This skill builds and deploys only the backend container image to the Google Cloud Run production environment.

## Instructions

1. Run the backend deployment script:
   ```bash
   ./scripts/deploy_prod_backend.sh
   ```
