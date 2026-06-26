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
            "Your task is to analyze the input (which could be video, audio, or text) and determine if it is relevant to dementia care.\n"
            "Input is VALID if it shows or describes any of the following:\n"
            "- A patient with dementia interacting with a caregiver, family member, or clinician.\n"
            "- A patient alone who is showing dementia-related symptoms or behaviors (e.g., agitation, confusion, repetitive speech, distress, wandering, emotional outbursts).\n"
            "- A caregiver describing or recounting a dementia care situation.\n"
            "- A text or audio account of a dementia care scenario.\n"
            "Input is INVALID only if it contains:\n"
            "- Silence, noise, music, or blank video/audio with no discernible human presence.\n"
            "- Random objects, pets, or scenery with no human content.\n"
            "- Completely unrelated topics (e.g., weather, news, sports, programming) or gibberish.\n"
            "When in doubt about whether content is dementia-related, lean toward marking it as valid.\n"
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
