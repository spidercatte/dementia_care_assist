import logging
from google.genai import types
from app.schemas import InteractionAnalysisResponse

logger = logging.getLogger("dementiacare-interaction-agent")

class InteractionAnalysisAgent:
    def __init__(self, client):
        self.client = client

    def run(self, contents: list) -> InteractionAnalysisResponse:
        logger.info("Agent 1 running: Interaction Analysis...")
        prompt = (
            "You are a specialized Interaction Analysis Agent in a dementia care clinic.\n"
            "Your task is to analyze the caregiver-patient interaction (which may be a video, audio, or a written text description).\n"
            "Identify the patient's observed behavior, likely trigger, and caregiver response pattern.\n"
            "Determine the patient's agitation level (1-10), confusion level (1-10), verbal summary, and non-verbal cues.\n"
            "Provide a 2-3 word search query to look up clinical care guidelines for this specific behavior.\n"
            "Additionally, extract a chronological behavioral_timeline of observation points mapping specific timeframes "
            "(e.g., '0:00 - 0:03') to the patient's observable behavior/speech, a clinical symptom term, and their underlying emotional or cognitive state.\n"
            "Determine the primary language used in the interaction (both video/audio dialogue and text input). If the interaction language is not English, specify the language name (e.g., 'Spanish', 'Tagalog'). If it is English, specify 'English'.\n"
            "Provide output strictly matching the required schema."
        )

        response = self.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=contents + [prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InteractionAnalysisResponse
            )
        )
        return InteractionAnalysisResponse.model_validate_json(response.text)
