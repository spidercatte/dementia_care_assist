# DementiaCare Coach: An AI-Powered Caregiver Co-Pilot

**An onboarding and transition engine for dementia care — so the people who need help can finally accept it.**

---

## The Problem Nobody Talks About

Over 55 million people worldwide live with dementia. Most are cared for at home by a single family member — a spouse, an adult child, a sibling — who stepped into the role without training and without a realistic picture of how consuming it would become.

The toll is well documented: sleep deprivation, social isolation, financial strain, and chronic grief — grieving a person who is still alive — combine into "caregiver burden." Burnout is not a risk. For most primary caregivers, it is an eventual certainty.

The standard advice is straightforward: share the load. Hire a Personal Support Worker. Arrange respite care. The logic is sound. The reality is devastating.

**Dementia profoundly changes how the brain processes trust and familiarity.**

Patients in moderate to advanced stages frequently experience heightened paranoia and severe anxiety around unfamiliar faces. Memory loss can strip a person of their ability to recognize a sibling or a longtime friend. When a new face enters the home — even a warm, trained, well-intentioned one — the patient's brain may register that person as an intruder. The result: resistance, agitation, and distress. Help has arrived cold.

This creates a trap families cycle through for years: the primary caregiver burns out, but every attempt to bring in support makes the patient worse, which increases guilt and reluctance to ask for help, which accelerates the burnout.

**No existing tool addresses this transition problem directly.** Generic guides cannot respond to what happened in this interaction today. Training programs take weeks. In-home coordinators are expensive. At 2 AM, when a patient is in crisis, none of those resources are reachable.

---

## What We Built

DementiaCare Coach is a multi-agent AI system designed to solve two problems simultaneously: coaching caregivers through difficult interactions in real time, and acting as an onboarding engine for every new person entering the care circle.

The platform learns the patient. Over time, through profile setup and automatic enrichment from real coaching conversations, the system builds a detailed picture — not just clinically, but as a person: the music they respond to, the phrases that calm them, the topics that trigger distress, the approaches that have worked. This knowledge lives in the system, accessible to everyone in the care circle.

When a new PSW starts, they do not arrive cold. They read the patient's full profile and interaction history before their first shift — what happened, how it escalated, what worked. The first visit is an informed introduction, not trial-and-error.

When an existing caregiver has a difficult moment, they can submit a video clip, audio recording, or written description. Within seconds, the system analyzes the interaction, retrieves evidence-based clinical protocols, and generates a structured coaching response: what the caregiver did well, what to change, and exactly what to say differently next time.

---

## How It Works

![Architecture Diagram](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F25975882%2Ff61f5545324f7816564a50c44a473f61%2FScreenshot%202026-06-26%20at%2010.59.01PM.png?generation=1782536377808014&alt=media)

### The Frontend

A React SPA with four tabs: Analysis (submit media or text), Coach Chat (follow-up questions), Simulator (practice new techniques), and History (past interactions). The stack runs locally via Docker Compose or in the cloud via Cloud Run.

### The Backend Pipeline

The core is a six-agent sequential pipeline running in a FastAPI backend. Each agent has a narrow system prompt and a Pydantic-enforced JSON output schema — one agent, one responsibility. This reduces hallucination, makes failures diagnosable per step, and keeps each agent primed with only relevant context.

**Step 0 — ValidationService.** Evaluates submitted content before any tokens are spent on analysis. Silence, unrelated media, and greetings with no behavioral signal are rejected here. Only valid submissions continue.

**Step 1 — InteractionAnalyzer.** Extracts behavioral signals: agitation level (1–5 scale), specific behaviors observed, a chronological timeline, the patient's likely emotional state, and a keyword phrase for the RAG query. Video and audio are processed via Gemini's File API for verbal content, tone, pacing, and observable physical signals.

**Step 2 — PatientContextProcessor.** Maps the patient's full profile against what was observed in Step 1. Identifies which documented triggers are present, whether the caregiver's approach aligned with or conflicted with known patient preferences, and what historical context is relevant to the current situation.

**RAG Retrieval.** The keyword from Step 1 queries the clinical guidelines vector store — 20+ structured markdown protocols covering medication refusal, sundowning agitation, wandering, aggression, false accusations, and more — embedded with Gemini `text-embedding-004` and indexed in ChromaDB. In production, Vertex AI Search handles retrieval with ChromaDB as a fallback.

**Step 3 — CareGuidanceService.** Synthesizes RAG-retrieved protocols into actionable recommendations specific to the observed scenario, identifying which evidence-based approaches apply and which caregiver behaviors are likely escalating the situation.

**Step 4 — SafetyEvaluator.** A dedicated safety agent — never buried in coaching output. Evaluates for fall risk, delirium signs, and medication omission danger. HIGH or EMERGENCY flags are persisted to the database via the MCP server's `log_safety_escalation` tool, creating a clinician-reviewable audit trail.

**Step 5 — CoachingSynthesizer.** Assembles the full caregiver-facing response: behavioral summary, strengths recognition, improvement opportunities, and dialog scripts — exact "Try saying" / "Avoid saying" phrase pairs calibrated to this patient's profile and this specific situation.

**ProfileEnricherAgent (post-conversation).** After each coaching exchange, this agent identifies new information the caregiver mentioned — undocumented triggers, comfort objects, behavioral patterns. Rather than writing directly to the profile, it returns structured suggestions for caregiver review. This is the Human-in-the-Loop mechanism: the profile improves continuously from real interactions, but only with explicit caregiver consent.

### The MCP Server

The FastAPI backend exposes a FastMCP server at `/mcp/sse`. Four tools — `get_patient_profile`, `log_safety_escalation`, `search_patients`, `query_care_guidelines` — are consumed by both the internal pipeline and the external ADK agent. All data access and side effects route through these tools, keeping the ADK agent fully stateless and independently deployable.

### The ADK Agent

A `google.adk.agents.Agent` in `adk-agent-scaffold/`, connected to the backend exclusively via MCP. Each conversation follows a strict protocol: load the patient profile, query guidelines, log safety concerns, and synthesize a compassionate, specific, actionable response. Conversation history is persisted per patient and reloaded across sessions — a caregiver can return after two days and the coach already knows what they discussed.

---

## A Real Scenario

A daughter has been caring for her mother — moderate-stage Alzheimer's, diagnosed three years ago — and she is exhausted. Her brother agreed to help on weekends, but every visit ends in agitation and accusation. He records one exchange and submits it.

The InteractionAnalyzer flags agitation level 4/5, identifies direct confrontation ("Mom, you have to take these, the doctor prescribed them"), and extracts `medication refusal` as the RAG query.

The PatientContextProcessor finds a documented trigger — direct instructions — and a documented preference: music-assisted morning routines. The confrontation approach directly conflicted with known care preferences.

RAG returns protocols on validation therapy for medication refusal and the offer-don't-demand principle from occupational therapy. CareGuidanceService synthesizes these into specific recommendations. SafetyEvaluator notes no fall risk or delirium — LOW flag.

CoachingSynthesizer delivers the response. Strengths: calm, eye contact, no raised voice. Opportunity: "you have to" activated resistance rather than cooperation. Dialog scripts:

- *Avoid saying:* "You have to take your medication."
- *Try saying:* "I brought you something with your morning tea. Can we sit together for a minute?"

The brother understands — not just what went wrong, but why — and what to do instead.

---

## Technical Concepts Demonstrated

| Concept | Implementation |
|---|---|
| Multi-agent system | 6-agent sequential pipeline in `backend/app/agents/`; ADK conversational agent in `adk-agent-scaffold/` |
| MCP Server | FastMCP over SSE at `/mcp/sse`; four tools consumed by the ADK agent |
| Human-in-the-Loop | ProfileEnricherAgent surfaces profile update suggestions; caregiver approves each before any DB write |
| RAG | Gemini `text-embedding-004` + ChromaDB; Vertex AI Search in production with automatic fallback |
| Structured output | All agents enforce Pydantic schemas with `response_mime_type="application/json"` |
| Security | API key auth (`X-API-Key`), rate limiting (60 req/min/IP), CORS allowlist, safety escalation audit trail, STRIDE threat model |
| Deployability | Docker Compose 4-service stack (PostgreSQL, ChromaDB, FastAPI, React/Nginx); Cloud Run deployment scripts; Vertex AI ADK scaffold |
| Antigravity Skills | 10 project-scoped skills in `.agents/skills/`: lifecycle automation (`dementiacare-setup`, `dementiacare-run-all`, `dementiacare-run-backend`, `dementiacare-run-frontend`, `dementiacare-seed-rag`, `dementiacare-stop-all`, `dementiacare-cleanup-ports`), GCP deployment (`dementiacare-deploy-backend`, `dementiacare-deploy-frontend`), and security (`stride-threat-model` for STRIDE assessment); agent rules in `.agents/CONTEXT.md` enforce Pydantic validation, no raw shell execution, and pre-commit remediation loops |

---

## Development Environment

### System Concept & Architectural Planning

The Antigravity Workspace was used during the initial concept phase to map functional behavior, system interactions, and architectural framework before writing code.

- **Concept Creation** — Brainstorming core user journeys and defining assistant behavior dynamically.
- **Functional Planning** — Specifying modular tool schemas, APIs, and agent interaction boundaries.
- **Architectural Framing** — Constructing structural system configuration files and prompt foundations.

### Antigravity IDE Integration

Once the initial project was created, the workspace transitioned into an interactive loop for deep fine-tuning and continuous execution within the IDE.

- **Direct File Syncing** — Real-time code exploration and editing inside a native environment.
- **Agent-Led Refinement** — Prompt tuning, configuration editing, and workflow adjustments.
- **Continuous Development** — Setup, seed, and background service scripts run directly from the IDE.

---

## Privacy, Ethics & Patient Consent

Media analysis of a vulnerable, non-consenting patient is a high-risk area for privacy and dignity. DementiaCare Coach implements a concrete consent governance framework:

1. **Surrogate Consent Gating**: Video and audio analysis requires documented surrogate consent from the patient's legal decision-maker (Power of Attorney, Legal Guardian, or primary family caregiver), scoped per media type, before any file is uploaded to an external API.
2. **Consent Limits Acknowledged**: Patients with moderate-to-advanced dementia typically cannot provide direct informed consent. Consent is attributed to the designated caregiver or legal authority, not the patient.
3. **Step 0 Validation**: Before any file upload, the orchestrator queries the `consent_records` table. No active consent for that media type = request blocked immediately.
4. **Auditable Trail**: Verification events are logged to `consent_audit_logs` (who authorized, required scope, allowed scope, result, timestamp), creating a clinical-grade audit record.
5. **No Persistent Media Storage**: Raw video, audio, and images are never permanently stored. Files are buffered in temporary directories for the duration of the API call and deleted in a `finally` block. Gemini File API uploads are deleted immediately via `client.files.delete(...)`, backed by a background task that purges orphaned files every 15 minutes.
6. **Text-Only Alternative**: Caregivers can describe interactions in writing — no recording, no upload required.

---

## Impact

DementiaCare Coach addresses a specific, underserved failure point: the moment care tries to expand and fails. Primary caregivers can finally take breaks because new caregivers enter the home informed rather than cold. New caregivers experience fewer crisis interactions early on, making them more likely to continue helping. Patients receive more consistent, evidence-aligned care from every person in their circle, reducing behavioral episodes over time. Safety risks are flagged and persisted for clinical review. The patient's care profile grows more accurate with every interaction — automatically, with caregiver consent.

---

## Future Work

- **Care circle shift handoffs** — automatically generated handoff notes from interaction history, so every shift starts informed
- **Real-time coaching** — live audio analysis during an interaction, not just post-hoc review
- **Wearable integration** — passive agitation monitoring from patient heart rate and movement data
- **EHR integration** — pull medication lists, care plans, and diagnostic history to seed the patient profile
- **Predictive behavior forecasting** — anticipate high-risk periods (sundowning windows, post-visit agitation cycles) from interaction patterns

---

*Built for the AI Agents: Intensive Vibe Coding Capstone Project — Kaggle. Contributors: Catherine Balajadia, Adrian Balajadia, Avan Sargento.*
