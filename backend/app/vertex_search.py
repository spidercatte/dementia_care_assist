import logging
import httpx
import google.auth
import google.auth.transport.requests
from app.config import settings

logger = logging.getLogger("dementiacare-vertex-search")

MCP_ENDPOINT = "https://discoveryengine.googleapis.com/mcp"


def _get_access_token() -> str:
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token


def _serving_config() -> str:
    return (
        f"projects/{settings.vertex_search_project_id}"
        f"/locations/{settings.vertex_search_location}"
        f"/collections/default_collection"
        f"/dataStores/{settings.vertex_search_datastore_id}"
        f"/servingConfigs/default_config"
    )


def _patient_serving_config() -> str:
    return (
        f"projects/{settings.vertex_search_project_id}"
        f"/locations/{settings.vertex_search_location}"
        f"/collections/default_collection"
        f"/dataStores/{settings.vertex_patient_datastore_id}"
        f"/servingConfigs/default_config"
    )


def query_vertex_search(query: str, n_results: int = 4) -> list[dict]:
    """Call the discoveryengine MCP search tool for guidelines and return results in the same
    shape as query_guidelines() so callers are backend-agnostic."""
    if not settings.vertex_search_project_id or not settings.vertex_search_datastore_id:
        logger.warning("Vertex AI Search not configured — skipping.")
        return []

    try:
        results = _mcp_search(_serving_config(), query, n_results)
        # Add distance=None to match query_guidelines() shape
        for r in results:
            r.setdefault("distance", None)
        logger.info(f"Vertex AI Search MCP returned {len(results)} results for: {query!r}")
        return results
    except Exception as e:
        logger.error(f"Vertex AI Search MCP call failed: {e}")
        return []


def _mcp_search(serving_config: str, query: str, n_results: int) -> list[dict]:
    """Shared MCP search call; returns raw result list."""
    token = _get_access_token()

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search",
            "arguments": {
                "servingConfig": serving_config,
                "query": query,
                "pageSize": n_results,
            },
        },
    }

    response = httpx.post(
        MCP_ENDPOINT,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    content = data.get("result", {}).get("content", [])
    results = []
    for item in content:
        if item.get("type") == "text":
            import json
            try:
                hit = json.loads(item["text"])
            except (json.JSONDecodeError, KeyError):
                hit = {"document": item.get("text", ""), "metadata": {}}

            results.append({
                "id": hit.get("id", ""),
                "document": hit.get("snippet", hit.get("document", "")),
                "metadata": {
                    "title": hit.get("title", ""),
                    "source_file": hit.get("link", ""),
                },
            })
    return results


def query_patient_search(query: str, n_results: int = 3) -> list[dict]:
    """Search the patient profiles Vertex AI Search datastore via discoveryengine MCP."""
    if not settings.vertex_search_project_id or not settings.vertex_patient_datastore_id:
        logger.warning("Patient Vertex AI Search not configured — skipping.")
        return []

    try:
        results = _mcp_search(_patient_serving_config(), query, n_results)
        logger.info(f"Patient search MCP returned {len(results)} results for: {query!r}")
        return results
    except Exception as e:
        logger.error(f"Patient search MCP call failed: {e}")
        return []
