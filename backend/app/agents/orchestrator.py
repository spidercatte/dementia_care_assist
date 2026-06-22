import logging
import json
from google import genai
from google.genai import errors

from app.config import settings
from app.schemas import FinalCoachingResponse
from app.mock_responses import get_mock_coaching_response
from app.rag import query_guidelines

# Import specialized agents
from app.agents.interaction_analysis import InteractionAnalysisAgent
from app.agents.patient_context import PatientContextAgent
from app.agents.care_guidance import CareGuidanceAgent
from app.agents.safety_escalation import SafetyEscalationAgent
from app.agents.caregiver_coaching import CaregiverCoachingAgent

logger = logging.getLogger("dementiacare-orchestrator")

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
                # Initialize sub-agents
                self.analyzer = InteractionAnalysisAgent(self.client)
                self.context_expert = PatientContextAgent(self.client)
                self.guidance_expert = CareGuidanceAgent(self.client)
                self.safety_expert = SafetyEscalationAgent(self.client)
                self.coach = CaregiverCoachingAgent(self.client)
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
            # Step 1: Interaction Analysis Agent
            analysis = self.analyzer.run(contents)
            logger.info("Step 1 Complete.")

            # Step 2: Patient Context Agent
            context = self.context_expert.run(patient_profile)
            logger.info("Step 2 Complete.")

            # Step RAG Ingestion: Search local vector DB using the generated RAG query
            logger.info(f"Retrieving care guidelines for query: '{analysis.rag_query}'")
            retrieved_docs = query_guidelines(analysis.rag_query, n_results=2)
            guidelines_text = "\n\n".join([
                f"Guideline: {doc['metadata'].get('title', 'General')}\n{doc['document']}" 
                for doc in retrieved_docs
            ])

            # Step 3: Care Guidance Agent
            guidance = self.guidance_expert.run(
                interaction_summary=analysis.observed_behavior + " - " + analysis.verbal_transcript_summary,
                patient_context=context.context_synthesis,
                guidelines_text=guidelines_text
            )
            logger.info("Step 3 Complete.")

            # Step 4: Safety / Escalation Agent
            safety = self.safety_expert.run(
                interaction_summary=analysis.observed_behavior + " - " + analysis.non_verbal_cues,
                health_risk_factors=context.health_risk_factors,
                clinical_advice=guidance.recommended_response
            )
            logger.info("Step 4 Complete.")

            # Step 5: Caregiver Coaching Agent (Consolidation)
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
        return self.run_pipeline(contents=[description], patient_profile=patient_profile)

    def analyze_file(self, file_path: str, mime_type: str, patient_profile: dict) -> FinalCoachingResponse:
        if self.use_mock:
            # Immediately resolve file uploads using a mock response based on filename
            filename = file_path.split("/")[-1]
            return get_mock_coaching_response(filename)

        logger.info(f"Uploading file {file_path} to Gemini File API...")
        uploaded_file = self.client.files.upload(file=file_path)
        logger.info(f"Uploaded file name: {uploaded_file.name}")
        
        try:
            feedback = self.run_pipeline(
                contents=[uploaded_file], 
                patient_profile=patient_profile
            )
        finally:
            logger.info(f"Cleaning up file {uploaded_file.name} from Gemini File API...")
            try:
                self.client.files.delete(name=uploaded_file.name)
            except Exception as e:
                logger.error(f"Failed to delete file from Gemini API: {e}")
                
        return feedback
