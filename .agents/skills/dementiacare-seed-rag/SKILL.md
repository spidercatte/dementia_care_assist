---
name: dementiacare-seed-rag
description: Use when seeding or populating the ChromaDB vector store guidelines for the DementiaCare Coach application.
metadata:
  category: automation
  triggers: seed dementia guidelines, populate chroma db dementia, seed dementia care rag
---

# DementiaCare Coach Seed RAG Skill

This skill automates the seeding process of the ChromaDB RAG Guidelines database.

## Instructions

1. Execute the seeding script using the `run_command` tool:
   ```bash
   /workspaces/dementia_care_assist/scripts/seed_rag.sh
   ```
2. Verify that:
   - The script output prints `=== Seeding Completed! ===` and does not throw errors.
