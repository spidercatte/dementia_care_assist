#!/usr/bin/env python3
"""
Seeds the production PostgreSQL (Cloud SQL) database with patient profiles.
Called by seed_cloud_sql.sh — reads connection config from environment variables.

Required env vars: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
Safe to re-run: uses INSERT ... ON CONFLICT DO UPDATE (upsert).
"""

import json
import os
import sys

try:
    import psycopg2
except ImportError:
    print("Error: psycopg2-binary is required. Run: pip install psycopg2-binary")
    sys.exit(1)

DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ.get("DB_NAME", "dementia_care")

MARIA = {
    "name": "Maria",
    "dementia_type": "Alzheimer's (Moderate Stage)",
    "triggers": ["direct correction", "being rushed", "loud noises", "asking 'do you remember?'"],
    "preferences": ["listening to 1950s big band music", "drinking chamomile tea", "talking about her past work as a gardener"],
    "background": (
        "Maria is 78 years old. She lives at home with her daughter who is her primary caregiver. "
        "She often gets confused in the late afternoon (sundowning) and can refuse medication or "
        "personal care because she believes she has to go to work or that her daughter is trying to poison her."
    ),
    "medications": [
        {"name": "Donepezil (Aricept)", "purpose": "memory / cognition"},
        {"name": "Metformin", "purpose": "Type 2 diabetes"},
        {"name": "Quetiapine (low dose)", "purpose": "agitation / sleep"},
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

ARTHUR = {
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
        {"name": "Melatonin", "purpose": "sleep regulation"},
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

PATIENTS = [MARIA, ARTHUR]

CREATE_PATIENTS = """
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
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
"""

CREATE_SAFETY_ESCALATIONS = """
CREATE TABLE IF NOT EXISTS safety_escalations (
    id SERIAL PRIMARY KEY,
    urgency_level TEXT NOT NULL,
    safety_reason TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""

CREATE_INTERACTION_HISTORY = """
CREATE TABLE IF NOT EXISTS interaction_history (
    id SERIAL PRIMARY KEY,
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
"""

CREATE_COACH_CHAT_HISTORY = """
CREATE TABLE IF NOT EXISTS coach_chat_history (
    id SERIAL PRIMARY KEY,
    patient_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL
)
"""

UPSERT_PATIENT = """
INSERT INTO patients (
    name, dementia_type, triggers, preferences, background,
    medications, conditions, allergies, fall_risk, mobility_aids, diet_texture, sensory_aids, care_notes
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (name) DO UPDATE SET
    dementia_type  = EXCLUDED.dementia_type,
    triggers       = EXCLUDED.triggers,
    preferences    = EXCLUDED.preferences,
    background     = EXCLUDED.background,
    medications    = EXCLUDED.medications,
    conditions     = EXCLUDED.conditions,
    allergies      = EXCLUDED.allergies,
    fall_risk      = EXCLUDED.fall_risk,
    mobility_aids  = EXCLUDED.mobility_aids,
    diet_texture   = EXCLUDED.diet_texture,
    sensory_aids   = EXCLUDED.sensory_aids,
    care_notes     = EXCLUDED.care_notes
"""

# Migration: add columns if they don't exist yet (for existing databases)
MIGRATION_COLUMNS = [
    ("medications",  "TEXT DEFAULT '[]'"),
    ("conditions",   "TEXT DEFAULT '[]'"),
    ("allergies",    "TEXT DEFAULT '[]'"),
    ("fall_risk",    "TEXT DEFAULT 'Low'"),
    ("mobility_aids","TEXT DEFAULT '[]'"),
    ("diet_texture", "TEXT DEFAULT 'Regular'"),
    ("sensory_aids", "TEXT DEFAULT '[]'"),
    ("care_notes",   "TEXT DEFAULT ''"),
]


def main() -> None:
    print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )
    conn.autocommit = False
    cur = conn.cursor()

    print("Creating tables if not exist...")
    cur.execute(CREATE_PATIENTS)
    cur.execute(CREATE_SAFETY_ESCALATIONS)
    cur.execute(CREATE_INTERACTION_HISTORY)
    cur.execute(CREATE_COACH_CHAT_HISTORY)

    print("Running column migrations...")
    for col, definition in MIGRATION_COLUMNS:
        try:
            cur.execute(f"ALTER TABLE patients ADD COLUMN IF NOT EXISTS {col} {definition}")
        except Exception as e:
            print(f"  Migration warning ({col}): {e}")
            conn.rollback()

    print("Upserting patient profiles...")
    for patient in PATIENTS:
        cur.execute(UPSERT_PATIENT, (
            patient["name"],
            patient["dementia_type"],
            json.dumps(patient["triggers"]),
            json.dumps(patient["preferences"]),
            patient["background"],
            json.dumps(patient["medications"]),
            json.dumps(patient["conditions"]),
            json.dumps(patient["allergies"]),
            patient["fall_risk"],
            json.dumps(patient["mobility_aids"]),
            patient["diet_texture"],
            json.dumps(patient["sensory_aids"]),
            patient.get("care_notes", ""),
        ))
        print(f"  Upserted: {patient['name']}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"\nDone. {len(PATIENTS)} patient(s) seeded successfully.")


if __name__ == "__main__":
    main()
