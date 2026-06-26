# DementiaCare Coach
**An AI-Powered Caregiver Co-Pilot | Kaggle AI Agents Capstone — Agents for Good**

DementiaCare Coach helps family and clinical caregivers manage difficult dementia patient behaviors — agitation, confusion, medication refusal, wandering, and emotional distress — using evidence-based practices including Validation Therapy, Habilitation, and Teepa Snow's Positive Approach to Care.

> Built for the [AI Agents: Intensive Vibe Coding Capstone Project](https://www.kaggle.com/competitions/vibecoding-agents-capstone-project) on Kaggle.

---

## The Problem

Over 55 million people worldwide live with dementia. The majority are cared for at home by family members who receive little to no professional training. When a patient becomes agitated, refuses medication, or exhibits distressing behaviors, caregivers often respond intuitively — and frequently make the situation worse by correcting the patient's reality, arguing, or rushing them.

The result: escalating distress for the patient, caregiver burnout, and unnecessary institutionalization.

**There is no always-available, personalized coach standing beside a caregiver at 2am when their loved one is having a crisis.**

---

## The Solution

DementiaCare Coach is a multi-modal AI agent that:

1. **Analyzes caregiver-patient interactions** — via uploaded video, audio, or written description
2. **Retrieves evidence-based clinical guidelines** from a RAG-indexed vector store
3. **Generates personalized coaching** — what the caregiver did well, what to change, and exact dialog scripts ("Try saying..." / "Avoid saying...")
4. **Flags safety hazards** — fall risk, medication omission, delirium signs — and persists them for clinician review
5. **Simulates patient interactions** — a training sandbox where caregivers practice before real situations

---

## Key Course Concepts Demonstrated

| Concept | Where |
|---|---|
| **Multi-agent system (ADK)** | `adk-agent-scaffold/app/agent.py` — ADK conversational coach; `backend/app/agents/` — 7-agent pipeline |
| **MCP Server** | `backend/app/mcp_server.py` — FastMCP over SSE, consumed by the ADK agent |
| **Human-in-the-Loop (HITL)** | `ProfileEnricherAgent` detects new triggers/preferences from coach conversations; surfaces them to the caregiver for approval before updating the patient profile |
| **Security features** | `backend/app/main.py` — API key auth (`X-API-Key`), rate limiting (60 req/min/IP), CORS |
| **Deployability** | `docker-compose.yaml` — 4-service stack (PostgreSQL, ChromaDB, FastAPI backend, React frontend) |
| **Antigravity** | See video demo |
| **RAG** | `backend/app/rag.py` — ChromaDB + Gemini `text-embedding-004`; `backend/data/rag/guidelines/` |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                           │
│   (Analysis tab | Simulator tab | Coach chat | RAG viewer)      │
└──────────────────────┬──────────────────────────────────────────┘
                       │ REST (VITE_BACKEND_URL)
┌──────────────────────▼──────────────────────────────────────────┐
│                    FastAPI Backend                               │
│                                                                 │
│   /analyze/text   /analyze/file   /simulator/step   /coach/chat  │
│   /patient/{name}/interactions   /patient/{name}/coach-chat      │
│   DELETE /patient/{name}/history                                 │
│         │                │                │               │     │
│  ┌──────▼────────────────▼──────┐   ┌─────▼───────────────▼──┐ │
│  │   OrchestratorAgent          │   │  SimulatorAgent /       │ │
│  │   6-Step Sequential Pipeline │   │  ConversationalCoach    │ │
│  │                              │   └────────────────────────┘ │
│  │  Step 0: ValidationService   │                              │
│  │  Step 1: InteractionAnalyzer │◄── Gemini File API           │
│  │  Step 2: PatientContext      │    (video/audio upload)      │
│  │     RAG: ChromaDB query ─────┼──► ChromaDB (guidelines)     │
│  │  Step 3: CareGuidanceService │                              │
│  │  Step 4: SafetyEvaluator     │                              │
│  │  Step 5: CoachingSynthesizer │                              │
│  └──────────────────────────────┘                              │
│                                                                 │
│   /mcp/sse  ◄─── FastMCP Server (MCP over SSE)                  │
│                  tools: get_patient_profile                     │
│                          log_safety_escalation (→ DB)          │
│                          query_care_guidelines (→ ChromaDB)    │
└───────────────────────┬─────────────────────────────────────────┘
                        │ MCP SSE
┌───────────────────────▼─────────────────────────────────────────┐
│              ADK Agent Scaffold (adk-agent-scaffold/)           │
│   google.adk.agents.Agent — conversational dementia coach       │
│   Tools: get_patient_profile | log_safety_escalation |          │
│           query_care_guidelines                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Database Tables

| Table | Purpose |
|---|---|
| `patients` | Patient profile (name, dementia type, triggers, preferences, medications, conditions, allergies, fall risk, mobility aids, diet texture, sensory aids) |
| `interaction_history` | One row per analysis run — stores raw input, observed behavior, likely trigger, risk level, try/avoid phrases, and full JSON response |
| `coach_chat_history` | Persists every caregiver ↔ coach message per patient; reloaded when the caregiver returns |
| `safety_escalations` | HIGH/EMERGENCY safety flags written by `SafetyEvaluator` via the MCP `log_safety_escalation` tool, for clinician audit |

---

### The 7-Agent Pipeline (detail)

Each step is a dedicated Gemini agent with a narrow system prompt and an enforced Pydantic output schema (`response_mime_type="application/json"`). Splitting across agents reduces hallucination: each agent is primed only with context relevant to its task, and failures are diagnosable per step.

| Step | Agent | Output Schema | Purpose |
|---|---|---|---|
| 0 | `ValidationService` | `ValidationResponse` | Reject noise (silence, unrelated media, greetings) before spending tokens |
| 1 | `InteractionAnalyzer` | `InteractionAnalysisResponse` | Extract behavior, agitation level, behavioral timeline, RAG query keyword |
| 2 | `PatientContextProcessor` | `PatientContextResponse` | Map patient history & known triggers against what was observed |
| RAG | ChromaDB | — | Retrieve top-2 clinical guidelines matching Step 1's `rag_query` |
| 3 | `CareGuidanceService` | `CareGuidanceResponse` | Synthesize RAG results into clinical recommendations & do-not lists |
| 4 | `SafetyEvaluator` | `SafetyEscalationResponse` | Dedicated safety pass — never buried in coaching output |
| 5 | `CoachingSynthesizer` | `FinalCoachingResponse` | Assemble full coaching response with scripts, strengths, recommendations |
| 6 | `ProfileEnricherAgent` | `ProfileEnrichmentResponse` | Runs after each coach chat turn; detects new triggers/preferences worth adding to the patient profile and returns them as HITL suggestions |

---

## Features

- **Multi-modal input** — video, audio, or text description of a care interaction
- **Behavioral timeline** — chronological breakdown of patient behavior with clinical symptom labels
- **Coaching scripts** — exact "Try saying / Avoid saying" dialog pairs
- **Interactive simulator** — roleplay as a caregiver with a simulated patient (Maria / Arthur); agitation level updates dynamically
- **Conversational coach** — follow-up chat powered by the ADK agent via MCP; chat history is persisted per patient and reloaded across sessions
- **Interaction history** — every analysis run is logged to the database; the Profile tab shows a timeline of past interactions with risk-level badges, observed behavior, trigger, and expandable Try/Avoid phrases
- **HITL profile enrichment** — after each coach chat exchange, `ProfileEnricherAgent` detects new behavioral triggers or patient preferences mentioned in conversation and surfaces them as suggestions; the caregiver approves each one before it is written to the patient profile
- **Multi-language support** — detects interaction language; translate coaching to caregiver's native language
- **Safety escalation** — HIGH/EMERGENCY alerts persisted to database for clinician review
- **RAG-grounded guidance** — recommendations cite indexed clinical protocols
- **Mock mode** — full demo without an API key (high-fidelity local responses)

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### Option A: Local Development (no Docker)

**1. Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set:
#   GEMINI_API_KEY=your_key_here
#   (Leave blank to run in MOCK mode — full demo still works)

uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

**2. Frontend**

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local:
#   VITE_BACKEND_URL=http://localhost:8000

npm run dev
```

Frontend runs at `http://localhost:5173`.

**3. Seed the RAG database**

On first run, click **"Seed RAG DB"** in the app header (or call `POST /guidelines/seed` with your admin API key). This embeds the clinical guidelines from `backend/data/rag/guidelines/` into ChromaDB.

---

### Option B: Docker Compose (full production-like stack)

```bash
# From the repo root
cp backend/.env.example backend/.env
# Edit backend/.env and set GEMINI_API_KEY

docker-compose up --build
```

This starts:
- `db` — PostgreSQL 15 (patient data, safety escalation logs)
- `rag` — ChromaDB 0.4.24 (clinical guidelines vector store)
- `backend` — FastAPI + FastMCP server
- `frontend` — React app served via Nginx on port 80

Access the app at `http://localhost`.

---

### Option C: ADK Agent Scaffold (conversational agent)

The ADK agent connects to the backend via MCP over SSE for conversational caregiver coaching.

```bash
cd adk-agent-scaffold
pip install -r requirements.txt   # or: uv sync

export BACKEND_URL=http://localhost:8000
# For Vertex AI:
export GOOGLE_GENAI_USE_VERTEXAI=True
export GOOGLE_CLOUD_PROJECT=your-project-id

adk run app
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | For live mode | Google Gemini API key |
| `ADMIN_API_KEY` | Optional | API key for admin endpoints (seeding, etc.) |
| `USER_API_KEY` | Optional | API key for caregiver-facing endpoints |
| `DATABASE_URL` | Docker only | PostgreSQL connection string |
| `CHROMA_SERVER_HOST` | Docker only | ChromaDB host (default: local PersistentClient) |
| `CHROMA_SERVER_PORT` | Docker only | ChromaDB port |

Leave `GEMINI_API_KEY` blank to run in **MOCK mode** — the app returns high-fidelity local responses for the three most common dementia scenarios (medication refusal, shower resistance, wanting to go home).

---

## Antigravity Agent Configuration

This project uses the **Antigravity** agent framework. All project skills, hooks, and scripts live in `.agents/`:

```
.agents/
├── AGENTS.md          # Project-scoped agent rules (deployment, security)
├── CONTEXT.md         # Secure coding standards and paved-road patterns
├── hooks.json         # Pre-tool-use hooks (e.g. validate tool calls before execution)
├── skills/            # Reusable skills invocable by the agent
│   ├── dementiacare-run-all/       # Boot the full stack (setup → backend → RAG → frontend)
│   ├── dementiacare-run-backend/   # Start the FastAPI backend only
│   ├── dementiacare-run-frontend/  # Start the React frontend only
│   ├── dementiacare-seed-rag/      # Seed ChromaDB with clinical guidelines
│   ├── dementiacare-setup/         # Install dependencies
│   ├── dementiacare-cleanup-ports/ # Kill processes on ports 8000 / 5173
│   ├── dementiacare-deploy-backend/
│   ├── dementiacare-deploy-frontend/
│   └── stride-threat-model/        # Generate a STRIDE threat model
└── scripts/
    └── validate_tool_call.py       # Hook script: validate agent tool call inputs
```

Each skill is self-contained with a `SKILL.md` that describes its steps and purpose.

---

## Project Structure

```
dementia_care/
├── .agents/               # Antigravity skills, hooks, and scripts (see above)
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── orchestrator.py          # Pipeline controller
│   │   │   ├── validation.py            # Step 0: intake gatekeeper
│   │   │   ├── interaction_analysis.py  # Step 1: behavioral signals
│   │   │   ├── patient_context.py       # Step 2: patient history mapping
│   │   │   ├── care_guidance.py         # Step 3: RAG-grounded advice
│   │   │   ├── safety_escalation.py     # Step 4: safety audit
│   │   │   ├── caregiver_coaching.py    # Step 5: final coaching output
│   │   │   ├── simulator.py             # Interactive training simulator
│   │   │   ├── conversational_coach.py  # Follow-up chat agent
│   │   │   └── profile_enricher.py      # Step 6: HITL profile enrichment suggestions
│   │   ├── main.py                      # FastAPI routes + auth + rate limiting
│   │   ├── mcp_server.py                # FastMCP tools (MCP over SSE)
│   │   ├── rag.py                       # ChromaDB + Gemini embeddings
│   │   ├── schemas.py                   # Pydantic output schemas (all agents)
│   │   ├── database.py                  # SQLite / PostgreSQL client
│   │   └── config.py                    # Pydantic settings
│   ├── data/
│   │   └── rag/guidelines/              # Clinical protocol markdown files
│   ├── tests/                           # Per-agent eval tests + API tests
│   └── requirements.txt
├── frontend/
│   └── src/
│       └── App.jsx                      # React SPA
├── adk-agent-scaffold/
│   └── app/
│       └── agent.py                     # ADK agent + MCP tool wrappers
├── docker-compose.yaml
└── threat_model.md
```

---

## Security

- **API key authentication** — `X-API-Key` header required on all caregiver and admin endpoints
- **Role separation** — separate `USER_API_KEY` and `ADMIN_API_KEY` (admin required for seeding/maintenance)
- **Rate limiting** — 60 requests/minute per IP address
- **CORS** — explicit allowlist of frontend origins
- **No secrets in code** — all keys via environment variables / `.env` files (never committed)
- **Safety audit trail** — escalations written to the database for clinician review

See [`threat_model.md`](./threat_model.md) for the full security threat model.

---

## Contributors

- Catherine Balajadia
- Adrian Balajadia
- Avan Sargento
