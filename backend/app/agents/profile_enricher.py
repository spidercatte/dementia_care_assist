import logging
import json
from google.genai import types
from app.agents.utils import clean_json_text
from app.schemas import ProfileEnricherResponse

logger = logging.getLogger("dementiacare-profile-enricher")

class ProfileEnricherAgent:
    def __init__(self, client):
        self.client = client

    def run(self, chat_history: list, patient_profile: dict) -> ProfileEnricherResponse:
        logger.info("Profile Enricher running: Extracting triggers and preferences from conversation history...")
        if not chat_history:
            return ProfileEnricherResponse(new_triggers=[], new_preferences=[])

        # Format chat history for the prompt
        formatted_history = ""
        for msg in chat_history:
            role = "Caregiver" if msg.get("role") == "user" else "Coach"
            content = msg.get("content", "")
            formatted_history += f"{role}: {content}\n"

        existing_triggers = ", ".join(patient_profile.get("triggers", []))
        existing_preferences = ", ".join(patient_profile.get("preferences", []))

        prompt = (
            "You are a clinical Dementia Profile Enrichment Agent.\n"
            "Your task is to analyze the conversation between a caregiver and a dementia care coach.\n"
            "Extract any NEW potential behavioral triggers (things that cause agitation, anxiety, or resistance) "
            "and any NEW comfort preferences (habits, items, music, routines, foods they respond well to) "
            "that are mentioned about the patient. Only extract things that are directly stated or clearly implied in the chat.\n\n"
            "Here is the active patient's current profile information:\n"
            f"- Patient Name: {patient_profile.get('name')}\n"
            f"- Staged/Type: {patient_profile.get('dementia_type')}\n"
            f"- Existing Triggers: [{existing_triggers}]\n"
            f"- Existing Preferences: [{existing_preferences}]\n\n"
            "Here is the chat history between the Caregiver and the Coach:\n"
            f"{formatted_history}\n\n"
            "Instructions:\n"
            "1. Extract ONLY new triggers and new preferences that are NOT already listed in the existing ones above.\n"
            "2. Make the extracted triggers/preferences short, clear, and actionable (e.g. 'direct commands', 'cold rooms' as triggers; 'Big Band music', 'warm tea' as preferences).\n"
            "3. Do not include generic advice or coach suggestions unless the caregiver confirmed they work.\n"
            "4. For each extracted new trigger and preference, populate 'new_triggers_details' and 'new_preferences_details' with:\n"
            "   - name: The trigger/preference name.\n"
            "   - status: Always 'suspected' since it is an AI suggestion.\n"
            "   - confidence: A score from 0.0 to 1.0 based on how strongly/explicitly verified it is in the chat conversation.\n"
            "   - source: A short snippet of caregiver evidence proving this (e.g., \"Caregiver: she loves tea\").\n"
            "5. Respond strictly in the required JSON schema."
        )

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ProfileEnricherResponse
                )
            )
            return ProfileEnricherResponse.model_validate_json(clean_json_text(response.text))
        except Exception as e:
            logger.error(f"Error running profile enricher agent: {e}")
            return ProfileEnricherResponse(new_triggers=[], new_preferences=[])
