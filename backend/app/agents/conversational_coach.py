import logging
import json
import os
from typing import List
from google.genai import types
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.events.event import Event
from app.config import settings
from app.rag import query_guidelines

logger = logging.getLogger("dementiacare-conversational-coach")


def query_care_guidelines(behavior: str) -> str:
    """Searches the clinical dementia care guidelines vector store for evidence-based protocols
    relevant to a specific patient behavior or caregiver question.

    Call this whenever the caregiver asks about a specific situation, behavior, or technique
    that may have additional clinical guidance (e.g. 'medication refusal', 'sundowning agitation',
    'shower resistance', 'validation therapy', 'wandering at night').

    Args:
        behavior: A short description of the behavior or topic to look up.

    Returns:
        A JSON string with the top matching clinical guidelines.
    """
    try:
        docs = query_guidelines(behavior, n_results=2)
        if not docs:
            return json.dumps({"guidelines": [], "note": "No matching guidelines found."})
        formatted = [
            {
                "title": d["metadata"].get("title", "General Protocol"),
                "text": d["document"]
            }
            for d in docs
        ]
        logger.info(f"Conversational coach RAG retrieved {len(formatted)} guideline(s) for: '{behavior}'")
        return json.dumps({"guidelines": formatted}, indent=2)
    except Exception as e:
        logger.error(f"RAG query failed in conversational coach: {e}")
        return json.dumps({"error": str(e)})


class ConversationalCoachAgent:
    def __init__(self, client=None):
        # client param retained for API compatibility but ADK manages its own Gemini connection
        pass

    def run(
        self,
        chat_history: List[dict],
        patient_profile: dict,
        feedback_context: dict
    ) -> str:
        logger.info("Conversational Coach ADK Agent running...")

        profile_summary = (
            f"Patient Name: {patient_profile.get('name')}\n"
            f"Dementia Staging: {patient_profile.get('dementia_type')}\n"
            f"Known Triggers: {', '.join(patient_profile.get('triggers', []))}\n"
            f"Preferences: {', '.join(patient_profile.get('preferences', []))}\n"
            f"Background: {patient_profile.get('background')}"
        )

        analysis_summary = (
            f"Observed Behavior: {feedback_context.get('observed_behavior')}\n"
            f"Likely Trigger: {feedback_context.get('likely_trigger')}\n"
            f"Caregiver Response Pattern: {feedback_context.get('caregiver_pattern')}\n"
            f"Safety Risk Level: {feedback_context.get('risk_level')}\n"
            f"Safety Instruction: {feedback_context.get('safety_note')}\n"
            f"Recommended Response Strategy: {feedback_context.get('recommended_response')}\n"
            f"Scripts to AVOID: {feedback_context.get('avoid_saying')}\n"
            f"Scripts to TRY: {feedback_context.get('try_saying')}"
        )

        system_instruction = (
            "You are an empathetic, clinical Dementia Care Coach. Your goal is to support and advise the caregiver.\n"
            "You have access to the context of the active patient and the specific interaction feedback report below.\n"
            "You also have a query_care_guidelines tool — use it whenever the caregiver asks about a specific behavior,\n"
            "situation, or technique that may benefit from clinical protocol guidance.\n\n"
            "--- ACTIVE PATIENT PROFILE ---\n"
            f"{profile_summary}\n\n"
            "--- INTERACTION ANALYSIS & COACHING PLAN ---\n"
            f"{analysis_summary}\n\n"
            "Instructions:\n"
            "1. Answer the caregiver's questions in a warm, compassionate, and highly practical tone.\n"
            "2. Ground your advice in the provided Patient Profile and Coaching Plan. Use validation therapy and redirection principles.\n"
            "3. If the caregiver is venting or emotionally exhausted, validate their feelings before giving clinical tips. Caregiving is hard.\n"
            "4. Keep answers relatively concise (1-2 short paragraphs) to make it readable in a chat window.\n"
            "5. If a safety hazard is described in their follow-up, remind them of the safety guidelines gently.\n"
            "6. Use query_care_guidelines when the caregiver's question goes beyond the coaching plan above."
        )

        if settings.gemini_api_key:
            os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

        coach_agent = Agent(
            name="conversational_coach_agent",
            model=Gemini(
                model="gemini-2.5-flash",
                retry_options=types.HttpRetryOptions(attempts=3),
            ),
            instruction=system_instruction,
            # The agent decides when to call RAG based on conversation context,
            # rather than a hardcoded keyword filter.
            tools=[query_care_guidelines]
        )

        session_service = InMemorySessionService()
        session = session_service.create_session_sync(user_id="caregiver", app_name="dementiacare")
        runner = Runner(agent=coach_agent, session_service=session_service, app_name="dementiacare")

        # Replay prior turns into the session before submitting the latest message
        if chat_history and len(chat_history) > 1:
            for msg in chat_history[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                event = Event(
                    message=types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    ),
                    author=role
                )
                session.events.append(event)

        last_msg_text = chat_history[-1]["content"] if chat_history else ""
        new_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=last_msg_text)]
        )

        events = list(
            runner.run(
                new_message=new_message,
                user_id="caregiver",
                session_id=session.id
            )
        )

        response_text = ""
        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        return response_text
