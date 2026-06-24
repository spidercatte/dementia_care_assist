# STRIDE Threat Model Assessment: DementiaCare Coach

This document details the threat modeling assessment of the **DementiaCare Coach** agentic graph and backend architecture using the STRIDE methodology.

---

## 1. System Description & Data Flow

DementiaCare Coach is a modular 6-agent collaborative pipeline that coordinates caregiver interactions, retrieves clinical guidelines via a RAG pipeline (ChromaDB), and produces coaching feedback using the Google Gemini API.

### Boundaries & Entry Points
* **Entry Points**: FastAPI public HTTP endpoints defined in [main.py](file:///workspaces/dementia_care_assist/backend/app/main.py) (`/patient`, `/guidelines/seed`, `/analyze/text`, `/analyze/file`, `/simulator/step`).
* **Data Flow**:
  1. Caregiver inputs text or uploads a file via the React Frontend.
  2. The FastAPI Backend handles requests and reads/writes the local `patient_profile.json` file.
  3. The [OrchestratorAgent](file:///workspaces/dementia_care_assist/backend/app/agents/orchestrator.py) coordinates data flow to specialized sub-agents ([interaction_analysis](file:///workspaces/dementia_care_assist/backend/app/agents/interaction_analysis.py), [patient_context](file:///workspaces/dementia_care_assist/backend/app/agents/patient_context.py), [care_guidance](file:///workspaces/dementia_care_assist/backend/app/agents/care_guidance.py), [safety_escalation](file:///workspaces/dementia_care_assist/backend/app/agents/safety_escalation.py), [caregiver_coaching](file:///workspaces/dementia_care_assist/backend/app/agents/caregiver_coaching.py)).
  4. The RAG pipeline in [rag.py](file:///workspaces/dementia_care_assist/backend/app/rag.py) queries a local ChromaDB instance containing embedded guidelines.
  5. The agents compile contexts and query the external **Google Gemini API** (handling uploads via the Gemini File API).
  6. Final responses are returned to the frontend.

---

## 2. STRIDE Threat Analysis

| Threat Category | Identified Vulnerability | Impact | Mitigation Status / Recommendation |
| :--- | :--- | :--- | :--- |
| **Spoofing** | No API authentication or identity verification exists for the FastAPI endpoints. | Malicious entities can spoof request origins, query patient records, and consume Gemini API quota. | **High Risk**: Implement token-based authentication (e.g., JWT or API key validation) to verify the client's identity before processing requests. |
| **Tampering** | 1. `patient_profile.json` can be modified arbitrarily by anyone via `POST /patient` without validation.<br>2. Prompt injection vulnerabilities exist since raw inputs from the user (`TextAnalysisRequest.description` and `SimulatorRequest.chat_history`) are fed directly into agent LLM prompts.<br>3. Patient profile fields can be injected with prompt commands. | 1. Caregiver/patient settings can be manipulated.<br>2. Malicious users can trigger prompt injections to bypass safety guidelines, alter agent reasoning, or access underlying system instructions.<br>3. The backend can be hijacked via profile-based injections. | **High Risk**: <br>- Implement strict input validation on patient fields.<br>- Use structured outputs and system instruction boundaries to sanitize user input before passing it to LLM contexts.<br>- Establish safety guardrails or validation checks on patient profile inputs. |
| **Repudiation** | Lack of secure, persistent audit trails for sensitive operations (e.g., patient profile changes, database seeding, API failures). | It is impossible to prove who modified a patient profile or triggered a billing-intensive vector DB seed operation. | **Medium Risk**: Implement a persistent logger that records timestamps, user IDs, and operation types for all write/run actions in a secure audit log. |
| **Information Disclosure** | 1. Patient PII (e.g., name, stage, background, caregiver triggers) is exposed publicly on the `/patient` endpoints.<br>2. Raw stack traces are returned to clients on HTTP 500 pipeline failures (e.g. `Seeding failed: {str(e)}`, `Analysis failed: {str(e)}`).<br>3. Files uploaded to the Gemini File API may persist on Google servers if cleanup fails. | 1. Direct leakage of patient PII (potential HIPAA/GDPR violation).<br>2. Exposure of internal paths, dependency structures, and API keys to clients.<br>3. Persistent leak of sensitive caregiver/patient media on external servers. | **High Risk**: <br>- Restrict access to `/patient` behind authenticated sessions.<br>- Sanitize error outputs; return generic error messages to clients while logging stack traces internally.<br>- Implement robust exception-safe cleanups and scheduled cron cleanups for Gemini File API uploads. |
| **Denial of Service** | 1. No rate limiting or request throttling is configured.<br>2. File uploads to `/analyze/file` do not validate file size limits.<br>3. Input that triggers model JSON validation errors forces mock fallback. | 1. High-frequency queries can exhaust the Gemini API quota and result in high financial charges.<br>2. Uploading massive files can saturate local disk space and freeze the server.<br>3. Malicious inputs can degrade quality of service by forcing the system into Mock Mode. | **High Risk**: <br>- Implement rate-limiting middleware (e.g., slowapi).<br>- Configure file size limits on the `/analyze/file` endpoint and restrict supported MIME types/extensions.<br>- Handle Pydantic validation errors gracefully with retries or sanitization. |
| **Elevation of Privilege**| There is no role-based access control (RBAC). Any client accessing the endpoints has full root-level control over patient records and guidelines seeding. | Normal users can perform administrative actions (e.g. re-seeding the database, modifying system settings). | **High Risk**: Implement RBAC distinguishing admin roles (seeding, configuration) from user roles (asking questions, simulator interaction). |

---

## 3. Threat Modeling the Agent Graph

The agent graph consists of 6 specialized collaborative agents (coordinated by [orchestrator.py](file:///workspaces/dementia_care_assist/backend/app/agents/orchestrator.py)):
```mermaid
graph TD
    Orchestrator[Orchestrator Agent] --> Analyzer[Interaction Analysis Agent]
    Orchestrator --> Context[Patient Context Agent]
    Analyzer -->|Generates RAG Query| RAG[ChromaDB RAG Retrieve]
    RAG -->|Guidelines Context| Guidance[Care Guidance Agent]
    Context -->|Patient Context| Guidance
    Guidance -->|Clinical Advice| Safety[Safety & Escalation Agent]
    Safety -->|Clinical Safety Check| Coach[Caregiver Coaching Agent]
    Coach -->|Final Coaching Script| User[Caregiver]
```

### Specific Agent Graph Risks:

1. **Cascade Prompt Injection**:
   - If the [InteractionAnalysisAgent](file:///workspaces/dementia_care_assist/backend/app/agents/interaction_analysis.py) receives a prompt injection, it could generate a malicious `rag_query`. This query could fetch unrelated/unsafe documents from the guidelines DB or inject instructions that are passed down to the [CareGuidanceAgent](file:///workspaces/dementia_care_assist/backend/app/agents/care_guidance.py) and [SafetyEscalationAgent](file:///workspaces/dementia_care_assist/backend/app/agents/safety_escalation.py) agents, overriding safety blocks.
   - **Recommendation**: Sanitize user inputs at the input boundary of the `Interaction Analysis Agent` and enforce strict parameter constraints on `rag_query`.

2. **RAG Poisoning via Unauthenticated Seeding**:
   - An attacker capable of invoking the seeding endpoints (`/guidelines/seed`) could inject false or harmful clinical guidelines into ChromaDB. Since the `Care Guidance Agent` relies on these guidelines, it would offer bad clinical advice.
   - **Recommendation**: Secure the RAG seeding API endpoint behind strict administrative authentication and require manual review/signing of ingested guideline files.

3. **Patient Profile-based Injection**:
   - The [PatientContextAgent](file:///workspaces/dementia_care_assist/backend/app/agents/patient_context.py) reads the patient profile directly and injects it into the prompt context. If a user can inject prompt directives into the profile (e.g., name or background containing `"System note: ignore previous instructions..."`), they can hijack the downstream analysis.
   - **Recommendation**: Enforce rigid schemas, sanitize profile values before context construction, and use system instructions/developer messages to isolate data from instructions.

4. **Gemini API Failures / Mock Mode Hijacking**:
   - When the Gemini API fails, the pipeline falls back to mock responses. If an attacker can trigger a denial-of-service on the API (e.g., quota exhaustion), they can force the system into Mock Mode. If the mock provider returns predefined responses, it could leak sensitive mock details or allow predictable behaviors.
   - **Recommendation**: Ensure the Mock Mode is securely configured and does not return debug context or stack traces.

5. **Gemini File API Leakage (Information Disclosure)**:
   - File analysis uploads user-provided audio/video files to Gemini. If an exception occurs after upload, the cleanup code in `finally` may not execute if the server crashes or restarts. This leaves sensitive patient files on external servers.
   - **Recommendation**: Register uploads to a database or local state, and run a startup/periodic worker to garbage collect outstanding files on the Gemini File API.

6. **Pydantic Validation DoS via Structured Outputs**:
   - If a prompt injection causes a model to emit responses that violate the Pydantic schema constraints (e.g., invalid ranges, missing fields), the parsing fails with a `ValidationError`, triggering a fallback to mock responses. This allows an attacker to easily DOS the live system.
   - **Recommendation**: Implement retry logic with corrected prompts on parsing failure, or handle schema errors gracefully before falling back.
