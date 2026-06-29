import json
import logging
from google.genai import types
from app.agents.utils import clean_json_text
from app.schemas import PatientContextResponse

logger = logging.getLogger("dementiacare-context-processor")

class PatientContextProcessor:
    def __init__(self, client):
        self.client = client

    def run(self, patient_profile: dict) -> PatientContextResponse:
        logger.info("Step 2 running: Patient Context...")
        prompt = (
            f"You are a Clinical Records Processor.\n"
            f"Analyze this raw patient profile and extract a structured care context:\n"
            f"{json.dumps(patient_profile, indent=2)}\n\n"
            f"Instructions:\n"
            f"1. Extract the clinical stage, active triggers, personal preferences, daily routine constraints, "
            f"and health risk factors (like diabetes, pain, sleep issues).\n"
            f"2. Differentiate clearly between confirmed and suspected triggers to prevent single-point-of-failure bias propagation.\n"
            f"3. For each trigger and preference, populate 'trigger_details' and 'preference_details' with:\n"
            f"   - name: The name/label of the trigger or preference.\n"
            f"   - status: Set to 'confirmed' if it is manually verified or confirmed in notes, or 'suspected' if it is an unverified AI extraction.\n"
            f"   - confidence: A score from 0.0 to 1.0 reflecting how strongly established it is (e.g. 1.0 if manually verified, lower if based on unconfirmed logs or single occurrences).\n"
            f"   - source: The origin or context where this was documented (e.g. 'caregiver notes', 'initial assessment', 'AI chat log').\n"
            f"4. If a trigger seems based on a single biased incident, has low confidence, or is unconfirmed, flag it as 'suspected' with lower confidence. Summarize any potential bias, conflicts, or weak initial data check warnings in the 'bias_warning_note' (e.g., warning downstream coaching sessions not to treat it as absolute clinical truth).\n"
            f"5. Respond strictly in the required JSON schema."
        )

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PatientContextResponse
            )
        )
        return PatientContextResponse.model_validate_json(clean_json_text(response.text))
