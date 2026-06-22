# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo
import os
import json
import google.auth

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# Configure Google Cloud environment settings
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# ====================================================
# ADK Agent Tools
# ====================================================

def get_patient_profile() -> str:
    """Retrieves the active patient's background, dementia staging, triggers, preferences, and daily constraints.
    
    Returns:
        A formatted JSON string of the patient's profile context.
    """
    # Mocking the JSON database lookup for the ADK agent context
    profile = {
        "name": "Arthur",
        "dementia_type": "Alzheimer's (Moderate Stage)",
        "triggers": ["direct correction", "being rushed", "loud noises", "asking 'do you remember?'"],
        "preferences": ["listening to 1950s big band music", "drinking chamomile tea", "talking about his past work as a carpenter"],
        "background": "Arthur is 78 years old. He lives at home with his daughter who is his primary caregiver. He often gets confused in the late afternoon (sundowning) and can refuse medication or personal care because he believes he has to go to work or that his daughter is trying to poison him."
    }
    return json.dumps(profile, indent=2)


def lookup_dementia_guidelines(query: str) -> str:
    """Search the clinical guidelines database for dementia care protocols and validation therapy techniques.
    
    Args:
        query: 2-3 keywords describing the behavioral symptom (e.g. 'medication refusal', 'shower resistance', 'sundowning').
        
    Returns:
        A string containing relevant care guidelines and evidence-based protocols.
    """
    q = query.lower()
    # Mocking Vector RAG search matching inside the ADK agent context
    if any(k in q for k in ["med", "pill", "tablet"]):
        return (
            "Guideline: Handling Medication Refusal\n"
            "When a dementia patient refuses medication, never argue, force, or lecture them. "
            "Instead, validate their feelings by saying: 'I understand you're tired of taking these pills, they do look big.' "
            "Redirect their attention to a pleasant topic or routine. Pair medication with a treat or favorite food: "
            "'Let's have a cookie first, then we can take this to help you feel strong.' "
            "Avoid logical explanations or saying 'the doctor ordered it', as logic often escalates agitation in dementia."
        )
    elif any(k in q for k in ["shower", "bath", "wash", "dirty", "clean"]):
        return (
            "Guideline: Managing Agitation and Resistance during Personal Care\n"
            "Resistance to bathing or dressing is often caused by feeling cold, exposed, or confused. "
            "Keep the environment warm, drape a towel over their shoulders for privacy, and explain each step in simple, positive words. "
            "Use Teepa Snow's Positive Physical Approach: approach from the front, call their name, slide hand into a hand-shake grip, "
            "stand at their side (not directly in front, which is confrontational), and speak in a low, gentle voice."
        )
    elif any(k in q for k in ["home", "mother", "suitcase", "leave"]):
        return (
            "Guideline: Responding to Repetitive Questions and Wanting to Go Home\n"
            "When a patient repeatedly asks to 'go home' or asks for a deceased relative, do not correct them or tell them their parents are dead. "
            "This causes fresh grief and distress. Instead, use Validation Therapy to address the emotional need behind the words. "
            "Say: 'You are thinking about home/your mom. Tell me about your childhood home.' "
            "Once they are engaged in sharing memories, transition/redirect their attention to a comforting current activity: "
            "'That sounds beautiful. Let's have a cup of warm tea while we fold these towels.'"
        )
    return (
        "Guideline: Validation Therapy over Reality Orientation\n"
        "Reality orientation (correcting mistakes like 'No, you don't work here anymore') "
        "almost always fails and triggers anger, fear, or shame. Validation Therapy focuses on validating the emotional truth of their statement. "
        "Acknowledge their pride and capability, then redirect them to a helper task in their current environment."
    )


def log_safety_escalation(urgency_level: str, safety_reason: str) -> str:
    """Logs a critical safety hazard or clinician escalation alert.
    
    Args:
        urgency_level: One of 'LOW', 'MEDIUM', 'HIGH', or 'EMERGENCY'.
        safety_reason: The reason for the safety flag (e.g. fall hazard, medication refusal danger, delirium indicators).
        
    Returns:
        A confirmation string stating that the safety alert was captured.
    """
    return f"[SAFETY ESCALATION LOGGED] Urgency: {urgency_level} | Detail: {safety_reason}"


# ====================================================
# ADK Agent Definition
# ====================================================

root_agent = Agent(
    name="dementiacare_coach_agent",
    model=Gemini(
        model="gemini-2.0-flash",
        api_key="AIzaSyD-mock-key-value-12345",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the lead DementiaCare Coach AI Agent. Your role is to provide kind, compassionate, "
        "and evidence-based coaching to dementia caregivers.\n\n"
        "When a caregiver describes an interaction, always follow this protocol:\n"
        "1. Retrieve the patient's context using get_patient_profile() to check their stage and active triggers.\n"
        "2. Query relevant care guidelines using lookup_dementia_guidelines() for the behaviors displayed.\n"
        "3. If there are safety hazards (e.g. falls, medication danger, severe pacing, wandering), log it using log_safety_escalation().\n"
        "4. Synthesize the findings and output caregiver feedback. Provide:\n"
        "   - An emotional behavioral analysis summary.\n"
        "   - Caregiver strengths (what they did well).\n"
        "   - Opportunities to improve (specifically calling out corrections/logical traps they fell into).\n"
        "   - Actionable dialog scripts: 'Avoid saying: ...' and 'Try saying: ...' customized to the scenario.\n"
        "   - Clear clinical guidelines and recommendations.\n\n"
        "Do not offer dry medical summaries; be highly actionable, supportive, and kind."
    ),
    tools=[get_patient_profile, lookup_dementia_guidelines, log_safety_escalation],
)

app = App(
    root_agent=root_agent,
    name="dementiacare-coach-app",
)
