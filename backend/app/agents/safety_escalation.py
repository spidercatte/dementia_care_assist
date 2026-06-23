import logging
from typing import List
from google.genai import types
from app.schemas import SafetyEscalationResponse

logger = logging.getLogger("dementiacare-safety-agent")

class SafetyEscalationAgent:
    def __init__(self, client):
        self.client = client

    def run(
        self,
        interaction_summary: str,
        health_risk_factors: List[str],
        clinical_advice: str
    ) -> SafetyEscalationResponse:
        logger.info("Agent 4 running: Safety & Escalation...")
        prompt = (
            f"You are a Clinical Safety and Risk Escalation Agent.\n"
            f"Examine the interaction details, patient context, and clinical advice to identify safety hazards:\n\n"
            f"--- INTERACTION ANALYSIS ---\n"
            f"Summary: {interaction_summary}\n\n"
            f"--- PATIENT HEALTH RISK FACTORS ---\n"
            f"{', '.join(health_risk_factors)}\n\n"
            f"--- CLINICAL CARE ADVICE ---\n"
            f"Advice: {clinical_advice}\n\n"
            f"Instructions:\n"
            f"1. Check for physical risks: fall risk, medication refusal danger, wandering/elopement risk.\n"
            f"2. Audit if sudden agitation spikes could indicate underlying physical issues (UTI, delirium, hidden pain).\n"
            f"3. Note caregiver burnout indicators (exhaustion, despair, anger).\n"
            f"4. Output a risk level (LOW, MEDIUM, HIGH, EMERGENCY) and specific safety notes.\n"
            f"5. Set escalate_to_clinician to True if clinician or emergency support is required.\n"
            f"6. Respond strictly in the required JSON schema."
        )

        response = self.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SafetyEscalationResponse
            )
        )
        return SafetyEscalationResponse.model_validate_json(response.text)
