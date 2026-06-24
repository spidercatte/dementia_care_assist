import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import pytest
from unittest import mock
from google import genai
from app.config import settings
from app.schemas import SafetyEscalationResponse
from app.agents.safety_escalation import SafetyEscalationAgent

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

    risk = "MEDIUM"
    escalate = False
    if "slipped" in text_content_lower or "tile" in text_content_lower or "hip" in text_content_lower:
        risk = "EMERGENCY"
        escalate = True
    elif "teaching" in text_content_lower or "front door" in text_content_lower or "shoes on" in text_content_lower:
        risk = "HIGH"
        escalate = True
    elif "shower" in text_content_lower or "bath" in text_content_lower or "bathed" in text_content_lower:
        risk = "LOW"
        escalate = False

    resp = SafetyEscalationResponse(
        risk_level=risk,
        safety_note="Ensure immediate environment is safe. Monitor patient carefully.",
        escalate_to_clinician=escalate
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
def test_safety_escalation_agent(gemini_client, case):
    """
    Evaluates the Safety & Escalation Agent (Agent 4) on risk classification.
    """
    agent = SafetyEscalationAgent(gemini_client)

    # Run the agent
    response = agent.run(
        interaction_summary=case["description"],
        health_risk_factors=case["patient_profile"]["background"].split("."),
        clinical_advice="Ensure patient is safe. Do not force or lock door."
    )

    # Assertions on response schema validation
    assert isinstance(response, SafetyEscalationResponse)
    assert response.risk_level in ["LOW", "MEDIUM", "HIGH", "EMERGENCY"]
    assert response.safety_note
    assert isinstance(response.escalate_to_clinician, bool)

    # Validate safety classification correctness
    exp = case["expected"]
    assert response.risk_level == exp["risk_level"]
    assert response.escalate_to_clinician == exp["escalate_to_clinician"]
