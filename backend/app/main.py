import os
import json
import shutil
import tempfile
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.schemas import FinalCoachingResponse
from app.agents.orchestrator import OrchestratorAgent
from app.agents.simulator import SimulatorAgent, SimulatorResponse
from app.rag import seed_default_guidelines

app = FastAPI(title=settings.app_name)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate orchestrator and simulator agents
orchestrator = OrchestratorAgent()
simulator = SimulatorAgent()

# Local persistence paths
PATIENT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "patient_profile.json")

# Default Patient Profile
DEFAULT_PROFILE = {
    "name": "Arthur",
    "dementia_type": "Alzheimer's (Moderate Stage)",
    "triggers": ["direct correction", "being rushed", "loud noises", "asking 'do you remember?'"],
    "preferences": ["listening to 1950s big band music", "drinking chamomile tea", "talking about his past work as a carpenter"],
    "background": "Arthur is 78 years old. He lives at home with his daughter who is his primary caregiver. He often gets confused in the late afternoon (sundowning) and can refuse medication or personal care because he believes he has to go to work or that his daughter is trying to poison him."
}

def load_patient_profile() -> dict:
    if os.path.exists(PATIENT_FILE):
        try:
            with open(PATIENT_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_PROFILE
    return DEFAULT_PROFILE

def save_patient_profile(profile: dict):
    with open(PATIENT_FILE, "w") as f:
        json.dump(profile, f, indent=4)

# HTTP Request Schemas
class PatientProfileSchema(BaseModel):
    name: str
    dementia_type: str
    triggers: List[str]
    preferences: List[str]
    background: str

class TextAnalysisRequest(BaseModel):
    description: str

class SimulatorRequest(BaseModel):
    scenario: str
    chat_history: List[Dict[str, str]]


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "mode": "MOCK" if orchestrator.use_mock else "LIVE"
    }

@app.get("/patient", response_model=PatientProfileSchema)
def get_patient():
    return load_patient_profile()

@app.post("/patient", response_model=PatientProfileSchema)
def update_patient(profile: PatientProfileSchema):
    save_patient_profile(profile.model_dump())
    return profile

@app.post("/guidelines/seed")
def seed_guidelines():
    try:
        seed_default_guidelines()
        return {"status": "success", "message": "Guidelines collection seeded successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Seeding failed: {str(e)}"
        )

@app.post("/analyze/text", response_model=FinalCoachingResponse)
def analyze_text(request: TextAnalysisRequest):
    patient_profile = load_patient_profile()
    try:
        feedback = orchestrator.analyze_text(request.description, patient_profile)
        return feedback
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@app.post("/analyze/file", response_model=FinalCoachingResponse)
def analyze_file(file: UploadFile = File(...)):
    patient_profile = load_patient_profile()

    # Save uploaded file to a temporary file
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        feedback = orchestrator.analyze_file(
            file_path=temp_path,
            mime_type=file.content_type,
            patient_profile=patient_profile,
            original_filename=file.filename
        )
        return feedback
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File analysis failed: {str(e)}"
        )
    finally:
        # Clean up local temporary file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

@app.post("/simulator/step", response_model=SimulatorResponse)
def simulator_step(request: SimulatorRequest):
    patient_profile = load_patient_profile()
    try:
        response = simulator.run(
            scenario=request.scenario,
            chat_history=request.chat_history,
            patient_profile=patient_profile
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {str(e)}"
        )
