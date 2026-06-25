import logging
from google.genai import types
from app.schemas import CareGuidanceResponse

logger = logging.getLogger("dementiacare-guidance-agent")

class CareGuidanceAgent:
    def __init__(self, client):
        self.client = client

    def run(
        self,
        interaction_summary: str,
        patient_context: str,
        guidelines_text: str
    ) -> CareGuidanceResponse:
        logger.info("Agent 3 running: Care Guidance (RAG)...")
        prompt = (
            f"You are a Clinical Care Guidance Agent, expert in occupational therapy, nursing protocols, and dementia care practices.\n"
            f"Based on the following inputs, generate evidence-based care advice:\n\n"
            f"--- INTERACTION SUMMARY ---\n"
            f"Summary: {interaction_summary}\n\n"
            f"--- PATIENT BASELINE ---\n"
            f"{patient_context}\n\n"
            f"--- RAG DEMENTIA GUIDELINES ---\n"
            f"{guidelines_text if guidelines_text else 'Standard dementia communication protocols.'}\n\n"
            f"Instructions:\n"
            f"1. Generate clinical recommendations grounded in the guidelines.\n"
            f"2. Supply a list of retrieved guidelines titles.\n"
            f"3. Detail do-not actions or phrases that exacerbate agitation in this situation.\n"
            f"4. Respond strictly in the required JSON schema."
        )

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CareGuidanceResponse
            )
        )
        return CareGuidanceResponse.model_validate_json(response.text)
