import logging
import json
from datetime import datetime, timezone
from typing import Optional
from mcp.server.fastmcp import FastMCP
from app.database import db_client
from app.config import settings

logger = logging.getLogger("dementiacare-mcp")

mcp = FastMCP("dementia_care_mcp")

@mcp.tool()
def get_patient_profile(name: Optional[str] = None) -> str:
    """Retrieves the active patient's background, dementia staging, triggers, preferences, and daily constraints from the database.

    Args:
        name: Optional name of the patient.

    Returns:
        A formatted JSON string of the patient's profile context.
    """
    try:
        if name:
            row = db_client.fetchone("SELECT name, dementia_type, triggers, preferences, background FROM patients WHERE name = ?", (name,))
        else:
            row = db_client.fetchone("SELECT name, dementia_type, triggers, preferences, background FROM patients ORDER BY id ASC LIMIT 1")
        if row:
            profile = {
                "name": row["name"],
                "dementia_type": row["dementia_type"],
                "triggers": json.loads(row["triggers"]) if row["triggers"] else [],
                "preferences": json.loads(row["preferences"]) if row["preferences"] else [],
                "background": row["background"]
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
        # Persist to DB so clinicians can review alerts after the session ends.
        # In-memory logging alone is insufficient — HIGH/EMERGENCY alerts must survive restarts.
        db_client.execute(
            "INSERT INTO safety_escalations (urgency_level, safety_reason, created_at) VALUES (?, ?, ?)",
            (urgency_level, safety_reason, datetime.now(timezone.utc).isoformat())
        )
        return f"Safety alert persisted to database. {msg}"
    except Exception as e:
        logger.error(f"Failed to persist safety escalation to DB: {e}")
        return f"Safety alert logged (DB write failed). {msg}"

@mcp.tool()
def query_care_guidelines(behavior: str) -> str:
    """Searches the clinical dementia care guidelines vector store for protocols relevant to a specific patient behavior.

    Args:
        behavior: A short description of the observed behavior or situation (e.g. 'medication refusal', 'shower resistance', 'sundowning agitation').

    Returns:
        A JSON string containing the top matching guidelines with titles and clinical text.
    """
    try:
        # Import inline to avoid circular imports at module load time
        from app.rag import query_guidelines
        results = query_guidelines(behavior, n_results=3)
        if not results:
            return json.dumps({"guidelines": [], "note": "No matching guidelines found."})
        formatted = [
            {
                "title": r["metadata"].get("title", "General Protocol"),
                "category": r["metadata"].get("category", ""),
                "text": r["document"]
            }
            for r in results
        ]
        return json.dumps({"guidelines": formatted}, indent=2)
    except Exception as e:
        logger.error(f"Error querying care guidelines via MCP: {e}")
        return json.dumps({"error": str(e)})
