import logging
import json
from datetime import datetime, timezone
from typing import Optional
from mcp.server.fastmcp import FastMCP
from common.database import db_client
from common.config import settings

logger = logging.getLogger("dementiacare-mcp")

mcp = FastMCP("dementia_care_mcp")

@mcp.tool()
def get_patient_profile(name: Optional[str] = None) -> str:
    """Retrieves a patient's full clinical profile from the database, including dementia staging,
    behavioral triggers, comfort preferences, medications, medical conditions, allergies, fall risk,
    mobility/sensory aids, diet texture, and caregiver care notes.

    Args:
        name: Optional name of the patient. Returns the first patient if omitted.

    Returns:
        A formatted JSON string of the patient's complete profile.
    """
    try:
        if name:
            row = db_client.fetchone("SELECT * FROM patients WHERE name = ?", (name,))
        else:
            row = db_client.fetchone("SELECT * FROM patients ORDER BY id ASC LIMIT 1")
        if row:
            profile = {
                "name": row["name"],
                "dementia_type": row["dementia_type"],
                "background": row["background"],
                "triggers": json.loads(row["triggers"]) if row["triggers"] else [],
                "preferences": json.loads(row["preferences"]) if row["preferences"] else [],
                "medications": json.loads(row["medications"]) if row.get("medications") else [],
                "conditions": json.loads(row["conditions"]) if row.get("conditions") else [],
                "allergies": json.loads(row["allergies"]) if row.get("allergies") else [],
                "fall_risk": row.get("fall_risk", "Low"),
                "mobility_aids": json.loads(row["mobility_aids"]) if row.get("mobility_aids") else [],
                "diet_texture": row.get("diet_texture", "Regular"),
                "sensory_aids": json.loads(row["sensory_aids"]) if row.get("sensory_aids") else [],
                "care_notes": row.get("care_notes", ""),
            }
            return json.dumps(profile, indent=2)
    except Exception as e:
        logger.error(f"Error fetching patient profile via MCP: {e}")
    return json.dumps({"error": "Patient not found"}, indent=2)


@mcp.tool()
def log_safety_escalation(urgency_level: str, safety_reason: str) -> str:
    """Logs a critical safety hazard or clinician escalation alert to the database for clinician review.

    Args:
        urgency_level: One of 'LOW', 'MEDIUM', 'HIGH', or 'EMERGENCY'.
        safety_reason: The reason for the safety flag (e.g. fall hazard, medication refusal danger, delirium indicators).

    Returns:
        A confirmation string stating that the safety alert was captured.
    """
    msg = f"[SAFETY ESCALATION] Urgency: {urgency_level} | Detail: {safety_reason}"
    logger.warning(msg)
    try:
        db_client.execute(
            "INSERT INTO safety_escalations (urgency_level, safety_reason, created_at) VALUES (?, ?, ?)",
            (urgency_level, safety_reason, datetime.now(timezone.utc).isoformat())
        )
        return f"Safety alert persisted to database. {msg}"
    except Exception as e:
        logger.error(f"Failed to persist safety escalation to DB: {e}")
        return f"Safety alert logged (DB write failed). {msg}"


@mcp.tool()
def search_patients(query: str) -> str:
    """Searches patient profiles using semantic search to find patients matching a clinical description.
    Uses Vertex AI Search in production; falls back to scanning the local database in development.

    Args:
        query: A natural language description to search for (e.g., 'patient with Lewy Body dementia',
               'who has high fall risk', 'patient allergic to penicillin', 'Maria').

    Returns:
        A JSON string containing matching patient profile summaries.
    """
    try:
        from common.vertex_search import query_patient_search

        if settings.vertex_search_project_id and settings.vertex_patient_datastore_id:
            results = query_patient_search(query, n_results=3)
            source = "vertex_ai_search"

            if not results:
                logger.warning("Patient search returned no results from Vertex AI Search, falling back to DB scan.")
                source = "db_fallback"
                results = _db_patient_search(query)
        else:
            results = _db_patient_search(query)
            source = "db"

        if not results:
            return json.dumps({"patients": [], "note": "No matching patients found.", "source": source})

        return json.dumps({"patients": results, "source": source}, indent=2)
    except Exception as e:
        logger.error(f"Error searching patients via MCP: {e}")
        return json.dumps({"error": str(e)})


def _db_patient_search(query: str) -> list[dict]:
    try:
        rows = db_client.fetchall(
            "SELECT name, dementia_type, triggers, preferences, background, fall_risk, care_notes FROM patients"
        )
        query_lower = query.lower()
        results = []
        for row in rows:
            searchable = " ".join([
                row.get("name", ""),
                row.get("dementia_type", ""),
                row.get("background", ""),
                row.get("triggers", ""),
                row.get("preferences", ""),
                row.get("care_notes", ""),
            ]).lower()
            if any(word in searchable for word in query_lower.split()):
                results.append({
                    "document": (
                        f"Patient: {row.get('name')} | "
                        f"Type: {row.get('dementia_type')} | "
                        f"Fall Risk: {row.get('fall_risk')} | "
                        f"Background: {row.get('background', '')[:200]} | "
                        f"Care Notes: {row.get('care_notes', '')[:200]}"
                    ),
                    "metadata": {"title": f"Patient Profile: {row.get('name')}"},
                })
        return results
    except Exception as e:
        logger.error(f"DB patient scan failed: {e}")
        return []


@mcp.tool()
def query_care_guidelines(behavior: str) -> str:
    """Searches the clinical dementia care guidelines vector store for protocols relevant to a specific patient behavior.

    Args:
        behavior: A short description of the observed behavior or situation (e.g. 'medication refusal', 'shower resistance', 'sundowning agitation').

    Returns:
        A JSON string containing the top matching guidelines with titles and clinical text.
    """
    try:
        from common.vertex_search import query_vertex_search
        from common.rag import query_guidelines

        if settings.vertex_search_project_id and settings.vertex_search_datastore_id:
            results = query_vertex_search(behavior, n_results=4)
            source = "vertex_ai_search"
            if not results:
                logger.warning("Vertex AI Search returned no results, falling back to ChromaDB.")
                results = query_guidelines(behavior, n_results=3)
                source = "chromadb_fallback"
        else:
            results = query_guidelines(behavior, n_results=3)
            source = "chromadb"

        if not results:
            return json.dumps({"guidelines": [], "note": "No matching guidelines found.", "source": source})

        formatted = [
            {
                "title": r["metadata"].get("title", "General Protocol"),
                "category": r["metadata"].get("category", ""),
                "text": r["document"]
            }
            for r in results
        ]
        return json.dumps({"guidelines": formatted, "source": source}, indent=2)
    except Exception as e:
        logger.error(f"Error querying care guidelines via MCP: {e}")
        return json.dumps({"error": str(e)})


# Standalone entrypoint
from fastapi import FastAPI
mcp_app = mcp.sse_app()
app = FastAPI(title="Dementia Care MCP Server Gateway")
app.mount("/mcp", mcp_app)
