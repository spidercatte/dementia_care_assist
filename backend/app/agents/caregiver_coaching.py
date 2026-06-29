import json
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

        trigger_details_str = ""
        if context.trigger_details:
            trigger_details_str = "\n".join([
                f"- Trigger: {t.name} (Status: {t.status}, Confidence: {t.confidence}, Source: {t.source})"
                for t in context.trigger_details
            ])

        bias_warning_str = f"Bias / Uncertainty Warning: {context.bias_warning_note}" if context.bias_warning_note else "None"

        prompt = (
            f"You are a supportive, empathetic Caregiver Coach. You act as an educational coaching aid, not a clinical replacement. "
            f"Do not diagnose, prescribe, or provide medical/clinical treatment advice. Focus on communication coaching and safety/redirection guidelines.\n"
            f"Translate the following findings, guidelines, and safety evaluations into a warm, helpful report:\n\n"
            f"--- INTERACTION ANALYSIS ---\n"
            f"Behavior: {analysis.observed_behavior}\n"
            f"Trigger: {analysis.likely_trigger}\n"
            f"Caregiver Style: {analysis.caregiver_pattern}\n"
            f"Agitation: {analysis.agitation_level}/10 | Confusion: {analysis.confusion_level}/10\n"
            f"Verbal Summary: {analysis.verbal_transcript_summary}\n"
            f"Non-verbal Cues: {analysis.non_verbal_cues}\n"
            f"Detected Language: {analysis.detected_language}\n"
            f"Clinical Timeline:\n{timeline_text}\n\n"
            f"--- PATIENT BASELINE CONTEXT (TIERED CONFIDENCE) ---\n"
            f"Stage: {context.clinical_stage}\n"
            f"{trigger_details_str}\n"
            f"{bias_warning_str}\n\n"
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
            f"4. If there is a bias warning or if key triggers/preferences are unconfirmed (suspected), mention this gently in the coaching advice or recommendations so the caregiver knows to verify them.\n"
            f"5. Populate the 'recommendations' list with concrete method cards (e.g. Validation Therapy, Redirection) detailing the description and clinical rationality.\n"
            f"6. Map the outputs to matching fields: behavior_analysis, strengths, opportunities_for_improvement, clinical_safety_flags.\n"
            f"7. Populate the 'behavioral_timeline' field with the timestamped observations provided.\n"
            f"8. Populate the 'detected_language' field with the detected language provided in the input: '{analysis.detected_language}'.\n"
            f"9. For the `try_saying` field, formulate a warm, validation-first dialogue script starting with validating/empathetic phrases (e.g., 'I understand you are...', 'I see you are...', 'Let's...', 'It's safe...').\n"
            f"10. Respond strictly in the required JSON schema."
        )

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FinalCoachingResponse
            )
        )
        res_obj = FinalCoachingResponse.model_validate_json(clean_json_text(response.text))

        # Programmatically guarantee details propagation to avoid single point of failure bias
        res_obj.bias_warning_note = context.bias_warning_note
        res_obj.trigger_details = context.trigger_details
        res_obj.preference_details = context.preference_details
        return res_obj
