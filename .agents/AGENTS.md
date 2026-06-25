# Project-Scoped Rules for DementiaCare Coach

## Production Deployment Rules
- **Do not read all files**: When the user requests a deployment to production, do NOT read, scan, or analyze frontend, backend, or database source files.
- **Use the deployment script**: Run the existing deployment script at [deploy_prod.sh](file:///workspaces/dementia_care_assist/scripts/deploy_prod.sh) directly.
- **Verification**: If you need to verify changes, only inspect files explicitly mentioned by the user in the prompt.
