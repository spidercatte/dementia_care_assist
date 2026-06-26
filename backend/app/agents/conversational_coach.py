import logging
from typing import List
from google.genai import types
from app.config import settings
from app.rag import query_guidelines

logger = logging.getLogger("dementiacare-conversational-coach")

class ConversationalCoachAgent:
    def __init__(self, client):
        self.client = client

    def run(
        self,
        chat_history: List[dict],
        patient_profile: dict,
        feedback_context: dict
    ) -> str:
        logger.info("Conversational Coach Agent running...")

        # 1. Dynamically retrieve extra guidelines if user asks new questions
        last_message = ""
        if chat_history:
            last_message = chat_history[-1].get("content", "")

        extra_guidelines_text = ""
        if last_message and len(last_message) > 10:
            # Simple keyword check for RAG querying
            search_terms = []
            keywords = ["shower", "bath", "med", "pill", "wandering", "home", "pacing", "sundowning", "aggression", "angry"]
            for kw in keywords:
                if kw in last_message.lower():
                    search_terms.append(kw)
            if search_terms:
                query_str = " ".join(search_terms)
                logger.info(f"Conversational coach querying guidelines for: '{query_str}'")
                docs = query_guidelines(query_str, n_results=1)
                if docs:
                    extra_guidelines_text = f"\n\n--- ADDITIONAL RETRIEVED CLINICAL GUIDELINES ---\n{docs[0]['document']}"

        # 2. Format patient profile and analysis context
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

        # Build system instruction
        system_instruction = (
            "You are an empathetic, clinical Dementia Care Coach. Your goal is to support and advise the caregiver.\n"
            "You have access to the context of the active patient and the specific interaction feedback report that has just been generated.\n\n"
            "--- ACTIVE PATIENT PROFILE ---\n"
            f"{profile_summary}\n\n"
            "--- INTERACTION ANALYSIS & COACHING PLAN ---\n"
            f"{analysis_summary}"
            f"{extra_guidelines_text}\n\n"
            "Instructions:\n"
            "1. Answer the caregiver's questions in a warm, compassionate, and highly practical tone.\n"
            "2. Ground your advice in the provided Patient Profile and Coaching Plan. Use validation therapy and redirection principles.\n"
            "3. If the caregiver is venting or emotionally exhausted, validate their feelings before giving clinical tips. Caregiving is hard.\n"
            "4. Keep answers relatively concise (1-2 short paragraphs) to make it readable in a chat window.\n"
            "5. If a safety hazard is described in their follow-up, remind them of the safety guidelines gently."
        )

        # Format history for Gemini API
        contents = []
        for msg in chat_history[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            ))

        # Add system prompt and final user turn
        if chat_history:
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=chat_history[-1]["content"])]
            ))

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        return response.text
