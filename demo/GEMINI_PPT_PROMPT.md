# Gemini Prompt: Create PowerPoint Deck for DementiaCare Coach

Use the following slide specifications to create a professional PowerPoint presentation.

**Global design rules to apply to every slide:**
- Color palette: Dark navy/slate background (#0f172a), primary accent teal (#06b6d4), secondary purple (#a78bfa), white text (#f8fafc), muted gray text (#94a3b8)
- Font: Headings in Inter Bold or Calibri Bold. Body in Inter Regular or Calibri.
- Slide size: 16:9 widescreen (1920x1080)
- Style: Modern, minimal, dark-mode tech dashboard aesthetic — similar to a SaaS product pitch deck
- No clipart. Use geometric shapes, icon-style line icons, and clean data layouts.
- Slide numbers in bottom right corner, small and muted.
- Do NOT use default PowerPoint themes. Apply a custom dark background to every slide.

---

## Slide 1: Title — DementiaCare Coach

**Detailed design prompt:**
Full-bleed dark navy background (#0f172a). In the top-left corner, place a small pill-shaped badge in teal (#06b6d4) with white text that reads "Kaggle AI Agents Capstone — Agents for Good". Centered vertically, the main headline in large white bold text (60–70pt): "DementiaCare Coach". Directly below in teal (#06b6d4), a subtitle line (28pt): "An AI-Powered Caregiver Co-Pilot". Below that, a short tagline in muted gray (#94a3b8, 18pt, italic): "Evidence-based coaching for dementia caregivers — available at 2am when no one else is." In the bottom-right, a soft glowing teal circle (decorative, low opacity ~15%) overlapping the corner. Bottom-left: team names in small muted text — "Catherine Balajadia · Adrian Balajadia · Avan Sargento".

**Script (narration during this slide):**
"It's 2 AM. Your 78-year-old mother is convinced someone is stealing her money. She's refusing her heart medication. She's getting more upset. You're exhausted. You don't know what to say — and everything you try seems to make it worse. What if you had an expert coach beside you, always available, who knew your mother personally — and could tell you exactly what to say?"

---

## Slide 2: The Problem — 55 Million People. 0 Trained Coaches at Home.

**Detailed design prompt:**
Dark navy background (#0f172a). Top-left: section label badge in dark gray pill shape with gray text "THE PROBLEM". Main headline in white bold text (44pt): "55 Million People. 0 Trained Coaches at Home." Below the headline, three large stat cards arranged horizontally in a row across the slide. Each card has: a dark slate card background (#1e293b), a thin teal top border (3px), a large bold teal number on top, and a short white description below. Card 1: "55M+" in 52pt teal, below it "people worldwide live with dementia" in 16pt white. Card 2: "70%" in 52pt teal, below it "cared for at home by family with no clinical training" in 16pt white. Card 3: "#1" in 52pt teal, below it "driver of premature institutionalization is caregiver burnout" in 16pt white. Below the stat cards, a horizontal divider line in teal at 20% opacity. Below that, a pull quote in italic white text (20pt), centered: "When a patient becomes agitated, caregivers instinctively argue, correct, or rush them. This almost always makes it worse." No images or clipart. Keep the layout clean and data-forward.

**Script (narration during this slide):**
"Over 55 million people worldwide live with dementia. The majority are cared for at home — by family members with no clinical training. When a patient becomes agitated, refuses medication, or wants to go home — caregivers instinctively argue, correct, or rush them. This almost always escalates the situation. There is no always-available, personalized coach. Caregiver burnout is one of the leading drivers of premature institutionalization. We built DementiaCare Coach to change that."

---

## Slide 3: Why Agents? — Not a Single Prompt

**Detailed design prompt:**
Dark navy background (#0f172a). Section label badge top-left in dark gray: "WHY AGENTS?". Headline in white bold (40pt): "Why Agents — Not a Single Prompt?" Below the headline, a two-column comparison layout taking up most of the slide. Left column header: a red-tinted pill badge with white text "Single LLM Call" (16pt, #ef4444 background). Right column header: a teal pill badge with white text "DementiaCare 7-Agent Pipeline" (16pt, #06b6d4 background). Below each header, list 4 rows of comparison items. Each row spans both columns — left item is a pain point (muted gray text, small red X icon), right item is the solution (white text, small green checkmark icon). Row 1 — Left: "Buries safety concerns in coaching text" / Right: "Dedicated SafetyEvaluator agent — always runs last, never skipped". Row 2 — Left: "Generic advice, no clinical grounding" / Right: "RAG retrieval against 18 indexed clinical protocols". Row 3 — Left: "One-size-fits-all output" / Right: "Patient profile + trigger history injected per run". Row 4 — Left: "No memory between sessions" / Right: "Persistent interaction history + HITL profile learning". Separate rows with thin horizontal lines in dark slate. Add a small decorative teal glowing dot in the top-right corner.

**Script (narration during this slide):**
"This problem needs agents — not a single prompt — because good dementia coaching requires multiple specialized reasoning steps that must happen in sequence. A single LLM call trying to do everything at once loses focus, hallucinates clinical details, and buries safety concerns in coaching output. Agents let us enforce separation of concerns: one agent detects behavior, one retrieves evidence-based clinical guidelines, one does the safety audit — and they only see the context they need. The result is coaching you can trust."

---

## Slide 4: Architecture — The 7-Agent Pipeline

**Detailed design prompt:**
Dark navy background (#0f172a). Section label badge top-left: "ARCHITECTURE". Headline in white bold (36pt): "7-Agent Sequential Pipeline". The main visual is a horizontal flow diagram centered on the slide, spanning the full width. Each agent is a rounded rectangle card. Use the following sequence left to right, connected by thin teal arrows (→): Card 1 (Step 0): dark slate background, teal top border, icon of a shield, text "Validation" below it and "Rejects noise & nonsense input" in small gray. Card 2 (Step 1): same style, brain icon, "Interaction Analyzer" / "Behavioral signals + timeline". Card 3 (Step 2): person icon, "Patient Context" / "Maps triggers & history". Then a branch from Step 2 showing a downward arrow to a ChromaDB RAG node — small separate card with purple (#a78bfa) accent, database icon, text "ChromaDB RAG" / "18 clinical protocols". Arrow goes back up to feed Card 4. Card 4 (Step 3): book icon, "Care Guidance" / "RAG-grounded protocols". Card 5 (Step 4): alert triangle icon in red (#ef4444 accent), "Safety Evaluator" / "Flags HIGH & EMERGENCY". Card 6 (Step 5): message icon, "Coaching Synthesizer" / "Final scripts + recommendations". Card 7 (Step 6): star icon in teal, "Profile Enricher" / "HITL: suggests profile updates". Below the pipeline, add two separate elements: on the left, a small box for "ADK Agent" (purple accent) with label "Conversational Coach — Google ADK + MCP tools"; on the right, a small box labeled "FastMCP over SSE" with three tool names: get_patient_profile · log_safety_escalation · query_care_guidelines. Connect the ADK box and the MCP box with a bidirectional arrow labeled "SSE". Font sizes inside cards: label ~12pt bold white, description ~9pt gray.

**Script (narration during this slide):**
"Here's how it works. The caregiver uploads a video, audio clip, or text description of a care interaction. It flows through a 7-step multi-agent pipeline — each step a dedicated Gemini agent with a Pydantic-enforced output schema. Step 0 — Validation: rejects nonsense before wasting tokens. Step 1 — Interaction Analyzer: extracts behavioral signals and agitation level. Step 2 — Patient Context: maps the patient's known triggers and history. Then ChromaDB RAG retrieves the top matching evidence-based clinical guidelines. Step 3 — Care Guidance synthesizes those into concrete protocols. Step 4 — Safety Evaluator is a dedicated pass that flags fall risk, medication omission, delirium signs, and writes HIGH or EMERGENCY alerts to the database for clinician review. Step 5 — Coaching Synthesizer assembles the final response. And Step 6 — the Profile Enricher — detects new triggers or preferences mentioned in coach chat and proposes them as human-approved profile updates. The conversational coach uses Google ADK and connects to the backend via a FastMCP server over SSE."

---

## Slide 5: Demo Transition — Let's See It In Action

**Detailed design prompt:**
Dark navy background (#0f172a). Centered on the slide: a large teal play button circle icon (outline style, ~200pt diameter) in the center-left third of the slide. To the right of the icon, two lines of text: first line in large bold white (48pt) "Live Demo", second line in muted gray (20pt) "DementiaCare Coach in action". Below those two lines, a short vertical list of four demo scenes as pill-shaped labels in dark slate (#1e293b) with a small teal left border: "01  Analyze a care interaction" / "02  Coach chat + HITL profile enrichment" / "03  Interaction history timeline" / "04  Practice simulator". Bottom of slide: a thin horizontal teal line (decorative). Overall feel: minimal, like a "now entering demo" chapter card.

**Script (narration during this slide):**
"Let's see it in action. I'm logged in as Maria's caregiver — 78 years old, Alzheimer's moderate stage."

---

## Slide 6: Demo Scene Callout — Analysis Result

**Detailed design prompt:**
Dark navy background (#0f172a). This is an annotation overlay slide shown briefly during the demo screen recording. Layout: left 60% of slide is a dark slate card (#1e293b) simulating what the analysis result looks like in the app. Inside the card, place: a risk badge in amber (#f59e0b) labeled "MEDIUM RISK", a heading "Medication Refusal & Paranoia", and two short lines of italic body text: "Observed trigger: Direct correction (showing pill bottle)" and "Try saying: 'I see you want to be sure you are safe. Let's have some tea first.'" The right 40% of the slide has a white bold annotation in 22pt: "7 agents. 1 coherent coaching response." Below it in gray: "Each agent sees only the context it needs — reducing hallucination and keeping safety isolated." A thin teal vertical divider line separates left and right sections. Top-right corner: small teal badge "PIPELINE OUTPUT".

**Script (narration during this slide):**
"Risk level MEDIUM. Observed behavior: Medication Refusal and Paranoia. The agent identified 'direct correction' as the trigger — exactly what I did when I showed her the pill bottle. Here are exact scripts: what to avoid saying, and what to try instead. And clinical recommendations grounded in Validation Therapy protocols retrieved from our RAG database."

---

## Slide 7: Demo Scene Callout — HITL Profile Enrichment

**Detailed design prompt:**
Dark navy background (#0f172a). Center of slide: a large notification/banner card in dark slate (#1e293b) with a teal left border (5px), styled like an in-app notification. Inside the banner card: a small teal sparkle/star icon top-left of card, then bold white text "New trigger detected by Profile Enricher" in 20pt. Below it in gray 14pt: "The coach conversation mentioned a new behavioral trigger not yet in Maria's profile." Then two large button-like elements side by side: a teal filled button labeled "✓ Accept — Add 'bright lights' to Maria's triggers" (white text), and a dark outline button labeled "✗ Dismiss". Below the banner, a short explanatory label in muted gray italic: "The Profile Enricher agent runs after every coach chat exchange. The caregiver always approves before any profile update is saved." Above the card, a section label in small caps teal text: "HUMAN-IN-THE-LOOP (HITL)". Top right: small white badge "Step 6 — ProfileEnricherAgent".

**Script (narration during this slide):**
"The Profile Enricher agent ran in the background. It detected that the caregiver mentioned a new trigger — bright lights — and is proposing it as a profile update. One click to accept, and it's saved to Maria's profile permanently. This is the human-in-the-loop: the AI identifies what it learns from conversation, and the caregiver stays in control of what gets remembered."

---

## Slide 8: Key Concepts Checklist — What We Built With

**Detailed design prompt:**
Dark navy background (#0f172a). Section label badge top-left: "THE BUILD". Headline in white bold (38pt): "Course Concepts — All Demonstrated." Below, a 2-column grid of 7 concept cards. Each card: dark slate background (#1e293b), a teal checkmark circle icon in the top-left of the card, concept name in white bold (16pt), and a short gray description below (12pt). Card 1: "Multi-Agent System (ADK)" — "7-step Gemini pipeline + ADK conversational coach". Card 2: "MCP Server" — "FastMCP over SSE — 3 tools: profile, safety, RAG". Card 3: "RAG" — "ChromaDB + Gemini text-embedding-004, 18 clinical guidelines". Card 4: "Human-in-the-Loop" — "ProfileEnricherAgent → caregiver approval before profile updates". Card 5: "Security" — "API key auth, role separation, 60 req/min rate limiter". Card 6: "Deployability" — "docker-compose up — 4-service stack, one command". Card 7: "Antigravity / Agent Skills" — ".agents/skills/ — setup, boot, deploy, seed". Card 7 spans the full bottom row width (centered). All checkmark icons in teal. Cards have a subtle teal glow border. Grid gap: even. Background has a faint grid pattern in very dark teal for texture.

**Script (narration during this slide):**
"Here's what's under the hood. A 7-step multi-agent pipeline each with Pydantic-enforced JSON output schemas — failures are isolated per step. Google ADK for the conversational coach with live tool use. FastMCP over SSE with three tools. ChromaDB and Gemini embeddings for RAG-grounded clinical advice. Human-in-the-loop profile enrichment. API key auth and rate limiting. And a full docker-compose stack for one-command deployment."

---

## Slide 9: Closing — End Card

**Detailed design prompt:**
Full-bleed dark navy background (#0f172a). Centered layout. Top: a thin horizontal teal line spanning 40% of the slide width, centered. Below it: main headline in large white bold (52pt): "DementiaCare Coach". Below that in teal (24pt, not bold): "For the caregivers who show up at 2am." Below that, a thin horizontal divider. Then team names in muted gray (16pt): "Catherine Balajadia · Adrian Balajadia · Avan Sargento". Below team names: "Kaggle AI Agents Capstone — Agents for Good" in small gray italic. Bottom-right quadrant: a decorative large translucent teal circle (background, ~400pt, 10% opacity) overlapping the corner. Bottom-left: a simple 3-icon row in teal line icons — a brain icon, a heart icon, a shield icon — spaced evenly, each ~30pt, representing intelligence, care, and safety.

**Script (narration during this slide):**
"Dementia caregiving is one of the hardest jobs in the world. It's physically exhausting, emotionally devastating, and deeply isolating. DementiaCare Coach doesn't replace human connection. It makes caregivers more effective — so the moments that matter can actually be moments of comfort. Built for the Kaggle AI Agents Capstone. Thank you."

---

## Final Instructions for Gemini

- Create all 9 slides as a single PowerPoint (.pptx) file.
- Apply the global design rules from the top of this prompt uniformly across all slides.
- Do not use stock images or clipart — all visuals should be built from shapes, icons (line style), and text.
- For Slide 4 (Architecture), build the pipeline flow diagram using connected shapes and arrows — not an image.
- For Slide 6 and 7 (Demo callouts), these are meant to be shown briefly over a screen recording — keep them semi-transparent-friendly (dark backgrounds work well for overlays).
- Export as a single .pptx file named: `DementiaCare_Coach_Pitch_Deck.pptx`
