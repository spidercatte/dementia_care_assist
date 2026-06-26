import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import pytest
from unittest import mock
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import FinalCoachingResponse
from app.agents.simulator import SimulatorResponse

client = TestClient(app)

def test_api_health_check():
    """
    Verifies that GET /health check works.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "mode" in data


def test_api_get_and_post_patient_info():
    """
    Verifies that patient profile GET, POST, and list endpoints work.
    """
    # 1. GET all profiles
    list_res = client.get("/patients")
    assert list_res.status_code == 200
    all_patients = list_res.json()
    assert len(all_patients) >= 2
    names = [p["name"] for p in all_patients]
    assert "Maria" in names
    assert "Arthur" in names

    # 2. GET specific profile (Arthur)
    arthur_res = client.get("/patient?name=Arthur")
    assert arthur_res.status_code == 200
    arthur_data = arthur_res.json()
    assert arthur_data["name"] == "Arthur"
    assert "Lewy Body" in arthur_data["dementia_type"]

    # 3. GET current profile (default/Maria)
    get_res = client.get("/patient")
    assert get_res.status_code == 200
    patient_data = get_res.json()
    assert patient_data["name"] == "Maria"

    # 4. POST updated profile (Arthur)
    updated_profile = {
        "name": "Arthur",
        "dementia_type": "Lewy Body Dementia (Moderate Stage) - Updated",
        "triggers": ["hallucinations", "loud noises"],
        "preferences": ["watching classic movies"],
        "background": "Arthur is 82 years old. Has LBD."
    }

    post_res = client.post("/patient", json=updated_profile)
    assert post_res.status_code == 200
    saved_data = post_res.json()
    assert saved_data["dementia_type"] == "Lewy Body Dementia (Moderate Stage) - Updated"
    assert saved_data["triggers"] == ["hallucinations", "loud noises"]

    # Restore original Arthur profile by getting and saving original
    client.post("/patient", json=arthur_data)


@mock.patch("app.main.seed_default_guidelines")
def test_api_seed_guidelines(mock_seed):
    """
    Verifies that POST /guidelines/seed endpoint triggers seed action.
    """
    response = client.post("/guidelines/seed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    mock_seed.assert_called_once()


@mock.patch("app.main.orchestrator.analyze_text")
def test_api_analyze_text(mock_analyze):
    """
    Verifies that POST /analyze/text routes to the orchestrator analysis correctly.
    """
    # Setup mock return response matching FinalCoachingResponse schema
    mock_resp = FinalCoachingResponse(
        observed_behavior="Refusal",
        likely_trigger="Command",
        caregiver_pattern="Lecture",
        risk_level="MEDIUM",
        recommended_response="Validation",
        try_saying="I see you are upset",
        avoid_saying="No",
        safety_note="Ensure safe environment",
        behavioral_timeline=[],
        behavior_analysis={
            "patient_emotion": "agitated",
            "patient_triggers": ["direct correction"],
            "caregiver_communication_style": "argumentative",
            "interaction_summary": "Summary"
        },
        strengths=["Good"],
        opportunities_for_improvement=["Better"],
        clinical_safety_flags=["UTI risk"],
        coaching_scripts=[],
        recommendations=[],
        detected_language="English"
    )
    mock_analyze.return_value = mock_resp

    payload = {"description": "Maria refused her pills."}
    response = client.post("/analyze/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["observed_behavior"] == "Refusal"
    assert data["risk_level"] == "MEDIUM"
    assert data["try_saying"] == "I see you are upset"


@mock.patch("app.main.orchestrator.analyze_file")
def test_api_analyze_file(mock_analyze_file):
    """
    Verifies that POST /analyze/file handles file uploads and routes to file analyzer correctly.
    """
    mock_resp = FinalCoachingResponse(
        observed_behavior="Refusal",
        likely_trigger="Command",
        caregiver_pattern="Lecture",
        risk_level="MEDIUM",
        recommended_response="Validation",
        try_saying="I see you are upset",
        avoid_saying="No",
        safety_note="Ensure safe environment",
        behavioral_timeline=[],
        behavior_analysis={
            "patient_emotion": "agitated",
            "patient_triggers": [],
            "caregiver_communication_style": "lecture",
            "interaction_summary": "Summary"
        },
        strengths=[],
        opportunities_for_improvement=[],
        clinical_safety_flags=[],
        coaching_scripts=[],
        recommendations=[],
        detected_language="English"
    )
    mock_analyze_file.return_value = mock_resp

    file_payload = {"file": ("test_video.mp4", b"dummy video bytes", "video/mp4")}
    response = client.post("/analyze/file", files=file_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["observed_behavior"] == "Refusal"


def test_api_translate_feedback():
    """
    Verifies that POST /translate returns translated schemas.
    """
    coaching_data = {
        "observed_behavior": "Medication Refusal & Theft Paranoia",
        "likely_trigger": "Direct correction",
        "caregiver_pattern": "Lecture",
        "risk_level": "MEDIUM",
        "recommended_response": "Acknowledge the fear of theft/poisoning",
        "try_saying": "I see you want to make sure your money is safe",
        "avoid_saying": "You didn't take your pills!",
        "safety_note": "Cardiac omission warning",
        "behavioral_timeline": [],
        "behavior_analysis": {
            "patient_emotion": "agitated",
            "patient_triggers": [],
            "caregiver_communication_style": "argumentative",
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
        "coaching_response": coaching_data,
        "target_language": "Spanish"
    }

    from app.main import orchestrator
    old_use_mock = orchestrator.use_mock
    orchestrator.use_mock = True
    try:
        response = client.post("/translate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["observed_behavior"] == "Rechazo de medicamentos y paranoia de robo"
    finally:
        orchestrator.use_mock = old_use_mock


@mock.patch("app.main.simulator.run")
def test_api_simulator_step(mock_sim_run):
    """
    Verifies that POST /simulator/step triggers simulator runs and returns correct response.
    """
    mock_resp = SimulatorResponse(
        patient_dialogue="No, I won't do it.",
        patient_agitation_level=7,
        coaching_tip="Try validating her emotions."
    )
    mock_sim_run.return_value = mock_resp

    payload = {
        "scenario": "Medication Refusal",
        "chat_history": [{"role": "user", "content": "Take this pill."}]
    }

    response = client.post("/simulator/step", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["patient_dialogue"] == "No, I won't do it."
    assert data["patient_agitation_level"] == 7
    assert "validating" in data["coaching_tip"]
