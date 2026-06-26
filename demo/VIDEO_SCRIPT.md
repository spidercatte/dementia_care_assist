# DementiaCare Coach — Video Demo Script
**Target length: 5 minutes**
**Format: Screen recording + voiceover, with slide overlays for problem/architecture sections**

---

## SECTION 1 — THE HOOK (0:00–0:30)

**[VISUAL: Black screen fading in. Show a still image or short clip of an elderly person with a caregiver — calm, documentary-style. No sound initially.]**

**NARRATION:**
> "It's 2 AM. Your 78-year-old mother is convinced someone is stealing her money. She's refusing her heart medication. She's getting more upset. You're exhausted. You don't know what to say — and everything you try seems to make it worse."

**[VISUAL: Fade in title card — "DementiaCare Coach"]**

> "What if you had an expert coach beside you, always available, who knew your mother personally — and could tell you exactly what to say?"

---

## SECTION 2 — THE PROBLEM (0:30–1:00)

**[VISUAL: Slide with stats — clean, minimal design]**

**NARRATION:**
> "Over 55 million people worldwide live with dementia. The majority are cared for at home — by family members with no clinical training."

> "When a patient becomes agitated, refuses medication, or wants to 'go home' — caregivers instinctively argue, correct, or rush them. This almost always escalates the situation."

> "There is no always-available, personalized coach. Caregiver burnout is one of the leading drivers of premature institutionalization."

> "We built DementiaCare Coach to change that."

---

## SECTION 3 — WHY AGENTS? (1:00–1:30)

**[VISUAL: Slide — "Why AI Agents?" with a simple illustration of a pipeline]**

**NARRATION:**
> "This problem needs agents — not a single prompt — because good dementia coaching requires multiple specialized reasoning steps that must happen in sequence."

> "A single LLM call trying to do everything at once loses focus, hallucinates clinical details, and buries safety concerns in coaching output."

> "Agents let us enforce separation of concerns: one agent detects behavior, one retrieves evidence-based clinical guidelines, one does the safety audit — and they only see the context they need."

> "The result is coaching you can trust."

---

## SECTION 4 — ARCHITECTURE (1:30–2:00)

**[VISUAL: Animated architecture diagram — show the pipeline flowing step by step]**
*(Use `architecture_diagram.html` as a reference, or screen-record it)*

**NARRATION:**
> "Here's how it works."

> "The caregiver uploads a video, audio clip, or text description of a care interaction."

> "It flows through a 7-step multi-agent pipeline — each step a dedicated Gemini agent with a Pydantic-enforced output schema."

**[VISUAL: Highlight each step as you name it]**

> "Step 0 — Validation: rejects nonsense input before wasting tokens."
> "Step 1 — Interaction Analyzer: extracts behavioral signals and agitation level."
> "Step 2 — Patient Context: maps the patient's known triggers and history against what was observed."
> "Then ChromaDB RAG retrieves the top matching evidence-based clinical guidelines."
> "Step 3 — Care Guidance: synthesizes RAG results into concrete protocols."
> "Step 4 — Safety Evaluator: a dedicated pass that flags fall risk, medication omission, delirium signs — and writes HIGH or EMERGENCY alerts to the database for clinician review."
> "Step 5 — Coaching Synthesizer: assembles the final response with scripts, strengths, and recommendations."

> "And after the caregiver chats with the coach, a 7th agent — the Profile Enricher — detects new triggers or preferences mentioned in conversation and proposes them as profile updates. The caregiver approves each one before it's saved. That's the human-in-the-loop."

> "The conversational coach is built with Google's ADK and connects to the backend via a FastMCP server over SSE."

---

## SECTION 5 — LIVE DEMO (2:00–4:15)

### Demo Scene 1 — Analyze an Interaction (2:00–2:45)

**[VISUAL: Open the app in browser — Dashboard tab]**

**NARRATION:**
> "Let's see it in action. I'm logged in as Maria's caregiver — 78 years old, Alzheimer's moderate stage."

**[ACTION: Type into the text box or upload a short video clip]**
*(Suggested text input for live typing:)*
> *"Maria refused to take her afternoon heart medication. She started shouting that I was poisoning her and trying to steal her money. I showed her the pill bottle to prove she hadn't taken it yet, and she got more upset and knocked it off the table."*

**[ACTION: Click Analyze]**

**NARRATION:**
> "Watch the 7-agent pipeline run — each step lights up as it completes."

**[VISUAL: Show the step progress indicator in the UI]**

> "And here's the result."

**[VISUAL: Scroll through the coaching output — risk badge, behavioral analysis, try/avoid scripts, timeline, recommendations]**

> "Risk level MEDIUM. Observed behavior: Medication Refusal and Paranoia. The agent identified 'direct correction' as the trigger — exactly what I did when I showed her the pill bottle."
> "Here are exact scripts: what to avoid saying, and what to try instead."
> "And clinical recommendations grounded in Validation Therapy protocols retrieved from our RAG database."

---

### Demo Scene 2 — Coach Chat & HITL Profile Enrichment (2:45–3:30)

**[VISUAL: Scroll down to the Coach Chat section]**

**NARRATION:**
> "After the analysis, the conversational coach is automatically primed with the context — and the caregiver can ask follow-up questions."

**[ACTION: Type a question into coach chat]**
*(Suggested message:)*
> *"She really hates it when there are bright lights on in the room during this time of day. Is that normal and what can I do?"*

**[ACTION: Send — wait for response]**

**NARRATION:**
> "The ADK agent uses the MCP server to query care guidelines in real time — the response is grounded, not generic."

**[VISUAL: Show the coach's response]**

> "Now watch what happens next."

**[VISUAL: A suggestion banner appears — 'New trigger detected: bright lights' with Accept / Dismiss buttons]**

> "The Profile Enricher agent ran in the background. It detected that the caregiver mentioned a new trigger — bright lights — and is proposing it as a profile update. One click to accept, and it's saved to Maria's profile permanently."
> "This is the human-in-the-loop: the AI identifies what it learns from conversation, and the caregiver stays in control of what gets remembered."

---

### Demo Scene 3 — Interaction History (3:30–3:45)

**[VISUAL: Switch to the Profile tab, scroll to Interaction History Timeline]**

**NARRATION:**
> "Every analysis is logged to the database. Here's the history timeline — color-coded by risk level. Click any entry to expand the Try and Avoid phrases from that session."
> "Over time, this builds a longitudinal picture of the patient's behavioral patterns."

---

### Demo Scene 4 — Practice Simulator (3:45–4:00)

**[VISUAL: Switch to Simulator tab]**

**NARRATION:**
> "Caregivers can also practice before real situations. The Simulator lets you roleplay with a patient agent — Maria or Arthur — and see the agitation level respond in real time to what you say."

**[ACTION: Type a response and show agitation going down or up]**

> "Good technique: agitation drops. Wrong approach: it spikes."

---

### Demo Scene 5 — Security & Deployability (4:00–4:15)

**[VISUAL: Briefly show the login screen with API key, then switch to terminal showing docker-compose up]**

**NARRATION:**
> "The app ships with API key authentication, role separation between user and admin keys, and a 60-requests-per-minute rate limiter."
> "The full stack — FastAPI backend, React frontend, ChromaDB, and SQLite — deploys with a single `docker-compose up`."

---

## SECTION 6 — THE BUILD (4:15–4:40)

**[VISUAL: Slide — tech stack / key concepts grid]**

**NARRATION:**
> "Here's what's under the hood:"

> "**Multi-agent pipeline** — 7 Gemini agents, each with a Pydantic-enforced JSON output schema. Failures are isolated and diagnosable per step."

> "**Google ADK** — the conversational coach is an ADK Agent with tool use — it calls `query_care_guidelines` via the MCP server in real time."

> "**FastMCP over SSE** — three MCP tools: `get_patient_profile`, `log_safety_escalation`, and `query_care_guidelines`. The ADK agent consumes these via SSE."

> "**ChromaDB + Gemini text-embedding-004** — 18 clinical dementia care protocols indexed and retrieved by semantic similarity."

> "**Antigravity** — project skills in `.agents/skills/` cover setup, boot, RAG seeding, and deployment — all invocable by the agent."

> "**Human-in-the-loop** — the Profile Enricher surfaces suggestions; a human approves before anything changes."

---

## SECTION 7 — CLOSING (4:40–5:00)

**[VISUAL: Return to the app — calm final shot of the dashboard]**

**NARRATION:**
> "Dementia caregiving is one of the hardest jobs in the world. It's physically exhausting, emotionally devastating, and deeply isolating."

> "DementiaCare Coach doesn't replace human connection. It makes caregivers more effective — so the moments that matter can actually be moments of comfort."

> "Built for the Kaggle AI Agents Capstone. Thank you."

**[VISUAL: End card — project name, GitHub repo link, team names]**

---

## RECORDING NOTES

- **App state before recording**: Make sure Maria's profile is loaded, interaction history has at least 2-3 past logs, and backend is live with `GEMINI_API_KEY` set.
- **Pre-type the demo input** in a text file so you can paste it quickly during recording — avoid live typing errors.
- **Coach chat HITL moment**: For the "bright lights" trigger suggestion to appear, the backend must be online and `ProfileEnricherAgent` must find something new. Test this flow before recording.
- **Simulator**: Pre-load the Medication Refusal scenario and have Maria's first dialogue visible before you speak.
- **Total talking time budget**: 5 min = 300 seconds. Each section is tight — practice once end-to-end before final record.
- **Screen resolution**: Record at 1920×1080, browser at 100% zoom.
