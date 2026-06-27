# DementiaCare Coach: An AI-Powered Caregiver Co-Pilot

**An onboarding and transition engine for dementia care — so the people who need help can finally accept it.**

---

## The Problem Nobody Talks About

Over 55 million people worldwide live with dementia. Most of them are cared for at home, not in clinical facilities. And most of that home care is provided by a single family member — a spouse, an adult child, a sibling — who stepped into the role without training, without a manual, and without a realistic picture of how consuming it would become.

The physical and emotional toll is well documented. Dementia caregiving is one of the most demanding roles a person can take on. Sleep deprivation, social isolation, financial strain, and chronic grief — grieving a person who is still alive — combine into what researchers call "caregiver burden." Burnout is not a risk. For most primary caregivers, it is an eventual certainty.

The standard advice is straightforward: share the load. Bring in another family member to help cover shifts. Hire a Personal Support Worker (PSW). Arrange respite care so the primary caregiver can take a break. The logic is sound. The reality is devastating.

**Dementia profoundly changes how the brain processes trust and familiarity.**

Patients in moderate to advanced stages of dementia frequently experience heightened paranoia, severe anxiety around unfamiliar people, and an inability to place or accept faces they may have known for decades. Memory loss is not simply forgetting — it can strip a person of their ability to recognize a sibling, a neighbor, a long-time family friend. When a new face enters the home, even a warm, trained, well-intentioned one, the patient's brain may register that person as an intruder, a stranger, a threat.

The result is immediate: resistance, agitation, confusion, sometimes physical distress. The new caregiver, trying to help, triggers a crisis simply by being unknown. They spend their first visits navigating escalating behaviors without any context for what works, what the patient's triggers are, or how to communicate in a way that feels safe to this specific person. It is not incompetence — it is an impossible situation. Help has arrived cold.

This creates a trap that families cycle through for years: the primary caregiver is burning out, but every attempt to bring in support makes the patient worse, which increases the primary caregiver's guilt and reluctance to ask for help, which accelerates the burnout.

**No existing tool addresses this transition problem directly.** Generic caregiver guides cannot respond to what happened in this interaction with this patient today. Training programs exist, but they take weeks and assume stable access to professional resources. In-home care coordinators are expensive and limited in availability. And at 2 AM, when a patient is in crisis and the caregiver is exhausted, none of those resources are reachable.

---

## What We Built

DementiaCare Coach is a multi-agent AI system designed to solve two problems simultaneously: coaching caregivers through difficult interactions in real time, and acting as an onboarding engine for every new person who enters the care circle.

The platform learns the patient. Over time, through a combination of direct profile setup and automatic enrichment from real coaching conversations, the system builds a detailed picture of who the patient is — not just clinically, but as a person. Their name, their life history, the music they respond to, the phrases that calm them, the topics that trigger distress, the care approaches that have worked, and the ones that have not. This knowledge does not live only in one caregiver's head. It lives in the system, accessible to everyone in the care circle.

When a new PSW starts, they do not arrive cold. Before their first shift, they read the patient's full profile and the history of recent interactions — what happened, how it escalated, what was said, what worked. They walk in with context. The first visit is not trial-and-error. It is an informed introduction.

When an existing caregiver has a difficult moment — a medication refusal, a sundowning episode, a patient who does not recognize them today — they can submit a video clip, an audio recording, or a written description of what happened. Within seconds, the system analyzes the interaction, identifies what escalated the situation, retrieves evidence-based clinical protocols relevant to the specific behavior, and generates a structured coaching response: what the caregiver did well, what to change, and exactly what to say differently next time — down to specific phrases.

---

## How It Works

### The Frontend

The interface is a React single-page application with four main tabs: Analysis, Simulator, Coach Chat, and History. Caregivers can upload media or type a description in the Analysis tab, follow up with questions in the Coach Chat, practice new techniques in the Simulator, and review past interactions in the History tab. The entire stack runs locally via Docker Compose or in the cloud via Cloud Run.

### The Backend Pipeline

The core of the system is a seven-agent sequential pipeline running in a FastAPI backend. Each step is a dedicated Gemini agent with a narrow system prompt and a Pydantic-enforced JSON output schema. Rather than a single monolithic prompt trying to do everything at once, each agent is responsible for exactly one thing. This reduces hallucination, makes failures diagnosable per step, and ensures each agent is primed only with the context relevant to its task.

**Step 0 — ValidationService.** Before any tokens are spent on analysis, the submitted content is evaluated. Is this actually a care interaction? Is there enough signal to work with? Silence, unrelated media, and greetings that contain no behavioral information are rejected here. Only valid submissions continue.

**Step 1 — InteractionAnalyzer.** The first substantive agent extracts behavioral signals from the input — the patient's agitation level on a five-point scale, the specific behaviors observed, a chronological timeline of how the interaction unfolded, the likely emotional state of the patient, and a short keyword phrase summarizing the core behavior for the RAG query in the next step. When video or audio is provided, this agent receives the media via Gemini's File API and analyzes verbal content, tone, pacing, and observable physical signals.

**Step 2 — PatientContextProcessor.** The patient's full profile is retrieved from the database and mapped against what was observed in Step 1. This agent identifies which documented triggers are present in the interaction, whether the caregiver's approach aligned with or conflicted with known patient preferences, and what contextual factors from the patient's history are relevant to the current situation. A patient who spent their career as a nurse will respond differently to a direct instruction than one who valued independence and autonomy in a different professional context — this step makes those distinctions.

**RAG Retrieval.** Between Steps 2 and 3, the keyword extracted in Step 1 is used to query the clinical guidelines vector store. Clinical protocols covering dozens of dementia behaviors — medication refusal, shower resistance, sundowning agitation, wandering, aggressive outbursts, false accusations, repetitive questioning — are stored as structured markdown documents, embedded using Gemini's `text-embedding-004` model, and indexed in ChromaDB. In production, Vertex AI Search handles retrieval with ChromaDB as a fallback, so the same code path works in both local and cloud environments. The top matching protocols are passed to the next agent.

**Step 3 — CareGuidanceService.** This agent synthesizes the RAG-retrieved guidelines into actionable clinical recommendations. It identifies which evidence-based approaches apply, generates a list of specific do-not behaviors that are likely escalating the situation, and frames recommendations in a way that connects the clinical theory to the specific scenario described.

**Step 4 — SafetyEvaluator.** Safety assessment is its own dedicated agent — never buried in coaching output or combined with recommendations where it might be missed. This agent evaluates the interaction for fall risk, signs of delirium, medication omission danger, and other HIGH or EMERGENCY safety concerns. When a safety flag is triggered, it is persisted to the database via the MCP server's `log_safety_escalation` tool, creating a clinician-reviewable audit trail that survives application restarts.

**Step 5 — CoachingSynthesizer.** The final coaching output is assembled here from the structured outputs of all previous agents. This agent produces the full caregiver-facing response: a behavioral summary, a recognition of what the caregiver did well, specific opportunities to improve, and the dialog scripts — exact "Try saying" and "Avoid saying" phrase pairs calibrated to this patient's profile and this specific situation.

**Step 6 — ProfileEnricherAgent.** This agent runs after each conversational coaching exchange, not after analysis. It reads the conversation turn and identifies whether the caregiver mentioned anything new about the patient — a previously undocumented trigger, a comfort object, a change in medication, a pattern of behavior the system has not recorded. Rather than writing these observations directly to the patient profile, it returns them as structured suggestions. The caregiver reviews each one in the frontend and approves or rejects it before anything is written. This is the Human-in-the-Loop mechanism: the patient profile improves continuously from real care interactions, but only with explicit caregiver consent.

### The MCP Server

The FastAPI backend exposes a FastMCP server at `/mcp/sse` using Model Context Protocol over Server-Sent Events. This server publishes four tools that are consumed by both the internal pipeline and the external ADK agent: `get_patient_profile`, `log_safety_escalation`, `search_patients`, and `query_care_guidelines`. The backend is the single source of truth. All data access and side effects are routed through these tools, which means the ADK conversational agent remains fully stateless and can be deployed, updated, or replaced independently of the backend.

### The ADK Agent

The conversational coach is a `google.adk.agents.Agent` running in a separate `adk-agent-scaffold` directory, connected to the backend exclusively through MCP. Every time a caregiver sends a message, the agent follows a strict protocol: identify and load the patient profile, query the guidelines vector store for relevant behaviors, log any safety concerns that emerge, and synthesize a response that is compassionate, specific, and actionable. Conversation history is persisted per patient and reloaded across sessions — a caregiver can return after two days and the coach already knows what they discussed.

---

## A Real Scenario

A daughter has been caring for her mother — moderate-stage Alzheimer's, diagnosed three years ago — and she is exhausted. Her brother has agreed to take over on weekends, but every time he visits, their mother becomes agitated and accusatory. He is trying to help with morning medications and the interaction is deteriorating.

He records a short video of one exchange and submits it to DementiaCare Coach.

The InteractionAnalyzer identifies agitation level 4 out of 5. It flags direct confrontation — "Mom, you have to take these, the doctor prescribed them" — and notes the patient's escalating physical withdrawal. It extracts `medication refusal` as the RAG query.

The PatientContextProcessor loads the patient profile and finds a documented trigger: direct instructions. It also finds a documented preference: music-assisted routines during morning care. The confrontation approach directly conflicts with known care preferences.

The RAG retrieval returns protocols on validation therapy for medication refusal and the offer-don't-demand principle from occupational therapy. CareGuidanceService synthesizes these into specific recommendations. SafetyEvaluator notes no immediate fall risk or delirium indicators — LOW safety flag.

The CoachingSynthesizer assembles the full response. Strengths: the brother remained calm, maintained eye contact, did not raise his voice. Opportunities: the direct statement of obligation ("you have to") activated the patient's resistance rather than her cooperation. Dialog scripts:

- *Avoid saying:* "You have to take your medication."
- *Try saying:* "I brought you something with your morning tea. Can we sit together for a minute?"

The brother reads this. He understands, for the first time, not just what went wrong but why — and what to do instead. The next visit goes differently.

---

## Technical Concepts Demonstrated

| Concept | Implementation |
|---|---|
| Multi-agent system | 7-agent sequential pipeline in `backend/app/agents/`; ADK conversational agent in `adk-agent-scaffold/` |
| MCP Server | FastMCP over SSE at `/mcp/sse`; four tools consumed by the ADK agent |
| Human-in-the-Loop | ProfileEnricherAgent surfaces profile update suggestions; caregiver approves each before any DB write |
| RAG | Gemini `text-embedding-004` + ChromaDB; Vertex AI Search in production with automatic fallback |
| Structured output | All agents enforce Pydantic schemas with `response_mime_type="application/json"` |
| Security | API key auth (`X-API-Key`), rate limiting (60 req/min/IP), CORS allowlist, safety escalation audit trail, STRIDE threat model |
| Deployability | Docker Compose 4-service stack (PostgreSQL, ChromaDB, FastAPI, React/Nginx); Cloud Run deployment scripts; Vertex AI ADK scaffold |
| Mock mode | Full application demo without a live API key using high-fidelity local responses |
| Testing | Per-agent unit tests for all 5 pipeline agents + orchestrator (mocked LLM, eval-dataset-driven); API integration tests via FastAPI `TestClient`; RAG and simulator unit tests; ADK integration tests (`test_agent_stream`, `AgentEngineApp`); Locust load test against the deployed agent runtime; LLM-judge eval runner (`run_evals.py`) scoring each pipeline response on empathy, actionability, and safety (1–5 scale) |
| Antigravity Skills | 10 project-scoped skills defined in `.agents/skills/`: lifecycle automation (`dementiacare-setup`, `dementiacare-run-all`, `dementiacare-run-backend`, `dementiacare-run-frontend`, `dementiacare-seed-rag`, `dementiacare-stop-all`, `dementiacare-cleanup-ports`), GCP deployment (`dementiacare-deploy-backend`, `dementiacare-deploy-frontend`), and security (`stride-threat-model` for STRIDE assessment); agent rules in `.agents/CONTEXT.md` enforce Pydantic validation, no raw shell execution, and pre-commit remediation loops |

---

## Development Environment

### System Concept & Architectural Planning

The Antigravity Workspace was used during the initial concept phase to map out the overall functional behavior, system interactions, and architectural framework before writing code.

- **Concept Creation** — Brainstorming core user journeys and defining assistant behavior dynamically.
- **Functional Planning** — Specifying modular tool schemas, APIs, and agent interaction boundaries.
- **Architectural Framing** — Constructing structural system configuration files and prompt foundations.

### Antigravity IDE Integration

Once the initial project was created, the workspace transitioned into an interactive loop for deep fine-tuning and continuous execution within the IDE.

- **Direct File Syncing** — Real-time code exploration and editing inside a native environment.
- **Agent-Led Refinement** — Prompt tuning, configuration editing, and workflow adjustments.
- **Continuous Development** — Easily run setup, seed, and background service scripts directly.

---

## Impact

DementiaCare Coach addresses a specific, underserved failure point: the moment care tries to expand and fails. By acting as an onboarding engine for incoming caregivers and a real-time coaching layer for existing ones, the platform makes the care circle expandable in a way that was previously impossible without expensive professional coordination.

The concrete outcomes this enables: primary caregivers can finally take breaks because new caregivers can enter the home informed rather than blind. New caregivers — PSWs, family members, respite workers — experience fewer crisis interactions in their early visits, which means they are more likely to continue helping. Patients experience more consistent, evidence-aligned care from every person in their circle, which reduces behavioral episodes over time. Safety risks are flagged and persisted for clinical review rather than unobserved. And the patient's care profile grows more accurate with every interaction, automatically, without requiring the primary caregiver to manually maintain a document.

---

## Future Work

- **Care circle shift handoffs** — automatically generated handoff notes from interaction history, so every shift starts informed without the primary caregiver having to brief each incoming helper manually
- **Real-time coaching** — live audio analysis during an interaction, not just post-hoc review
- **Wearable integration** — passive agitation monitoring from patient heart rate and movement data
- **EHR integration** — pull medication lists, care plans, and diagnostic history directly from electronic health records to seed the patient profile
- **Predictive behavior forecasting** — identify patterns in the interaction history to anticipate high-risk periods, such as sundowning windows or post-visit agitation cycles, before they occur

---

*Built for the AI Agents: Intensive Vibe Coding Capstone Project — Kaggle. Contributors: Catherine Balajadia, Adrian Balajadia, Avan Sargento.*
