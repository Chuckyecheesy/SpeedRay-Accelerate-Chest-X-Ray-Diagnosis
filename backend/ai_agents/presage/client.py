"""Presage risk API client for SpeedRay."""

from typing import Any, Dict

from .config import PRESAGE_API_KEY, PRESAGE_BASE_URL


def get_risk_prediction(
    report_summary: str,
    findings: list,
    anomaly_score: float,
) -> Dict[str, Any]:
    """Call Presage for risk prediction. Returns level and confidence."""
    if not PRESAGE_BASE_URL:
        return {"level": "unknown", "confidence": 0.0, "factors": []}

    try:
        import requests
        resp = requests.post(
            f"{PRESAGE_BASE_URL.rstrip('/')}/predict",
            json={
                "report_summary": report_summary,
                "findings": findings,
                "anomaly_score": anomaly_score,
            },
            headers={"Authorization": f"Bearer {PRESAGE_API_KEY}"} if PRESAGE_API_KEY else {},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "level": data.get("level", "unknown"),
            "confidence": float(data.get("confidence", 0)),
            "factors": data.get("factors", []),
        }
    except Exception as e:
        return {"level": "error", "confidence": 0.0, "factors": [], "error": str(e)}
