import logging
from typing import List
from google.genai import types
from app.schemas import FinalCoachingResponse
from pydantic import BaseModel, Field

# We import the Client initialization helper
from app.config import settings
from google import genai

logger = logging.getLogger("dementiacare-simulator-agent")

class SimulatorResponse(BaseModel):
    patient_dialogue: str = Field(description="The spoken dialogue of the patient in response to the caregiver")
    patient_agitation_level: int = Field(description="The patient's current agitation/distress level on a scale of 1 (calm) to 10 (highly agitated/combative)")
    coaching_tip: str = Field(description="A gentle coaching tip or feedback on the caregiver's last response (e.g. 'Excellent validation', 'Avoid using logic to explain, redirect instead')")

class SimulatorAgent:
    def __init__(self):
        self.use_mock = not settings.gemini_api_key
        self.client = None
        if not self.use_mock:
            self.client = genai.Client(api_key=settings.gemini_api_key)

    def run(self, scenario: str, chat_history: List[dict], patient_profile: dict) -> SimulatorResponse:
        """
        Simulates a step in an interactive caregiver roleplay session.
        """
        if self.use_mock:
            # Simple mock response logic for testing
            return self._mock_step(scenario, chat_history)

        # Format chat history
        formatted_chat = ""
        for msg in chat_history:
            role = "Caregiver" if msg["role"] == "user" else "Patient (Simulated)"
            formatted_chat += f"{role}: {msg['content']}\n"

        prompt = (
            f"You are a training simulator for dementia caregivers. Your task is to play the role of a dementia patient in a training scenario.\n"
            f"You must react realistically based on the caregiver's responses. "
            f"If the caregiver is confrontational, uses direct correction, or argues, your agitation level should INCREASE. "
            f"If the caregiver uses validation therapy, keeps a calm tone, or redirects, your agitation level should DECREASE.\n\n"
            f"--- PATIENT PROFILE ---\n"
            f"Name: {patient_profile.get('name', 'Maria')}\n"
            f"Dementia Type: {patient_profile.get('dementia_type', 'Alzheimer\'s')}\n"
            f"Key Triggers: {', '.join(patient_profile.get('triggers', ['direct correction', 'arguments']))}\n"
            f"Preferences: {', '.join(patient_profile.get('preferences', ['music', 'tea']))}\n\n"
            f"--- SCENARIO ---\n"
            f"\"{scenario}\"\n\n"
            f"--- CONVERSATION HISTORY ---\n"
            f"{formatted_chat}\n"
            f"Instructions:\n"
            f"1. Generate the next verbal response from the patient.\n"
            f"2. Assess the patient's current agitation level (1 to 10).\n"
            f"3. Provide a constructive feedback coaching tip on the caregiver's last utterance, evaluating if they followed best practices (e.g., validation, redirection) or fell into common traps (e.g., trying to use logic, correcting the patient's timeline).\n"
            f"4. Respond strictly in the required JSON schema."
        )

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SimulatorResponse
                )
            )
            return SimulatorResponse.model_validate_json(response.text)
        except Exception as e:
            logger.warning(f"Failed to generate simulation response via Gemini API: {e}. Falling back to mock step.")
            return self._mock_step(scenario, chat_history)

    def _mock_step(self, scenario: str, chat_history: List[dict]) -> SimulatorResponse:
        """
        Local mock step handler.
        """
        if not chat_history:
            return SimulatorResponse(
                patient_dialogue="What do you want?",
                patient_agitation_level=5,
                coaching_tip="Maria is confused. Try introducing yourself and validating her feelings."
            )

        last_user_message = chat_history[-1]["content"].lower()

        # Simple keywords to determine mock behavior
        if "med" in scenario.lower() or "pill" in scenario.lower():
            if any(x in last_user_message for x in ["must", "have to", "wrong", "doctor"]):
                return SimulatorResponse(
                    patient_dialogue="I don't care what the doctor said! You're lying to me. You want me to sleep so you can search my room. Go away!",
                    patient_agitation_level=8,
                    coaching_tip="Trap detected: Attempted to use logic/authority which triggers paranoia. Try validating Maria's mistrust."
                )
            elif any(x in last_user_message for x in ["sorry", "tea", "cookie", "magazine", "music"]):
                return SimulatorResponse(
                    patient_dialogue="Well... I do like chamomile tea. But make sure you don't touch my papers in the living room. Where are my gardening magazines?",
                    patient_agitation_level=4,
                    coaching_tip="Success: You validated her distraction or offered a preferred comfort (tea/gardening). Agitation decreases."
                )
            else:
                return SimulatorResponse(
                    patient_dialogue="Leave me alone! Why are you standing there holding that bottle? It looks toxic!",
                    patient_agitation_level=6,
                    coaching_tip="Tip: Put the pills away. Focus on validation therapy (agree with her feelings) or redirection."
                )
        elif "shower" in scenario.lower() or "bath" in scenario.lower():
            if any(x in last_user_message for x in ["dirty", "smell", "yesterday", "wash"]):
                return SimulatorResponse(
                    patient_dialogue="I do NOT smell! You are insulting me in my own house. I'm not going in that bathroom, it's freezing!",
                    patient_agitation_level=7,
                    coaching_tip="Trap detected: Correcting her memory ('yesterday') or accusing her of smelling triggers shame. Validate that she feels clean, or check room comfort."
                )
            elif any(x in last_user_message for x in ["warm", "towel", "music", "comfortable"]):
                return SimulatorResponse(
                    patient_dialogue="Warm towels? Well, it is a bit drafty in here. I suppose you can turn the heater on first. But don't rush me.",
                    patient_agitation_level=4,
                    coaching_tip="Success: Addressing environment warmth and dignity helps lower resistance to bathing."
                )
            else:
                return SimulatorResponse(
                    patient_dialogue="I said no! Why are you always bossing me around like a child?",
                    patient_agitation_level=6,
                    coaching_tip="Tip: Try making it about comfort. Use Teepa Snow's positive physical approach: 'Let's get you warmed up first.'"
                )
        else:
            # wants to go home
            if any(x in last_user_message for x in ["dead", "sold", "here", "can't"]):
                return SimulatorResponse(
                    patient_dialogue="No, you're wrong! My mother is waiting! Why are you keeping me locked up here? Help! Someone help me!",
                    patient_agitation_level=9,
                    coaching_tip="Critical Trap: Reality orientation (telling her her mother is dead or house is sold) triggers traumatic grief. Validate her memory instead."
                )
            elif any(x in last_user_message for x in ["tell me", "mother", "farm", "childhood"]):
                return SimulatorResponse(
                    patient_dialogue="My mother... she always made the best apple pies on Sundays. The farm had three horses... one was named Barnaby.",
                    patient_agitation_level=5,
                    coaching_tip="Success: Validation therapy. By asking her to share a memory about her mother/farm, you validated her emotions and can now redirect her."
                )
            else:
                return SimulatorResponse(
                    patient_dialogue="Get out of my way, I need to walk to the bus stop. The bus comes at 5:00!",
                    patient_agitation_level=7,
                    coaching_tip="Tip: Ask about her home or childhood. Try: 'You really want to help your mom. Tell me about the chores you did.'"
                )
