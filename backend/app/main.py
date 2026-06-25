import os
import json
import shutil
import tempfile
import time
from collections import defaultdict
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Security, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.genai import types
from app.config import settings
from app.database import db_client
from app.schemas import FinalCoachingResponse, TranslationRequest
from app.agents.orchestrator import OrchestratorAgent
from app.agents.simulator import SimulatorAgent, SimulatorResponse
from app.rag import seed_default_guidelines
from app.mock_responses import get_mock_translation

# Rate Limiter implementation
class RateLimiter:
    def __init__(self, requests_limit: int = 60, window_seconds: int = 60):
        self.limit = requests_limit
        self.window = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.window]
        if len(self.requests[client_ip]) >= self.limit:
            return False
        self.requests[client_ip].append(now)
        return True

rate_limiter = RateLimiter(requests_limit=60, window_seconds=60)

# API Key & RBAC validation
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_user_key(api_key: Optional[str] = Security(API_KEY_HEADER)):
    if not settings.admin_api_key and not settings.user_api_key:
        return
    if api_key in (settings.admin_api_key, settings.user_api_key) and api_key != "":
        return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid User Access Key"
    )

def verify_admin_key(api_key: Optional[str] = Security(API_KEY_HEADER)):
    if not settings.admin_api_key:
        return
    if api_key == settings.admin_api_key and api_key != "":
        return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid Admin Access Key"
    )

def cleanup_old_gemini_files():
    if not settings.gemini_api_key:
        return
    try:
        from google import genai
        client = genai.Client(api_key=settings.gemini_api_key)
        print("[Startup] Scanning Gemini File API for orphaned files...", flush=True)
        for f in client.files.list():
            try:
                print(f"[Startup] Deleting orphaned file: {f.name}", flush=True)
                client.files.delete(name=f.name)
            except Exception as delete_err:
                print(f"[Startup] Failed to delete file {f.name}: {delete_err}", flush=True)
    except Exception as e:
        print(f"[Startup] Gemini File API cleanup error: {e}", flush=True)

app = FastAPI(title=settings.app_name)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    if request.url.path != "/health" and not request.url.path.startswith("/mcp") and not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests. Please try again later."}
        )
    return await call_next(request)

from app.mcp_server import mcp
app.mount("/mcp", mcp.sse_app())

# Instantiate orchestrator and simulator agents
orchestrator = OrchestratorAgent()
simulator = SimulatorAgent()

# Local persistence paths
PATIENT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "patient_profile.json")

# Default Patient Profile
DEFAULT_PROFILE = {
    "name": "Maria",
    "dementia_type": "Alzheimer's (Moderate Stage)",
    "triggers": ["direct correction", "being rushed", "loud noises", "asking 'do you remember?'"],
    "preferences": ["listening to 1950s big band music", "drinking chamomile tea", "talking about her past work as a gardener"],
    "background": "Maria is 78 years old. She lives at home with her daughter who is her primary caregiver. She often gets confused in the late afternoon (sundowning) and can refuse medication or personal care because she believes she has to go to work or that her daughter is trying to poison her."
}

ARTHUR_PROFILE = {
    "name": "Arthur",
    "dementia_type": "Lewy Body Dementia (Moderate Stage)",
    "triggers": ["hallucinations", "being corrected about visions", "sudden movements", "complex task demands"],
    "preferences": ["watching classic movies", "eating soft butterscotch candy", "holding a warm cup of coffee"],
    "background": "Arthur is 82 years old. He has Lewy Body dementia and experiences vivid visual hallucinations (often seeing children or small animals in the room). He gets highly anxious when others tell him these are not real. He is prone to motor fluctuations and stiffness, especially during transitions."
}

def init_db():
    db_client.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            dementia_type TEXT,
            triggers TEXT,
            preferences TEXT,
            background TEXT
        )
    """)

    # Seed Maria
    row = db_client.fetchone("SELECT COUNT(*) FROM patients WHERE name = ?", ("Maria",))
    if row and list(row.values())[0] == 0:
        # Try to load existing JSON file to migrate Maria's data
        maria_profile = DEFAULT_PROFILE
        if os.path.exists(PATIENT_FILE):
            try:
                with open(PATIENT_FILE, "r") as f:
                    temp_profile = json.load(f)
                    if temp_profile.get("name") == "Maria":
                        maria_profile = temp_profile
            except Exception:
                pass
        db_client.execute("""
            INSERT INTO patients (name, dementia_type, triggers, preferences, background)
            VALUES (?, ?, ?, ?, ?)
        """, (
            maria_profile["name"],
            maria_profile["dementia_type"],
            json.dumps(maria_profile["triggers"]),
            json.dumps(maria_profile["preferences"]),
            maria_profile["background"]
        ))

    # Seed Arthur
    row = db_client.fetchone("SELECT COUNT(*) FROM patients WHERE name = ?", ("Arthur",))
    if row and list(row.values())[0] == 0:
        db_client.execute("""
            INSERT INTO patients (name, dementia_type, triggers, preferences, background)
            VALUES (?, ?, ?, ?, ?)
        """, (
            ARTHUR_PROFILE["name"],
            ARTHUR_PROFILE["dementia_type"],
            json.dumps(ARTHUR_PROFILE["triggers"]),
            json.dumps(ARTHUR_PROFILE["preferences"]),
            ARTHUR_PROFILE["background"]
        ))

# Run database initialization
init_db()
try:
    seed_default_guidelines()
except Exception as e:
    print(f"Failed to auto-seed guidelines on startup: {e}")
try:
    cleanup_old_gemini_files()
except Exception as e:
    print(f"Failed to run Gemini File API startup cleanup: {e}")

def load_patient_profile(name: Optional[str] = None) -> dict:
    try:
        if name:
            row = db_client.fetchone("SELECT name, dementia_type, triggers, preferences, background FROM patients WHERE name = ?", (name,))
        else:
            row = db_client.fetchone("SELECT name, dementia_type, triggers, preferences, background FROM patients ORDER BY id ASC LIMIT 1")
        if row:
            return {
                "name": row["name"],
                "dementia_type": row["dementia_type"],
                "triggers": json.loads(row["triggers"]) if row["triggers"] else [],
                "preferences": json.loads(row["preferences"]) if row["preferences"] else [],
                "background": row["background"]
            }
    except Exception as e:
        print(f"Error loading patient profile: {e}")
    return DEFAULT_PROFILE

def load_all_patients() -> list:
    try:
        rows = db_client.fetchall("SELECT name, dementia_type, triggers, preferences, background FROM patients")
        return [
            {
                "name": r["name"],
                "dementia_type": r["dementia_type"],
                "triggers": json.loads(r["triggers"]) if r["triggers"] else [],
                "preferences": json.loads(r["preferences"]) if r["preferences"] else [],
                "background": r["background"]
            }
            for r in rows
        ]
    except Exception as e:
        print(f"Error loading all patients: {e}")
    return [DEFAULT_PROFILE]

def save_patient_profile(profile: dict):
    try:
        row = db_client.fetchone("SELECT id FROM patients WHERE name = ?", (profile.get("name"),))
        if row:
            db_client.execute("""
                UPDATE patients
                SET dementia_type = ?, triggers = ?, preferences = ?, background = ?
                WHERE id = ?
            """, (
                profile.get("dementia_type"),
                json.dumps(profile.get("triggers", [])),
                json.dumps(profile.get("preferences", [])),
                profile.get("background"),
                list(row.values())[0]
            ))
        else:
            db_client.execute("""
                INSERT INTO patients (name, dementia_type, triggers, preferences, background)
                VALUES (?, ?, ?, ?, ?)
            """, (
                profile.get("name"),
                profile.get("dementia_type"),
                json.dumps(profile.get("triggers", [])),
                json.dumps(profile.get("preferences", [])),
                profile.get("background")
            ))
    except Exception as e:
        print(f"Error saving patient profile: {e}")

# HTTP Request Schemas
class PatientProfileSchema(BaseModel):
    name: str
    dementia_type: str
    triggers: List[str]
    preferences: List[str]
    background: str

class TextAnalysisRequest(BaseModel):
    description: str
    patient_name: Optional[str] = None

class SimulatorRequest(BaseModel):
    scenario: str
    chat_history: List[Dict[str, str]]
    patient_name: Optional[str] = None


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "mode": "MOCK" if orchestrator.use_mock else "LIVE"
    }

@app.get("/patients", response_model=List[PatientProfileSchema])
def get_all_patients_endpoint(api_key: Optional[str] = Depends(verify_user_key)):
    return load_all_patients()

@app.get("/patient", response_model=PatientProfileSchema)
def get_patient(name: Optional[str] = None, api_key: Optional[str] = Depends(verify_user_key)):
    return load_patient_profile(name)

@app.post("/patient", response_model=PatientProfileSchema)
def update_patient(profile: PatientProfileSchema, api_key: Optional[str] = Depends(verify_user_key)):
    save_patient_profile(profile.model_dump())
    return profile

@app.post("/guidelines/seed")
def seed_guidelines(api_key: Optional[str] = Depends(verify_admin_key)):
    try:
        seed_default_guidelines()
        return {"status": "success", "message": "Guidelines collection seeded successfully."}
    except Exception as e:
        print(f"[Error] Guidelines seeding failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Seeding failed. Please check backend logs."
        )

@app.post("/analyze/text", response_model=FinalCoachingResponse)
def analyze_text(request: TextAnalysisRequest, api_key: Optional[str] = Depends(verify_user_key)):
    patient_profile = load_patient_profile(request.patient_name)
    try:
        feedback = orchestrator.analyze_text(request.description, patient_profile)
        return feedback
    except Exception as e:
        print(f"[Error] Text analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis pipeline failed. Please check backend logs."
        )

@app.post("/analyze/file", response_model=FinalCoachingResponse)
def analyze_file(file: UploadFile = File(...), patient_name: Optional[str] = Form(None), api_key: Optional[str] = Depends(verify_user_key)):
    patient_profile = load_patient_profile(patient_name)

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
        print(f"[Error] File analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File analysis pipeline failed. Please check backend logs."
        )
    finally:
        # Clean up local temporary file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

@app.post("/translate", response_model=FinalCoachingResponse)
def translate_feedback(request: TranslationRequest, api_key: Optional[str] = Depends(verify_user_key)):
    if orchestrator.use_mock or not orchestrator.client:
        return get_mock_translation(request.coaching_response, request.target_language)

    try:
        response_json = request.coaching_response.model_dump_json()
        prompt = (
            f"You are an expert medical translator specializing in dementia care counseling.\n"
            f"Translate all user-facing text values in the following JSON object to '{request.target_language}'.\n"
            f"Do not translate JSON keys, timestamps, agitation/confusion levels, risk levels, or other technical values.\n"
            f"Make sure to translate recommendations, descriptions, timelines, try_saying, avoid_saying, clinical advice, strengths, and opportunities.\n"
            f"Maintain the exact same JSON schema and structure. Output strictly the translated JSON matching the schema.\n\n"
            f"JSON object to translate:\n{response_json}"
        )
        response = orchestrator.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FinalCoachingResponse
            )
        )
        return FinalCoachingResponse.model_validate_json(response.text)
    except Exception as e:
        print(f"[Error] Translation failed: {e}")
        return get_mock_translation(request.coaching_response, request.target_language)

@app.post("/simulator/step", response_model=SimulatorResponse)
def simulator_step(request: SimulatorRequest, api_key: Optional[str] = Depends(verify_user_key)):
    patient_profile = load_patient_profile(request.patient_name)
    try:
        response = simulator.run(
            scenario=request.scenario,
            chat_history=request.chat_history,
            patient_profile=patient_profile
        )
        return response
    except Exception as e:
        print(f"[Error] Simulation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Simulation step failed. Please check backend logs."
        )
