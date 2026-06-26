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
            f"Extract the clinical stage, active triggers, personal preferences, daily routine constraints, "
            f"and health risk factors (like diabetes, pain, sleep issues).\n"
            f"Respond strictly in the required JSON schema."
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
