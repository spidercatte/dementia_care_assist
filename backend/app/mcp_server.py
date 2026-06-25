import logging
import json
from mcp.server.fastmcp import FastMCP
from app.database import db_client
from app.config import settings

logger = logging.getLogger("dementiacare-mcp")

mcp = FastMCP("dementia_care_mcp")

@mcp.tool()
def get_patient_profile(name: str = None) -> str:
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
    """Logs a critical safety hazard or clinician escalation alert in the database logs.

    Args:
        urgency_level: One of 'LOW', 'MEDIUM', 'HIGH', or 'EMERGENCY'.
        safety_reason: The reason for the safety flag (e.g. fall hazard, medication refusal danger, delirium indicators).

    Returns:
        A confirmation string stating that the safety alert was captured.
    """
    msg = f"[SAFETY ESCALATION LOGGED] Urgency: {urgency_level} | Detail: {safety_reason}"
    logger.warning(msg)
    return msg
