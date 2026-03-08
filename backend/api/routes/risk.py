"""Risk prediction endpoint for SpeedRay frontend."""

from fastapi import APIRouter
from pydantic import BaseModel
from ...ai_agents.presage import get_risk_prediction
from ...ai_agents.risk_calculator import calculate_risk

router = APIRouter(prefix="/risk", tags=["risk"])


class RiskRequest(BaseModel):
    report_summary: str = ""
    findings: list = []
    anomaly_score: float = 0.0


class TopCritical(BaseModel):
    name: str
    score: float


class AnomalyRiskRequest(BaseModel):
    top_critical: TopCritical
    high_threshold: float = 0.62
    moderate_min: float = 0.5
    moderate_max: float = 0.62


@router.post("/predict")
def predict_risk(req: RiskRequest):
    return get_risk_prediction(req.report_summary, req.findings, req.anomaly_score)


@router.post("/from-anomaly")
def risk_from_anomaly(req: AnomalyRiskRequest):
    """
    Assign risk level from top_critical anomaly (score thresholds).
    Returns: {"risk": "Low|Moderate|High", "reasoning": "..."}
    """
    return calculate_risk(
        top_critical=req.top_critical.model_dump(),
        high_threshold=req.high_threshold,
        moderate_min=req.moderate_min,
        moderate_max=req.moderate_max,
    )
