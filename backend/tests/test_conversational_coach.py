import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from unittest import mock
from fastapi.testclient import TestClient
from google import genai
from app.main import app
from app.config import settings
from app.agents.conversational_coach import ConversationalCoachAgent

client = TestClient(app)

class MockGenerateContentResponse:
    def __init__(self, text):
        self.text = text

def get_mock_llm_response(*args, **kwargs):
    return MockGenerateContentResponse("Empathetic coaching advice response.")

@pytest.fixture
def gemini_client():
    if settings.gemini_api_key and not os.environ.get("FORCE_MOCK_EVAL"):
        try:
            c = genai.Client(api_key=settings.gemini_api_key)
            c.models.list()
            return c
        except Exception:
            pass

    mock_client = mock.MagicMock()
    mock_client.models.generate_content.side_effect = get_mock_llm_response
    return mock_client

def test_conversational_coach_agent_run(gemini_client):
    """
    Verifies that ConversationalCoachAgent runs and returns response text.
    """
    agent = ConversationalCoachAgent(gemini_client)
    history = [{"role": "user", "content": "How can I get Mom to calm down?"}]
    profile = {
        "name": "Maria",
        "dementia_type": "Alzheimer's",
        "triggers": ["direct correction"],
        "preferences": ["tea"],
        "background": "Maria is 78."
    }
    feedback = {
        "observed_behavior": "Medication Refusal",
        "likely_trigger": "Rushing",
        "caregiver_pattern": "Lecturing",
        "risk_level": "LOW",
        "safety_note": "Keep environment calm.",
        "recommended_response": "Use validation therapy.",
        "avoid_saying": "You must take this.",
        "try_saying": "Let's drink some tea."
    }

    response_text = agent.run(
        chat_history=history,
        patient_profile=profile,
        feedback_context=feedback
    )
    assert isinstance(response_text, str)
    assert len(response_text) > 0

@mock.patch("app.main.ConversationalCoachAgent.run")
def test_api_coach_chat(mock_coach_run):
    """
    Verifies that POST /coach/chat calls the agent and returns the response.
    """
    mock_coach_run.return_value = "This is a mock live coach advice."

    feedback_data = {
        "observed_behavior": "Medication Refusal",
        "likely_trigger": "Rushing",
        "caregiver_pattern": "Lecture",
        "risk_level": "LOW",
        "recommended_response": "Validation",
        "try_saying": "Let's drink tea",
        "avoid_saying": "You must take this",
        "safety_note": "Ensure safe environment",
        "behavioral_timeline": [],
        "behavior_analysis": {
            "patient_emotion": "agitated",
            "patient_triggers": [],
            "caregiver_communication_style": "lecture",
            "interaction_summary": "Summary"
        },
        "strengths": [],
        "opportunities_for_improvement": [],
        "clinical_safety_flags": [],
        "coaching_scripts": [],
        "recommendations": [],
        "detected_language": "English"
    }

    payload = {
        "chat_history": [{"role": "user", "content": "She is refusing to take her tea too."}],
        "feedback_context": feedback_data,
        "patient_name": "Maria"
    }

    # Verify endpoint returns status 200 and calls the agent correctly
    response = client.post("/coach/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["response"] == "This is a mock live coach advice."
