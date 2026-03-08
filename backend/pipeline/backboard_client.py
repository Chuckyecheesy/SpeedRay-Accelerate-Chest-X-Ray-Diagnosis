"""Backboard.io orchestration client for SpeedRay."""

from typing import Any, Dict

from ..config import get_settings


def _headers() -> Dict[str, str]:
    settings = get_settings()
    api_key = (settings.backboard_api_key or "").strip()
    return {"X-API-Key": api_key} if api_key else {}


def _base_url() -> str:
    return (get_settings().backboard_base_url or "").strip()


def check_connection() -> Dict[str, Any]:
    """
    Verify Backboard API key and connectivity using GET /assistants.
    Returns {"ok": True, "assistants_count": N} or {"ok": False, "error": "..."}.
    """
    base = _base_url()
    if not base:
        return {"ok": False, "error": "not_configured", "detail": "SPEEDRAY_BACKBOARD_BASE_URL not set"}
    try:
        import requests
        resp = requests.get(
            f"{base.rstrip('/')}/assistants",
            headers=_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        count = len(data) if isinstance(data, list) else 0
        return {"ok": True, "assistants_count": count}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def run_pipeline(pipeline_id: str, input_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trigger a pipeline run on Backboard.io (if they support pipeline runs).
    Note: Backboard's public API uses assistants/threads/messages, not /pipelines/{id}/runs.
    Use check_connection() to verify API key; use assistants/threads for conversation flows.
    """
    base_url = _base_url()
    if not base_url:
        return {"run_id": "", "status": "not_configured"}

    try:
        import requests
        resp = requests.post(
            f"{base_url.rstrip('/')}/pipelines/{pipeline_id}/runs",
            json=input_payload,
            headers=_headers(),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return {"run_id": data.get("run_id", ""), "status": data.get("status", "running")}
    except Exception as e:
        return {"run_id": "", "status": "error", "error": str(e)}
