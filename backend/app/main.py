import os
import json
import shutil
import tempfile
import time
import asyncio
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
from app.agents.conversational_coach import ConversationalCoachAgent
from app.agents.profile_enricher import ProfileEnricherAgent
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
    # Bypassed for hackathon demo
    return

def verify_admin_key(api_key: Optional[str] = Security(API_KEY_HEADER)):
    # Bypassed for hackathon demo
    return

def cleanup_old_gemini_files():
    if not settings.gemini_api_key:
        return
    try:
        from google import genai
        client = genai.Client(api_key=settings.gemini_api_key)
        print("[Startup] Scanning Gemini File API for orphaned files...", flush=True)
        for f in client.files.list():
            try:
                if not f.name:
                    continue
                print(f"[Startup] Deleting orphaned file: {f.name}", flush=True)
                client.files.delete(name=f.name)
            except Exception as delete_err:
                print(f"[Startup] Failed to delete file {f.name}: {delete_err}", flush=True)
    except Exception as e:
        print(f"[Startup] Gemini File API cleanup error: {e}", flush=True)

async def periodic_gemini_file_cleanup():
    while True:
        try:
            # Run cleanup every 15 minutes (900 seconds)
            await asyncio.sleep(900)
            print("[Background Cleanup] Running periodic cleanup of Gemini File API...", flush=True)
            cleanup_old_gemini_files()
        except asyncio.CancelledError:
            print("[Background Cleanup] Periodic cleanup task cancelled.", flush=True)
            break
        except Exception as e:
            print(f"[Background Cleanup] Periodic cleanup encountered an error: {e}", flush=True)

app = FastAPI(title=settings.app_name)

@app.on_event("startup")
async def start_periodic_cleanup():
    asyncio.create_task(periodic_gemini_file_cleanup())

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
    if request.url.path != "/health" and not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests. Please try again later."}
        )
    return await call_next(request)

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
    "background": "Maria is 78 years old. She lives at home with her daughter who is her primary caregiver. She often gets confused in the late afternoon (sundowning) and can refuse medication or personal care because she believes she has to go to work or that her daughter is trying to poison her.",
    "medications": [
        {"name": "Donepezil (Aricept)", "purpose": "memory / cognition"},
        {"name": "Metformin", "purpose": "Type 2 diabetes"},
        {"name": "Quetiapine (low dose)", "purpose": "agitation / sleep"}
    ],
    "conditions": ["Type 2 Diabetes", "Hypertension", "Osteoporosis"],
    "allergies": ["Penicillin"],
    "fall_risk": "Medium",
    "mobility_aids": ["walker"],
    "diet_texture": "Soft",
    "sensory_aids": ["glasses"],
    "care_notes": (
        "Maria responds well to validation therapy and redirection to familiar memories. She becomes "
        "distressed when corrected or when her sense of routine is disrupted. Approach her with a calm, "
        "unhurried tone. Music from the 1950s is particularly effective for de-escalation during "
        "sundowning episodes. Her diabetes management requires monitoring intake during agitated episodes "
        "when she may refuse food."
    ),
}

ARTHUR_PROFILE = {
    "name": "Arthur",
    "dementia_type": "Lewy Body Dementia (Moderate Stage)",
    "triggers": [
        "Visual hallucinations being denied or dismissed",
        "Being corrected about visions he sees",
        "Sudden movements in his peripheral vision",
        "Complex task demands during motor-off periods",
    ],
    "preferences": [
        "watching classic movies",
        "eating soft butterscotch candy",
        "holding a warm cup of coffee",
        "Discussing engineering or machinery topics",
    ],
    "background": (
        "Arthur is 82 years old. He has Lewy Body dementia and experiences vivid visual hallucinations "
        "(often seeing children or small animals in the room). He gets highly anxious when others tell him "
        "these are not real. He is prone to motor fluctuations and stiffness, especially during transitions. "
        "He was a retired engineer who takes pride in his problem-solving abilities."
    ),
    "medications": [
        {"name": "Rivastigmine (Exelon)", "purpose": "memory / cognition"},
        {"name": "Carbidopa-Levodopa", "purpose": "Parkinson's-like motor symptoms"},
        {"name": "Melatonin", "purpose": "sleep regulation"}
    ],
    "conditions": ["Lewy Body Dementia", "Parkinsonism", "Atrial Fibrillation"],
    "allergies": [],
    "fall_risk": "High",
    "mobility_aids": ["cane", "grab bars"],
    "diet_texture": "Regular",
    "sensory_aids": ["hearing aids", "glasses"],
    "care_notes": (
        "Never dismiss or argue about Arthur's hallucinations — acknowledge them with calm reassurance "
        "('I don't see them, but I understand they look real to you'). Approach him slowly and announce "
        "your presence before touching. Schedule personal care tasks during motor-on periods (typically "
        "mid-morning). His atrial fibrillation increases fall risk during dizziness episodes; ensure grab "
        "bars are within reach at all times. Classic films from the 1940s-1960s provide reliable comfort "
        "and distraction."
    ),
}

def init_db():
    db_client.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            dementia_type TEXT,
            triggers TEXT,
            preferences TEXT,
            background TEXT,
            medications TEXT,
            conditions TEXT,
            allergies TEXT,
            fall_risk TEXT,
            mobility_aids TEXT,
            diet_texture TEXT,
            sensory_aids TEXT,
            care_notes TEXT
        )
    """)
    # Migrate existing tables that predate the new health columns
    for col, default in [
        ("medications", "[]"), ("conditions", "[]"), ("allergies", "[]"),
        ("fall_risk", "Low"), ("mobility_aids", "[]"),
        ("diet_texture", "Regular"), ("sensory_aids", "[]"),
        ("care_notes", ""),
    ]:
        try:
            db_client.execute(f"ALTER TABLE patients ADD COLUMN {col} TEXT DEFAULT '{default}'")
        except Exception:
            pass  # column already exists
    db_client.execute("""
        CREATE TABLE IF NOT EXISTS safety_escalations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            urgency_level TEXT NOT NULL,
            safety_reason TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    db_client.execute("""
        CREATE TABLE IF NOT EXISTS interaction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            raw_input TEXT,
            observed_behavior TEXT,
            likely_trigger TEXT,
            risk_level TEXT,
            try_saying TEXT,
            avoid_saying TEXT,
            analysis_json TEXT
        )
    """)
    db_client.execute("""
        CREATE TABLE IF NOT EXISTS coach_chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    db_client.execute("""
        CREATE TABLE IF NOT EXISTS consent_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            granted_by TEXT,
            scope TEXT NOT NULL, -- 'text' | 'audio' | 'video'
            granted_at TEXT NOT NULL,
            revoked_at TEXT
        )
    """)
    db_client.execute("""
        CREATE TABLE IF NOT EXISTS consent_audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            required_scope TEXT NOT NULL,
            allowed_scope TEXT NOT NULL,
            granted_by TEXT,
            result TEXT NOT NULL, -- 'GRANTED' | 'REJECTED'
            timestamp TEXT NOT NULL
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
            INSERT INTO patients (name, dementia_type, triggers, preferences, background,
                medications, conditions, allergies, fall_risk, mobility_aids, diet_texture, sensory_aids, care_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            maria_profile["name"], maria_profile["dementia_type"],
            json.dumps(maria_profile["triggers"]), json.dumps(maria_profile["preferences"]),
            maria_profile["background"],
            json.dumps(maria_profile.get("medications", [])),
            json.dumps(maria_profile.get("conditions", [])),
            json.dumps(maria_profile.get("allergies", [])),
            maria_profile.get("fall_risk", "Low"),
            json.dumps(maria_profile.get("mobility_aids", [])),
            maria_profile.get("diet_texture", "Regular"),
            json.dumps(maria_profile.get("sensory_aids", [])),
            maria_profile.get("care_notes", ""),
        ))

    # Seed Arthur
    row = db_client.fetchone("SELECT COUNT(*) FROM patients WHERE name = ?", ("Arthur",))
    if row and list(row.values())[0] == 0:
        db_client.execute("""
            INSERT INTO patients (name, dementia_type, triggers, preferences, background,
                medications, conditions, allergies, fall_risk, mobility_aids, diet_texture, sensory_aids, care_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ARTHUR_PROFILE["name"], ARTHUR_PROFILE["dementia_type"],
            json.dumps(ARTHUR_PROFILE["triggers"]), json.dumps(ARTHUR_PROFILE["preferences"]),
            ARTHUR_PROFILE["background"],
            json.dumps(ARTHUR_PROFILE.get("medications", [])),
            json.dumps(ARTHUR_PROFILE.get("conditions", [])),
            json.dumps(ARTHUR_PROFILE.get("allergies", [])),
            ARTHUR_PROFILE.get("fall_risk", "Low"),
            json.dumps(ARTHUR_PROFILE.get("mobility_aids", [])),
            ARTHUR_PROFILE.get("diet_texture", "Regular"),
            json.dumps(ARTHUR_PROFILE.get("sensory_aids", [])),
            ARTHUR_PROFILE.get("care_notes", ""),
        ))

    # Backfill care_notes for existing rows that predate the field
    for profile in [DEFAULT_PROFILE, ARTHUR_PROFILE]:
        care_notes = profile.get("care_notes", "")
        if care_notes:
            try:
                db_client.execute(
                    "UPDATE patients SET care_notes = ? WHERE name = ? AND (care_notes IS NULL OR care_notes = '')",
                    (care_notes, profile["name"])
                )
            except Exception:
                pass

    # Backfill updated fields (triggers, preferences, background) for existing rows
    for profile in [DEFAULT_PROFILE, ARTHUR_PROFILE]:
        try:
            db_client.execute(
                "UPDATE patients SET triggers = ?, preferences = ?, background = ? WHERE name = ?",
                (
                    json.dumps(profile["triggers"]),
                    json.dumps(profile["preferences"]),
                    profile["background"],
                    profile["name"],
                )
            )
        except Exception:
            pass

    # Seed default surrogate consents
    try:
        row_consent = db_client.fetchone("SELECT COUNT(*) FROM consent_records WHERE patient_name = ?", ("Maria",))
        if row_consent and list(row_consent.values())[0] == 0:
            db_client.execute("""
                INSERT INTO consent_records (patient_name, granted_by, scope, granted_at)
                VALUES (?, ?, ?, ?)
            """, ("Maria", "Sarah (Daughter / Power of Attorney)", "video", "2026-06-29T12:00:00Z"))

        row_consent_arthur = db_client.fetchone("SELECT COUNT(*) FROM consent_records WHERE patient_name = ?", ("Arthur",))
        if row_consent_arthur and list(row_consent_arthur.values())[0] == 0:
            db_client.execute("""
                INSERT INTO consent_records (patient_name, granted_by, scope, granted_at)
                VALUES (?, ?, ?, ?)
            """, ("Arthur", "Robert (Son / Legal Guardian)", "audio", "2026-06-29T12:00:00Z"))
    except Exception as e:
        print(f"Error seeding default consents: {e}")

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

def _row_to_profile(row: dict) -> dict:
    return {
        "name": row["name"],
        "dementia_type": row["dementia_type"],
        "triggers": json.loads(row["triggers"]) if row["triggers"] else [],
        "preferences": json.loads(row["preferences"]) if row["preferences"] else [],
        "background": row["background"],
        "medications": json.loads(row["medications"]) if row.get("medications") else [],
        "conditions": json.loads(row["conditions"]) if row.get("conditions") else [],
        "allergies": json.loads(row["allergies"]) if row.get("allergies") else [],
        "fall_risk": row.get("fall_risk") or "Low",
        "mobility_aids": json.loads(row["mobility_aids"]) if row.get("mobility_aids") else [],
        "diet_texture": row.get("diet_texture") or "Regular",
        "sensory_aids": json.loads(row["sensory_aids"]) if row.get("sensory_aids") else [],
    }

def load_patient_profile(name: Optional[str] = None) -> dict:
    try:
        if name:
            row = db_client.fetchone("SELECT * FROM patients WHERE name = ?", (name,))
        else:
            row = db_client.fetchone("SELECT * FROM patients ORDER BY id ASC LIMIT 1")
        if row:
            return _row_to_profile(row)
    except Exception as e:
        print(f"Error loading patient profile: {e}")
    return DEFAULT_PROFILE

def load_all_patients() -> list:
    try:
        rows = db_client.fetchall("SELECT * FROM patients")
        return [_row_to_profile(r) for r in rows]
    except Exception as e:
        print(f"Error loading all patients: {e}")
    return [DEFAULT_PROFILE]

def save_patient_profile(profile: dict):
    try:
        row = db_client.fetchone("SELECT id FROM patients WHERE name = ?", (profile.get("name"),))
        params = (
            profile.get("dementia_type"),
            json.dumps(profile.get("triggers", [])),
            json.dumps(profile.get("preferences", [])),
            profile.get("background"),
            json.dumps(profile.get("medications", [])),
            json.dumps(profile.get("conditions", [])),
            json.dumps(profile.get("allergies", [])),
            profile.get("fall_risk", "Low"),
            json.dumps(profile.get("mobility_aids", [])),
            profile.get("diet_texture", "Regular"),
            json.dumps(profile.get("sensory_aids", [])),
            profile.get("care_notes", ""),
        )
        if row:
            db_client.execute("""
                UPDATE patients
                SET dementia_type = ?, triggers = ?, preferences = ?, background = ?,
                    medications = ?, conditions = ?, allergies = ?, fall_risk = ?,
                    mobility_aids = ?, diet_texture = ?, sensory_aids = ?, care_notes = ?
                WHERE id = ?
            """, params + (list(row.values())[0],))
        else:
            db_client.execute("""
                INSERT INTO patients (name, dementia_type, triggers, preferences, background,
                    medications, conditions, allergies, fall_risk, mobility_aids, diet_texture, sensory_aids, care_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (profile.get("name"),) + params)
    except Exception as e:
        print(f"Error saving patient profile: {e}")

def save_interaction_log(patient_name: str, raw_input: str, analysis: dict):
    try:
        from datetime import datetime, timezone
        db_client.execute("""
            INSERT INTO interaction_history (
                patient_name, timestamp, raw_input, observed_behavior, likely_trigger, risk_level, try_saying, avoid_saying, analysis_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_name,
            datetime.now(timezone.utc).isoformat(),
            raw_input,
            analysis.get("observed_behavior"),
            analysis.get("likely_trigger"),
            analysis.get("risk_level"),
            analysis.get("try_saying"),
            analysis.get("avoid_saying"),
            json.dumps(analysis)
        ))
    except Exception as e:
        print(f"Error saving interaction log: {e}")

def save_coach_message(patient_name: str, role: str, content: str):
    try:
        from datetime import datetime, timezone
        db_client.execute("""
            INSERT INTO coach_chat_history (patient_name, timestamp, role, content)
            VALUES (?, ?, ?, ?)
        """, (
            patient_name,
            datetime.now(timezone.utc).isoformat(),
            role,
            content
        ))
    except Exception as e:
        print(f"Error saving coach message: {e}")

def get_interaction_logs(patient_name: str) -> list:
    try:
        rows = db_client.fetchall("""
            SELECT id, timestamp, raw_input, observed_behavior, likely_trigger, risk_level, try_saying, avoid_saying, analysis_json
            FROM interaction_history
            WHERE patient_name = ?
            ORDER BY id DESC
        """, (patient_name,))
        return [
            {
                "id": r["id"],
                "timestamp": r["timestamp"],
                "raw_input": r["raw_input"],
                "observed_behavior": r["observed_behavior"],
                "likely_trigger": r["likely_trigger"],
                "risk_level": r["risk_level"],
                "try_saying": r["try_saying"],
                "avoid_saying": r["avoid_saying"],
                "analysis": json.loads(r["analysis_json"]) if r["analysis_json"] else {}
            }
            for r in rows
        ]
    except Exception as e:
        print(f"Error getting interaction logs: {e}")
        return []

def get_coach_messages(patient_name: str) -> list:
    try:
        rows = db_client.fetchall("""
            SELECT role, content
            FROM coach_chat_history
            WHERE patient_name = ?
            ORDER BY id ASC
        """, (patient_name,))
        return [{"role": r["role"], "content": r["content"]} for r in rows]
    except Exception as e:
        print(f"Error getting coach messages: {e}")
        return []

def clear_patient_history(patient_name: str):
    try:
        db_client.execute("DELETE FROM interaction_history WHERE patient_name = ?", (patient_name,))
        db_client.execute("DELETE FROM coach_chat_history WHERE patient_name = ?", (patient_name,))
    except Exception as e:
        print(f"Error clearing history: {e}")

def process_analysis_suggestions_and_log(feedback: FinalCoachingResponse, patient_profile: dict, raw_input: str):
    """Persists the analysis and populates suggested_triggers with any new triggers not yet in the patient profile."""
    save_interaction_log(patient_profile["name"], raw_input, feedback.model_dump())

    if feedback.observed_behavior == "Input Insufficient / Invalid":
        return

    existing_lower = {t.lower() for t in patient_profile.get("triggers", [])}
    candidates: List[str] = []

    if feedback.behavior_analysis and feedback.behavior_analysis.patient_triggers:
        for t in feedback.behavior_analysis.patient_triggers:
            if t and t.lower() not in existing_lower and t not in candidates:
                candidates.append(t)

    if (
        feedback.likely_trigger
        and feedback.likely_trigger not in ("N/A", "N/A - Insufficient description details")
        and feedback.likely_trigger.lower() not in existing_lower
        and feedback.likely_trigger not in candidates
    ):
        candidates.append(feedback.likely_trigger)

    if candidates:
        feedback.suggested_triggers = candidates

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

class CoachChatRequest(BaseModel):
    chat_history: List[Dict[str, Any]]
    feedback_context: Dict[str, Any]
    patient_name: Optional[str] = None
class ConsentRecordSchema(BaseModel):
    patient_name: str
    granted_by: str
    scope: str # 'text' | 'audio' | 'video'
    granted_at: str
    revoked_at: Optional[str] = None



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
        process_analysis_suggestions_and_log(feedback, patient_profile, request.description)
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
    filename = file.filename or "uploaded_file"
    suffix = os.path.splitext(filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        feedback = orchestrator.analyze_file(
            file_path=temp_path,
            mime_type=file.content_type or "application/octet-stream",
            patient_profile=patient_profile,
            original_filename=file.filename
        )
        process_analysis_suggestions_and_log(feedback, patient_profile, f"Uploaded file: {filename}")
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
        if not response.text:
            return get_mock_translation(request.coaching_response, request.target_language)
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

@app.post("/coach/chat")
def coach_chat(request: CoachChatRequest, api_key: Optional[str] = Depends(verify_user_key)):
    patient_profile = load_patient_profile(request.patient_name)

    client = orchestrator.client
    if orchestrator.use_mock or not client:
        last_message = request.chat_history[-1]["content"] if request.chat_history else ""
        response_text = f"[MOCK COACH] I hear your concern about {patient_profile.get('name')} regarding '{last_message}'. Remember to use validation therapy: connect before correcting."
        if request.chat_history:
            save_coach_message(patient_profile["name"], "user", last_message)
        save_coach_message(patient_profile["name"], "assistant", response_text)

        # Simulating suggested updates for testing in mock mode
        suggested_updates = None
        last_lower = last_message.lower()
        if "bright light" in last_lower or "glare" in last_lower:
            suggested_updates = {
                "new_triggers": ["bright lights"],
                "new_preferences": []
            }
        elif "music" in last_lower or "song" in last_lower:
            suggested_updates = {
                "new_triggers": [],
                "new_preferences": ["listening to music"]
            }

        return {
            "response": response_text,
            "suggested_profile_updates": suggested_updates
        }

    try:
        agent = ConversationalCoachAgent(client)
        response_text = agent.run(
            chat_history=request.chat_history,
            patient_profile=patient_profile,
            feedback_context=request.feedback_context
        )
        if request.chat_history:
            save_coach_message(patient_profile["name"], "user", request.chat_history[-1]["content"])
        save_coach_message(patient_profile["name"], "assistant", response_text)

        # Run ProfileEnricherAgent
        suggested_updates = None
        try:
            enricher = ProfileEnricherAgent(client)
            enricher_res = enricher.run(
                chat_history=request.chat_history + [{"role": "assistant", "content": response_text}],
                patient_profile=patient_profile
            )
            if enricher_res.new_triggers or enricher_res.new_preferences:
                suggested_updates = {
                    "new_triggers": enricher_res.new_triggers,
                    "new_preferences": enricher_res.new_preferences
                }
        except Exception as enrich_err:
            print(f"Profile enrichment failed: {enrich_err}")

        return {
            "response": response_text,
            "suggested_profile_updates": suggested_updates
        }
    except Exception as e:
        print(f"[Error] Coach chat failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Coach chat session failed. Please check backend logs."
        )

@app.get("/patient/{name}/interactions")
def get_interactions_endpoint(name: str, api_key: Optional[str] = Depends(verify_user_key)):
    return get_interaction_logs(name)

@app.get("/patient/{name}/coach-chat")
def get_coach_chat_endpoint(name: str, api_key: Optional[str] = Depends(verify_user_key)):
    return get_coach_messages(name)

@app.delete("/patient/{name}/history")
def delete_history_endpoint(name: str, api_key: Optional[str] = Depends(verify_user_key)):
    clear_patient_history(name)
    return {"status": "success", "message": f"Cleared history for {name}"}

@app.get("/patient/{name}/consent", response_model=Optional[ConsentRecordSchema])
def get_patient_consent_endpoint(name: str, api_key: Optional[str] = Depends(verify_user_key)):
    try:
        row = db_client.fetchone("""
            SELECT patient_name, granted_by, scope, granted_at, revoked_at
            FROM consent_records WHERE patient_name = ? AND revoked_at IS NULL
        """, (name,))
        if not row:
            return None
        return ConsentRecordSchema(
            patient_name=row["patient_name"],
            granted_by=row["granted_by"],
            scope=row["scope"],
            granted_at=row["granted_at"],
            revoked_at=row["revoked_at"]
        )
    except Exception as e:
        print(f"Error fetching consent: {e}")
        return None

@app.post("/patient/{name}/consent")
def set_patient_consent_endpoint(name: str, consent: ConsentRecordSchema, api_key: Optional[str] = Depends(verify_user_key)):
    try:
        # Revoke existing consent records first
        db_client.execute("UPDATE consent_records SET revoked_at = ? WHERE patient_name = ? AND revoked_at IS NULL", (consent.granted_at, name))
        db_client.execute("""
            INSERT INTO consent_records (patient_name, granted_by, scope, granted_at, revoked_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, consent.granted_by, consent.scope, consent.granted_at, consent.revoked_at))
        return {"status": "success", "message": f"Surrogate consent scope '{consent.scope}' updated/enforced for {name}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update surrogate consent: {e}"
        )
