# DementiaCare Coach — Slide Deck Outline
**Companion to VIDEO_SCRIPT.md**
**These are the slides that appear during non-demo sections of the video.**

---

## Slide 1 — Title Card (shown at ~0:28)
- **Headline:** DementiaCare Coach
- **Subline:** An AI-Powered Caregiver Co-Pilot
- **Tagline:** Real-time, evidence-based coaching for dementia caregivers — available at 2am when no one else is.
- **Visual:** Soft, warm photo of an elderly person's hands being held

---

## Slide 2 — The Problem (shown at ~0:32)
- **Headline:** 55 Million People. 0 Trained Coaches at Home.
- **Stats (3 bullet points):**
  - 55M+ people worldwide live with dementia
  - 70% are cared for at home by family members with no clinical training
  - Caregiver burnout → #1 driver of premature institutionalization
- **Pull quote:** *"When they argue back, they're not being difficult. They're doing what feels logical to them."*
- **Visual:** Simple iconographic stat layout

---

## Slide 3 — Why Agents? (shown at ~1:02)
- **Headline:** Why Agents — Not a Single Prompt?
- **3-column layout:**
  | Single LLM | DementiaCare Agents |
  |---|---|
  | Buries safety flags | Dedicated safety agent — always runs |
  | Generic advice | RAG-grounded clinical protocols |
  | One size fits all | Personalized to the patient's profile |
  | No memory | Persistent interaction history + HITL learning |
- **Visual:** Side-by-side comparison cards

---

## Slide 4 — Architecture Diagram (shown at ~1:32)
- Use the existing `architecture_diagram.html` exported as an image or screen-recorded
- Animate each step lighting up as you describe it in voiceover
- **Key labels to highlight:**
  - 7-Agent Sequential Pipeline
  - ChromaDB RAG
  - FastMCP over SSE
  - ADK Conversational Agent
  - HITL Profile Enricher

---

## Slide 5 — Key Course Concepts Checklist (shown at ~4:17)
- **Headline:** What We Built With
- **Checklist grid:**

  | Concept | How |
  |---|---|
  | ✅ Multi-Agent System (ADK) | 7-step pipeline + ADK conversational agent |
  | ✅ MCP Server | FastMCP over SSE — 3 tools (profile, safety, RAG) |
  | ✅ RAG | ChromaDB + Gemini text-embedding-004, 18 clinical guidelines |
  | ✅ Human-in-the-Loop | ProfileEnricherAgent → caregiver approval before profile update |
  | ✅ Security | API key auth, role separation, rate limiting (60 req/min/IP) |
  | ✅ Deployability | docker-compose up — 4-service stack |
  | ✅ Antigravity | Agent skills in .agents/skills/ — setup, boot, deploy, seed |

---

## Slide 6 — End Card (shown at ~4:58)
- **Headline:** DementiaCare Coach
- **Subline:** Kaggle AI Agents Capstone — Agents for Good
- **Team:** Catherine Balajadia · Adrian Balajadia · Avan Sargento
- **GitHub:** [repo link]
- **Visual:** App screenshot or logo

---

## Design Notes
- Color palette: match the app's dark teal + slate theme (`--primary: #06b6d4`, dark backgrounds)
- Font: clean sans-serif (Inter or similar)
- Keep each slide to 1 key idea — no paragraph text
- Slide transitions: simple fade, no animations except the architecture diagram
