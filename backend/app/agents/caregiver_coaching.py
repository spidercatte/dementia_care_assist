import logging
from google.genai import types
from app.agents.utils import clean_json_text
from app.schemas import (
    FinalCoachingResponse,
    InteractionAnalysisResponse,
    PatientContextResponse,
    CareGuidanceResponse,
    SafetyEscalationResponse,
    BehaviorRecognition,
    Recommendation
)

logger = logging.getLogger("dementiacare-coaching-synthesizer")

class CoachingSynthesizer:
    def __init__(self, client):
        self.client = client

    def run(
        self,
        analysis: InteractionAnalysisResponse,
        context: PatientContextResponse,
        guidance: CareGuidanceResponse,
        safety: SafetyEscalationResponse
    ) -> FinalCoachingResponse:
        logger.info("Step 5 running: Caregiver Coaching Synthesis...")
        timeline_text = "\n".join([
            f"- {obs.timeframe} | Behavior: {obs.observable_behavior} | Symptom: {obs.clinical_symptom} | State: {obs.cognitive_state}"
            for obs in analysis.behavioral_timeline
        ])
        prompt = (
            f"You are a supportive, empathetic Caregiver Coach.\n"
            f"Translate the following clinical findings and safety evaluations into a warm, helpful report:\n\n"
            f"--- INTERACTION ANALYSIS ---\n"
            f"Behavior: {analysis.observed_behavior}\n"
            f"Trigger: {analysis.likely_trigger}\n"
            f"Caregiver Style: {analysis.caregiver_pattern}\n"
            f"Agitation: {analysis.agitation_level}/10 | Confusion: {analysis.confusion_level}/10\n"
            f"Verbal Summary: {analysis.verbal_transcript_summary}\n"
            f"Non-verbal Cues: {analysis.non_verbal_cues}\n"
            f"Detected Language: {analysis.detected_language}\n"
            f"Clinical Timeline:\n{timeline_text}\n\n"
            f"--- CLINICAL GUIDANCE ---\n"
            f"Advice: {guidance.recommended_response}\n"
            f"Do Nots: {', '.join(guidance.do_nots)}\n"
            f"Guidelines Used: {', '.join(guidance.retrieved_guidelines)}\n\n"
            f"--- SAFETY ASSESSMENT ---\n"
            f"Risk Level: {safety.risk_level}\n"
            f"Escalate: {safety.escalate_to_clinician}\n"
            f"Safety Instruction: {safety.safety_note}\n\n"
            f"Instructions:\n"
            f"1. Complete the FinalCoachingResponse schema.\n"
            f"2. Keep the tone warm, kind, and supportive. Caregiving is emotionally taxing.\n"
            f"3. Formulate specific dialog scripts in 'coaching_scripts': e.g., 'Avoid saying: ...' and 'Try saying: ...'.\n"
            f"4. Populate the 'recommendations' list with concrete method cards (e.g. Validation Therapy, Redirection) detailing the description and clinical rationality.\n"
            f"5. Map the outputs to matching fields: behavior_analysis, strengths, opportunities_for_improvement, clinical_safety_flags.\n"
            f"6. Populate the 'behavioral_timeline' field with the timestamped observations provided.\n"
            f"7. Populate the 'detected_language' field with the detected language provided in the input: '{analysis.detected_language}'.\n"
            f"8. Respond strictly in the required JSON schema."
        )

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FinalCoachingResponse
            )
        )
        return FinalCoachingResponse.model_validate_json(clean_json_text(response.text))
