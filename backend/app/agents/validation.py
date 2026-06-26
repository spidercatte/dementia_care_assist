import logging
from google.genai import types
from app.agents.utils import clean_json_text
from app.schemas import ValidationResponse

logger = logging.getLogger("dementiacare-validation-service")

class ValidationService:
    def __init__(self, client):
        self.client = client

    def run(self, contents: list) -> ValidationResponse:
        logger.info("Validation Service running...")
        prompt = (
            "You are an Intake Validation Service in a dementia care clinic.\n"
            "Your task is to analyze the input (which could be video, audio, or text) and determine if it contains a recognizable caregiver-patient interaction related to dementia care.\n"
            "An interaction is valid if it describes or shows a patient with dementia interacting with a caregiver, family member, or clinician.\n"
            "An interaction is INVALID if it contains:\n"
            "- Silence, noise, music, or blank video/audio.\n"
            "- Random objects, pets, or scenery with no human interaction.\n"
            "- Pure greetings (e.g., 'hello', 'how are you') with no care context.\n"
            "- Unrelated topics (e.g., weather, news, sports, programming) or gibberish.\n"
            "If invalid, set is_valid to False, summary to null, and specify a clear rejection reason explaining what was found.\n"
            "If valid, set is_valid to True, write a very short 1-sentence summary of the interaction, and set reason to null.\n"
            "Provide output strictly matching the required schema."
        )
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents + [prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ValidationResponse
            )
        )
        return ValidationResponse.model_validate_json(clean_json_text(response.text))
