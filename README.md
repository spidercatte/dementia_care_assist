# DementiaCare Coach 🧠❤️
**An AI-Powered Caregiver Co-Pilot utilizing a Modular 6-Agent Collaborative Pipeline**

DementiaCare Coach is an intelligent assistant designed to help family and clinical dementia caregivers manage difficult behaviors (agitation, confusion, refusal, wandering, emotional distress) using evidence-based practices (Validation Therapy, Habilitation, Teepa Snow's Positive Approach to Care).

This project was built for the **AI Agents: Intensive Vibe Coding Capstone Project** competition.

---

## Project Overview

### Problem
Dementia caregivers often face aggressive behaviors, confusion, wandering, and emotional distress. Most family caregivers receive little training and struggle to respond effectively in difficult situations.

### Solution
DementiaCare Coach is an AI agent that analyzes caregiver-patient interactions through video, audio, and patient history. The system provides personalized coaching recommendations grounded in dementia care best practices.

### Key Features (Product Goals)
* 📹 **Video interaction analysis**
* 🎭 **Emotion and behavior recognition**
* 💡 **Personalized coaching suggestions**
* 🧠 **Patient context awareness**
* 🏥 **Medical condition integration**
* 🤝 **Trauma-informed care guidance**
* 📊 **Caregiver education and feedback**

### How It Works
1. **Caregiver records an interaction.**
2. **AI analyzes verbal and non-verbal signals.**
3. **Patient profile is retrieved.**
4. **Agent reasons over:**
   * Dementia care guidelines
   * Occupational therapy practices
   * Nursing protocols
   * Patient history
5. **Personalized recommendations are generated.**

### Example Scenario
If a patient becomes agitated when reminded to take medication, the agent may identify that direct correction is escalating distress and suggest validation therapy techniques instead.

### Impact
The system helps caregivers reduce stress, improve communication, and potentially delay institutionalization while improving quality of life for dementia patients.

---

## Key Features

1. **Explicit 6-Agent Modular Architecture:**
   The backend splits the reasoning process across six specialized agents, coordinated by a central orchestrator:
   * 🎮 **Orchestrator Agent (`orchestrator.py`):** Acts as the pipeline controller. Coordinates state, handles inputs, invokes RAG, and manages the API fallback.
   * 🔍 **Interaction Analysis Agent (`interaction_analysis.py`):** Extracts observed behaviors, verbal/non-verbal cues, caregiver style, and agitation levels (1-10) from logs.
   * 📋 **Patient Context Agent (`patient_context.py`):** Examines history and staging to flag health risk factors and patient-specific triggers.
   * 📚 **Care Guidance Agent (`care_guidance.py`):** Queries guidelines and provides clinical recommendations.
   * ⚠️ **Safety & Escalation Agent (`safety_escalation.py`):** Audits safety hazards (falls, wandering, medication omissions, UTI signs).
   * 🎓 **Caregiver Coaching Agent (`caregiver_coaching.py`):** Converts clinical findings into compassionate step-by-step coaching scripts ("Try saying..." vs "Avoid saying...").

2. **Interactive Care Simulator (Maria):**
   A training sandbox where caregivers can text with a simulated patient (Maria). Maria's agitation level updates dynamically based on the caregiver's response patterns. Includes live coaching tips.

3. **Externalized Guidelines & RAG Library:**
   Care guidelines are stored in `backend/data/dementia_care_guidelines.md`. The RAG pipeline parses, embeds, and indexes these guidelines directly into ChromaDB.

4. **API-Resilient Mock Mode:**
   If the Gemini API key is missing or calls fail, the backend seamlessly falls back to local high-fidelity mock responses for typical scenarios (medication refusal, shower resistance, wants to go home), protecting the demonstration.

---

## Directory Structure

```
dementia_care/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── orchestrator.py
│   │   │   ├── interaction_analysis.py
│   │   │   ├── patient_context.py
│   │   │   ├── care_guidance.py
│   │   │   ├── safety_escalation.py
│   │   │   ├── caregiver_coaching.py
│   │   │   └── simulator.py
│   │   ├── main.py               # FastAPI routes
│   │   ├── rag.py                # ChromaDB vector indexer
│   │   ├── schemas.py            # Pydantic schemas
│   │   ├── mock_responses.py     # Local mock data provider
│   │   └── config.py
│   ├── data/
│   │   └── dementia_care_guidelines.md   # Externalized guidelines
│   └── requirements.txt
├── frontend/
│   └── ...
└── README.md
```

---

## Setup & Running Instructions

### 1. Configure Backend Environment
First, navigate to the `backend` directory, create a `.env` file, and enter your Google Gemini API key:
```bash
cd backend
cp .env.example .env
# Open .env and set:
# GEMINI_API_KEY=your_actual_api_key (Leave blank to run in MOCK mode!)
```

#### Start the Backend Server:
Activate the virtual environment and start the FastAPI uvicorn server:
```bash
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
*The backend API will run on `http://localhost:8000`. You can view the swagger docs at `http://localhost:8000/docs`.*

---

### 2. Configure & Run Frontend
In a new terminal window, navigate to the `frontend` directory:
```bash
cd frontend
npm install
npm run dev
```
*The frontend web app will open at `http://localhost:5173`.*

---

### 3. Seed the Guidelines Database (RAG)
When running the app for the first time, click the **"Seed RAG DB"** button in the header of the app to read `dementia_care_guidelines.md` and seed the local vector store.

---

## Future Work
* ⚡ **Real-time coaching**
* ⌚ **Wearable integration**
* 🏥 **EHR (Electronic Health Record) integration**
* 🔮 **Predictive behavior forecasting**
* 🎓 **Caregiver training simulations**
