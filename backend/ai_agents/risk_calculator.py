"""Rule-based risk level calculator for X-ray anomalies (top_critical + score thresholds)."""

from typing import Any, Dict, Optional

# Default thresholds (optional overrides supported)
DEFAULT_HIGH_THRESHOLD = 0.62
DEFAULT_MODERATE_MAX = 0.62
DEFAULT_MODERATE_MIN = 0.5


def calculate_risk(
    top_critical: Dict[str, Any],
    high_threshold: float = DEFAULT_HIGH_THRESHOLD,
    moderate_min: float = DEFAULT_MODERATE_MIN,
    moderate_max: float = DEFAULT_MODERATE_MAX,
) -> Dict[str, str]:
    """
    Assign risk level from top_critical anomaly score.

    Thresholds:
    - High risk: score > high_threshold (default 0.62)
    - Moderate risk: moderate_min < score <= moderate_max (default 0.5 < score <= 0.62)
    - Low risk: score <= moderate_min (default <= 0.5)

    Returns JSON: {"risk": "<Low|Moderate|High>", "reasoning": "<Short explanation>"}
    """
    name = top_critical.get("name") or "Finding"
    score = float(top_critical.get("score", 0.0))

    if score > high_threshold:
        risk = "High"
        reasoning = f"Score exceeds {high_threshold} threshold, indicating high probability of {name}."
    elif moderate_min < score <= moderate_max:
        risk = "Moderate"
        reasoning = f"Score between {moderate_min} and {moderate_max}, indicating moderate probability of {name}."
    else:
        risk = "Low"
        reasoning = f"Score at or below {moderate_min}, indicating low probability of {name}."

    return {"risk": risk, "reasoning": reasoning}


def get_risk_level(
    score: float,
    high_threshold: float = DEFAULT_HIGH_THRESHOLD,
    moderate_min: float = DEFAULT_MODERATE_MIN,
    moderate_max: float = DEFAULT_MODERATE_MAX,
) -> str:
    """Return risk level string only: 'High' | 'Moderate' | 'Low'."""
    if score > high_threshold:
        return "High"
    if moderate_min < score <= moderate_max:
        return "Moderate"
    return "Low"
