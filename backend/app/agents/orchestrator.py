import logging
import json
from google import genai
from google.genai import errors

from app.config import settings
from app.schemas import FinalCoachingResponse, BehaviorRecognition, Recommendation, ValidationResponse
from app.mock_responses import get_mock_coaching_response
from app.rag import query_guidelines

# Import specialized pipeline services
from app.agents.validation import ValidationService
from app.agents.interaction_analysis import InteractionAnalyzer
from app.agents.patient_context import PatientContextProcessor
from app.agents.care_guidance import CareGuidanceService
from app.agents.safety_escalation import SafetyEvaluator
from app.agents.caregiver_coaching import CoachingSynthesizer

logger = logging.getLogger("dementiacare-orchestrator")

def is_nonsensical_or_too_short(text: str) -> bool:
    if not text:
        return True
    cleaned = text.strip().lower()
    # Filter common short/greeting words
    greetings = {"hi", "hello", "hey", "test", "demo", "help", "please", "okay", "ok", "good morning", "good afternoon", "good evening", "goodbye", "bye", "yo", "sup"}
    if cleaned in greetings:
        return True
    if len(cleaned) < 15:
        return True
    # If the text has no spaces (just a single long word/gibberish)
    if " " not in cleaned and len(cleaned) > 0:
        return True
    return False

def get_invalid_input_response(description: str, rejection_reason: str = None) -> FinalCoachingResponse:
    reason_prefix = f"Rejection Reason: {rejection_reason}\n\n" if rejection_reason else ""
    return FinalCoachingResponse(
        observed_behavior="Input Insufficient / Invalid",
        likely_trigger="N/A - Insufficient description details",
        caregiver_pattern="N/A",
        risk_level="LOW",
        recommended_response=(
            f"{reason_prefix}"
            "Please describe a specific interaction between a caregiver and a patient with dementia. "
            "To get the best clinical analysis and coaching script, try including:\n"
            "1. What the patient said or did (their behavior).\n"
            "2. What might have triggered it (e.g. being rushed, asked to take medication).\n"
            "3. How the caregiver responded."
        ),
        try_saying="Describe a caregiver-patient situation (e.g., 'Mom got angry when asked to take a bath...').",
        avoid_saying="Using greetings, test keywords, or very short inputs.",
        safety_note="Please provide a detailed care log or scenario description to see safety warnings.",
        behavioral_timeline=[],
        behavior_analysis=BehaviorRecognition(
            patient_emotion="N/A",
            patient_triggers=[],
            caregiver_communication_style="N/A",
            interaction_summary=rejection_reason or f"The input '{description}' is too short or doesn't describe a dementia care interaction."
        ),
        strengths=[],
        opportunities_for_improvement=[],
        clinical_safety_flags=[],
        coaching_scripts=[
            "Avoid: Single word greetings or test phrases.",
            "Try: Describing what happened, what was said, and what you did."
        ],
        recommendations=[
            Recommendation(
                strategy_name="Describe the Patient's Action",
                description="Tell us what the patient did or said (e.g., refused medication, paced around, accused someone of stealing).",
                rationality="Knowing the patient's behavior allows us to identify the underlying dementia symptoms and emotional needs."
            ),
            Recommendation(
                strategy_name="Describe the Caregiver's Action",
                description="Tell us what you said or did in response (e.g., explained the schedule, raised voice, agreed with them).",
                rationality="Analyzing caregiver response patterns helps us identify triggers and suggest alternative, validation-based scripts."
            )
        ],
        detected_language="English"
    )

class OrchestratorAgent:
    def __init__(self):
        self.use_mock = False
        self.client = None

        # Check if API key exists
        if not settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY is not configured. Orchestrator running in MOCK mode.")
            self.use_mock = True
        else:
            try:
                self.client = genai.Client(api_key=settings.gemini_api_key)
                # Initialize sub-services
                self.validator = ValidationService(self.client)
                self.analyzer = InteractionAnalyzer(self.client)
                self.context_expert = PatientContextProcessor(self.client)
                self.guidance_expert = CareGuidanceService(self.client)
                self.safety_expert = SafetyEvaluator(self.client)
                self.coach = CoachingSynthesizer(self.client)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}. Falling back to MOCK mode.")
                self.use_mock = True

    def run_pipeline(self, contents: list, patient_profile: dict) -> FinalCoachingResponse:
        """
        Coordinates the execution of the 5 sub-agents in sequence.
        """
        # Fall back to mock if flagged
        if self.use_mock:
            logger.info("Executing pipeline in MOCK mode...")
            description_text = ""
            for item in contents:
                if isinstance(item, str):
                    description_text += item + " "
            return get_mock_coaching_response(description_text or "Default Care Interaction Log")

        try:
            # Step 0: Intake Validation Service
            validation = self.validator.run(contents)
            logger.info(f"Step 0 (Intake Validation) Complete. Valid: {validation.is_valid}")
            if not validation.is_valid:
                description_name = "the uploaded file"
                for item in contents:
                    if isinstance(item, str):
                        description_name = f"'{item}'"
                return get_invalid_input_response(description_name, validation.reason)

            # Step 1: Interaction Analysis (Analyzer)
            # Pass the validation summary alongside original media to prime the analyzer
            analysis_contents = contents + [f"Validation Intake Summary: {validation.summary}"]
            analysis = self.analyzer.run(analysis_contents)
            logger.info("Step 1 Complete.")

            # Step 2: Patient Context Processor
            context = self.context_expert.run(patient_profile)
            logger.info("Step 2 Complete.")

            # Step RAG Ingestion: Search local vector DB using the generated RAG query
            logger.info(f"Retrieving care guidelines for query: '{analysis.rag_query}'")
            retrieved_docs = query_guidelines(analysis.rag_query, n_results=2)
            guidelines_text = "\n\n".join([
                f"Guideline: {doc['metadata'].get('title', 'General')}\n{doc['document']}"
                for doc in retrieved_docs
            ])

            # Step 3: Care Guidance Service
            context_summary = (
                f"Clinical Stage: {context.clinical_stage}\n"
                f"Active Triggers: {', '.join(context.active_triggers)}\n"
                f"Preferences: {', '.join(context.preferences)}\n"
                f"Routine Constraints: {', '.join(context.daily_routine_constraints)}\n"
                f"Health Risk Factors: {', '.join(context.health_risk_factors)}"
            )
            guidance = self.guidance_expert.run(
                interaction_summary=analysis.observed_behavior + " - " + analysis.verbal_transcript_summary,
                patient_context=context_summary,
                guidelines_text=guidelines_text
            )
            logger.info("Step 3 Complete.")

            # Step 4: Safety / Escalation Evaluator
            safety = self.safety_expert.run(
                interaction_summary=analysis.observed_behavior + " - " + analysis.non_verbal_cues,
                health_risk_factors=context.health_risk_factors,
                clinical_advice=guidance.recommended_response
            )
            logger.info("Step 4 Complete.")

            # Step 5: Caregiver Coaching Synthesis (Synthesizer)
            final_response = self.coach.run(
                analysis=analysis,
                context=context,
                guidance=guidance,
                safety=safety
            )
            logger.info("Step 5 Complete. Orchestration finished.")
            return final_response

        except errors.APIError as e:
            logger.error(f"Gemini API Error in orchestrator: {e}. Falling back to mock response.")
            description_text = "".join([x for x in contents if isinstance(x, str)])
            return get_mock_coaching_response(description_text)
        except Exception as e:
            logger.error(f"Unexpected pipeline error: {e}. Falling back to mock response.")
            description_text = "".join([x for x in contents if isinstance(x, str)])
            return get_mock_coaching_response(description_text)

    def analyze_text(self, description: str, patient_profile: dict) -> FinalCoachingResponse:
        if is_nonsensical_or_too_short(description):
            return get_invalid_input_response(description)
        return self.run_pipeline(contents=[description], patient_profile=patient_profile)

    def analyze_file(self, file_path: str, mime_type: str, patient_profile: dict, original_filename: str = None) -> FinalCoachingResponse:
        filename = original_filename or file_path.split("/")[-1]
        if self.use_mock:
            # Immediately resolve file uploads using a mock response based on filename
            return get_mock_coaching_response(filename)

        uploaded_file = None
        try:
            logger.info(f"Uploading file {file_path} to Gemini File API...")
            uploaded_file = self.client.files.upload(file=file_path)
            logger.info(f"Uploaded file name: {uploaded_file.name}")

            # Wait for file to become active
            import time
            max_retries = 30  # Wait up to 60 seconds (30 * 2)
            retry_interval = 2

            for i in range(max_retries):
                file_info = self.client.files.get(name=uploaded_file.name)
                state = file_info.state.name if hasattr(file_info.state, 'name') else str(file_info.state)

                if state == "ACTIVE":
                    logger.info("File state is ACTIVE and ready for processing.")
                    break
                elif state == "FAILED":
                    raise Exception(f"File processing failed on Gemini servers: {getattr(file_info, 'error', 'Unknown error')}")
                elif state == "PROCESSING":
                    logger.info(f"File is PROCESSING (check {i+1}/{max_retries}), waiting...")
                    time.sleep(retry_interval)
                else:
                    logger.warning(f"Unknown file state encountered: {state}")
                    time.sleep(retry_interval)
            else:
                raise Exception("File processing timed out on Gemini File API.")

            feedback = self.run_pipeline(
                contents=[uploaded_file],
                patient_profile=patient_profile
            )
            return feedback

        except Exception as e:
            logger.error(f"File analysis failed: {e}. Falling back to mock response.")
            return get_mock_coaching_response(filename)

        finally:
            if uploaded_file is not None:
                logger.info(f"Cleaning up file {uploaded_file.name} from Gemini File API...")
                try:
                    self.client.files.delete(name=uploaded_file.name)
                except Exception as e:
                    logger.error(f"Failed to delete file from Gemini API: {e}")
