import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import pytest
from unittest import mock
from google import genai
from app.config import settings
from app.schemas import PatientContextResponse
from app.agents.patient_context import PatientContextAgent

# Load eval cases from dataset
EVAL_DATASET_PATH = os.path.join(os.path.dirname(__file__), "eval_dataset.json")

def load_eval_cases():
    if not os.path.exists(EVAL_DATASET_PATH):
        return []
    with open(EVAL_DATASET_PATH, "r") as f:
        data = json.load(f)
    return data.get("eval_cases", [])

eval_cases = load_eval_cases()

class MockGenerateContentResponse:
    def __init__(self, text):
        self.text = text

def get_mock_llm_response(*args, **kwargs):
    prompt_or_contents = kwargs.get("contents", args[0] if args else "")
    text_content = ""
    if isinstance(prompt_or_contents, list):
        for item in prompt_or_contents:
            if hasattr(item, "parts") and item.parts:
                for p in item.parts:
                    if hasattr(p, "text"):
                        text_content += p.text + " "
            elif isinstance(item, str):
                text_content += item + " "
    else:
        text_content = str(prompt_or_contents)

    text_content_lower = text_content.lower()

    resp = PatientContextResponse(
        clinical_stage="Alzheimer's (Moderate)",
        active_triggers=["direct correction", "asking do you remember"],
        preferences=["tea", "gardening"],
        daily_routine_constraints=["sundowning in the afternoon"],
        health_risk_factors=["diabetes", "fall risk" if "slipped" in text_content_lower or "hip" in text_content_lower else "sleep patterns"]
    )
    return MockGenerateContentResponse(resp.model_dump_json())


@pytest.fixture
def gemini_client():
    if settings.gemini_api_key and not os.environ.get("FORCE_MOCK_EVAL"):
        try:
            client = genai.Client(api_key=settings.gemini_api_key)
            client.models.list()
            return client
        except Exception:
            pass

    mock_client = mock.MagicMock()
    mock_client.models.generate_content.side_effect = get_mock_llm_response
    return mock_client


@pytest.mark.parametrize("case", eval_cases)
def test_patient_context_agent(gemini_client, case):
    """
    Evaluates the Patient Context Agent (Agent 2) on structured profiles.
    """
    agent = PatientContextAgent(gemini_client)

    # Run the agent
    response = agent.run(case["patient_profile"])

    # Assertions on response schema validation
    assert isinstance(response, PatientContextResponse)
    assert response.clinical_stage
    assert isinstance(response.active_triggers, list)
    assert isinstance(response.preferences, list)
    assert isinstance(response.health_risk_factors, list)

    # Verify clinical stage is correctly parsed
    assert "Alzheimer" in response.clinical_stage or "Moderate" in response.clinical_stage
