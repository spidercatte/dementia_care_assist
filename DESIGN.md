# DementiaCare Coach — System Design & Architecture Reference

This document serves as the architectural blueprint and directory mapping for the DementiaCare Coach application. When working with coding agents, this file acts as a high-level cache to understand the codebase structure and data flows without needing to search directories from scratch.

---

## 1. Directory Structure

- `frontend/` — React SPA built with Vite
  - `src/App.jsx` — Core interactive interface containing main styling, recording interfaces, simulation screens, and view state management.
- `backend/` — FastAPI Server
  - `app/main.py` — Main entrypoint: defines routes, server lifecycles, startup cleaning tasks, and DB initialization.
  - `app/database.py` — SQLite client access wrapper.
  - `app/rag.py` — Vector search client interfaces querying the local ChromaDB vector store.
  - `app/mock_responses.py` — Fallback responses used for offline mode, testing, and robust fail-overs.
  - `app/agents/` — Autonomous AI coaching, analysis, and simulation agents:
    - `orchestrator.py` — **Main Flow Controller**. Manages video/audio uploads, checks surrogate consent, runs profile enrichment, queries clinical guidelines via RAG, coordinates agent sub-calls, and logs verification results.
    - `caregiver_coaching.py` — Generates validation/redirection feedback and "Try Saying / Avoid Saying" dialogue scripts.
    - `conversational_coach.py` — Back-and-forth conversational coach agent for ongoing caregiver support.
    - `simulator.py` — Simulates agitated patient responses (high/medium/low agitation) based on selected care scenarios to let caregivers practice communication techniques.
    - `validation.py` / `safety_escalation.py` / `care_guidance.py` / `profile_enricher.py` — Micro-agents verifying input formats, scanning for clinical safety risks, retrieving protocol lookups, and packing patient data.
- `common/` — Shared database clients, configurations, and core utilities.
- `scripts/` — Automated tasks:
  - `deploy_prod.sh` — Orchestrates production deployment to Google Cloud Run.
  - `seed_rag.py` — Populates ChromaDB vector store with clinical protocol guidelines.
  - `run_all.sh` / `stop_all.sh` — Dev-environment management.

---

## 2. Core Data Flows

### A. Media Upload & Analysis Flow
1. **Intake**: Caregiver uploads video/audio file or text description of a patient behavioral challenge.
2. **Surrogate Consent Gating** (`orchestrator.py` & `main.py`):
   - System queries `consent_records` in SQLite for the patient name.
   - Verifies if the legal decision-maker (POA/guardian) has approved the specific media scope (`text`, `audio`, or `video`).
   - Logs the verification event (`GRANTED` or `REJECTED`) to `consent_audit_logs`.
   - If consent is missing, aborts request immediately with a validation error.
3. **Data Enrichment**: Orchestrator fetches patient profiles (history, cognitive stage, triggers) from the SQLite database.
4. **Clinical RAG Retrieval**: Orchestrator queries ChromaDB for relevant clinical guidelines (e.g., validation therapy, redirection, communication safety).
5. **AI Analysis & Coaching** (`caregiver_coaching.py`):
   - Uploads file securely to Gemini File API.
   - Instructs Gemini 1.5 Pro to analyze body language, agitation cues, caregiver posture, and tone of voice.
   - Fuses clinical guidelines, profile metadata, and Gemini analysis to generate structural feedback:
     - *Dementia Agitation Level* assessment.
     - *De-escalation Feedback* (what went well, what could improve).
     - *Try saying / Avoid saying* concrete dialogue suggestions.
     - *Clinical Guidance References* linking back to source care rules.
6. **Immediate Lifecycle Cleanup**: Delete command executed in a `finally` block to instantly purge the media file from local storage and the Gemini File API.

### B. Patient Agitation Simulation Flow
1. **Start**: Caregiver selects a patient scenario (e.g., "wandering," "repetitive questions").
2. **Simulation System** (`simulator.py`):
   - Sets up patient simulator agent preloaded with the specific patient's profile and baseline agitation.
   - Generates realistic, emotionally complex replies reflecting dementia behaviors.
   - Tracks caregiver's responses, calculating validation/redirection quality and calculating dynamically updating agitation metrics (1-100%).

---

## 3. Database Schema Reference

SQLite database tracking state and compliance logs:

- `patients` — Profiles (id, name, age, cognitive_stage, background, triggers, preferences).
- `interactions` — Historical caregiver interactions and generated coach recommendations.
- `consent_records` — Compliance tracking:
  - `patient_name` (TEXT)
  - `granted_by` (TEXT) - Name of POA/Legal Guardian granting surrogate consent
  - `scope` (TEXT) - Allowed media: `'text'`, `'audio'`, `'video'`
  - `granted_at` (TEXT) - Timestamp
  - `revoked_at` (TEXT, Nullable) - Revocation timestamp
- `consent_audit_logs` — Immutable verification history:
  - `patient_name` (TEXT)
  - `required_scope` (TEXT)
  - `allowed_scope` (TEXT)
  - `granted_by` (TEXT)
  - `result` (TEXT) - `'GRANTED'` or `'REJECTED'`
  - `timestamp` (TEXT)
