"""Fetch Gemini report (SpeedRay)."""

from fastapi import APIRouter
from pydantic import BaseModel
from ...ai_agents.gemini_api import generate_diagnostic_report
from ...ai_agents.diagnostic_summary import get_diagnostic_summary

router = APIRouter(prefix="/report", tags=["report"])


class GenerateReportRequest(BaseModel):
    run_id: str = ""
    rag_context: str = ""
    anomaly_summary: str = ""
    suspected_diseases: list = []


class DiagnosticSummaryRequest(BaseModel):
    filename: str = ""
    top_critical: dict  # {"name": "<disease>", "score": <float>, "risk": "<Low|Moderate|High>"}


@router.post("/generate")
def generate_report(req: GenerateReportRequest):
    return generate_diagnostic_report(
        prompt="Generate a structured chest X-ray diagnostic report.",
        rag_context=req.rag_context,
        anomaly_summary=req.anomaly_summary,
        suspected_diseases=req.suspected_diseases or None,
    )


@router.post("/diagnostic-summary")
def diagnostic_summary(req: DiagnosticSummaryRequest):
    """Deterministic short diagnostic report for top finding. Returns JSON: top_finding, risk, explanation, recommended_next_steps."""
    return get_diagnostic_summary(filename=req.filename, top_critical=req.top_critical)


@router.get("/{run_id}")
def get_report(run_id: str):
    # In production, load from DB/cache by run_id
    return {"run_id": run_id, "summary": "", "findings": [], "impression": ""}
