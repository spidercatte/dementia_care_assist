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

import asyncio
import os

import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types
from mcp import ClientSession
from mcp.client.sse import sse_client

# Configure Google Cloud environment settings
if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true":
    try:
        _, project_id = google.auth.default()
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    except Exception:
        pass
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
else:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# ====================================================
# ADK Agent Tools & FastMCP Client
#
# Architecture: The ADK agent does NOT contain business logic directly.
# All data access and side effects are delegated to the FastAPI backend
# via MCP (Model Context Protocol) over Server-Sent Events (SSE).
# This keeps the agent stateless and the backend the single source of truth
# for patient data, RAG guidelines, and safety audit logs.
# ====================================================


def call_mcp_tool(name: str, arguments: dict | None = None) -> str:
    """Helper to synchronously execute an MCP tool on the remote backend server over SSE.

    The ADK runtime is async, but tool functions must be synchronous.
    nest_asyncio patches the running event loop to allow asyncio.run() inside it.
    """
    backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
    if arguments is None:
        arguments = {}

    async def _async_call():
        # Establish connection to backend's FastMCP SSE endpoint
        async with sse_client(f"{backend_url}/mcp/sse") as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments=arguments)
                return result.content[0].text

    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()
            return asyncio.run(_async_call())
        else:
            return asyncio.run(_async_call())
    except Exception as e:
        return f"Error executing MCP tool '{name}': {e}"


def get_patient_profile() -> str:
    """Retrieves the active patient's background, dementia staging, triggers, preferences, and daily constraints from the database.

    Returns:
        A formatted JSON string of the patient's profile context.
    """
    return call_mcp_tool("get_patient_profile")


def log_safety_escalation(urgency_level: str, safety_reason: str) -> str:
    """Logs a critical safety hazard or clinician escalation alert, persisted to the database for clinician review.

    Args:
        urgency_level: One of 'LOW', 'MEDIUM', 'HIGH', or 'EMERGENCY'.
        safety_reason: The reason for the safety flag (e.g. fall hazard, medication refusal danger, delirium indicators).

    Returns:
        A confirmation string stating that the safety alert was captured and persisted.
    """
    return call_mcp_tool(
        "log_safety_escalation",
        {"urgency_level": urgency_level, "safety_reason": safety_reason},
    )


def query_care_guidelines(behavior: str) -> str:
    """Searches the clinical dementia care guidelines vector store (RAG) for evidence-based protocols matching the observed patient behavior.

    Args:
        behavior: A short description of the observed behavior or situation
                  (e.g. 'medication refusal', 'shower resistance', 'sundowning agitation', 'wandering').

    Returns:
        A JSON string containing the top matching guidelines with titles and clinical text.
    """
    return call_mcp_tool("query_care_guidelines", {"behavior": behavior})


# ====================================================
# ADK Agent Definition
# ====================================================

root_agent = Agent(
    name="dementiacare_coach_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the lead DementiaCare Coach AI Agent. Your role is to provide kind, compassionate, "
        "and evidence-based coaching to dementia caregivers.\n\n"
        "When a caregiver describes an interaction, always follow this protocol:\n"
        "1. Retrieve the patient's context using get_patient_profile() to check their stage and active triggers.\n"
        "2. Query relevant care guidelines for the behaviors displayed using query_care_guidelines() with a short behavior keyword.\n"
        "3. If there are safety hazards (e.g. falls, medication danger, severe pacing, wandering), log it using log_safety_escalation().\n"
        "4. Synthesize the findings and output caregiver feedback. Provide:\n"
        "   - An emotional behavioral analysis summary.\n"
        "   - Caregiver strengths (what they did well).\n"
        "   - Opportunities to improve (specifically calling out corrections/logical traps they fell into).\n"
        "   - Actionable dialog scripts: 'Avoid saying: ...' and 'Try saying: ...' customized to the scenario.\n"
        "   - Clear clinical guidelines and recommendations.\n\n"
        "Do not offer dry medical summaries; be highly actionable, supportive, and kind."
    ),
    tools=[get_patient_profile, log_safety_escalation, query_care_guidelines],
)

app = App(
    root_agent=root_agent,
    name="app",
)
