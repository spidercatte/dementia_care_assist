import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from unittest import mock
from google import genai
from app.config import settings
from app.agents.simulator import SimulatorAgent, SimulatorResponse

class MockGenerateContentResponse:
    def __init__(self, text):
        self.text = text

def get_mock_llm_response(*args, **kwargs):
    prompt_or_contents = kwargs.get("contents", args[0] if args else "")
    text_content = str(prompt_or_contents).lower()

    agitation = 6
    dialogue = "Leave me alone."
    tip = "Maria is confused."

    if any(x in text_content for x in ["must", "have to", "wrong", "doctor"]):
        agitation = 8
        dialogue = "I don't care what the doctor said! You're lying to me."
        tip = "Trap detected: Attempted to use logic/authority which triggers paranoia."
    elif any(x in text_content for x in ["sorry", "tea", "cookie", "gardening", "music"]):
        agitation = 4
        dialogue = "Well... I do like chamomile tea."
        tip = "Success: You validated her distraction or offered a preferred comfort."

    resp = SimulatorResponse(
        patient_dialogue=dialogue,
        patient_agitation_level=agitation,
        coaching_tip=tip
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


def test_simulator_agent_mock_fallback():
    """
    Verifies that the simulator agent runs successfully in mock mode.
    """
    agent = SimulatorAgent()
    agent.use_mock = True

    # Test case 1: confrontational input in medication refusal scenario
    history = [{"role": "user", "content": "You must take your pills because the doctor ordered them."}]
    res = agent.run(
        scenario="Medication Refusal",
        chat_history=history,
        patient_profile={"name": "Maria"}
    )
    assert isinstance(res, SimulatorResponse)
    assert res.patient_agitation_level > 5
    assert "Trap" in res.coaching_tip or "logic" in res.coaching_tip.lower()

    # Test case 2: validating/supportive input
    history = [{"role": "user", "content": "I see you are worried. Let's make some tea."}]
    res = agent.run(
        scenario="Medication Refusal",
        chat_history=history,
        patient_profile={"name": "Maria"}
    )
    assert isinstance(res, SimulatorResponse)
    assert res.patient_agitation_level < 6
    assert "Success" in res.coaching_tip or "validated" in res.coaching_tip.lower()


def test_simulator_agent_llm_flow(gemini_client):
    """
    Verifies that the simulator agent executes the LLM pipeline successfully when client is active.
    """
    agent = SimulatorAgent()
    agent.use_mock = False
    agent.client = gemini_client

    # Mocking standard inputs
    history = [{"role": "user", "content": "You must take your medicine, it's wrong not to."}]
    patient_profile = {
        "name": "Maria",
        "dementia_type": "Alzheimer's",
        "triggers": ["direct correction"],
        "preferences": ["tea"]
    }

    res = agent.run(
        scenario="Medication Refusal",
        chat_history=history,
        patient_profile=patient_profile
    )
    assert isinstance(res, SimulatorResponse)
    assert res.patient_dialogue
    assert 1 <= res.patient_agitation_level <= 10
    assert res.coaching_tip
