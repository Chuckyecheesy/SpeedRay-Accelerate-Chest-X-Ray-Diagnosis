"""Trigger Backboard pipeline run (SpeedRay)."""

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from ...pipeline import run_pipeline_sync
from ...pipeline.backboard_client import check_connection
from ...pipeline.batch_annotate import run_batch_annotate
from ...prompts import get_report_prompt
from ...storage import build_annotated_image_url_with_text
from ...ai_agents.risk_calculator import get_risk_level

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


class TopCriticalInput(BaseModel):
    name: str
    score: float
    risk: Optional[str] = None  # "Low" | "Moderate" | "High"; computed if missing


class RegionInput(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class ImageAnnotateInput(BaseModel):
    filename: str
    top_critical: TopCriticalInput
    regions: List[RegionInput] = []
    public_id: Optional[str] = None
    image_width: Optional[int] = None  # for coloured overlay when regions empty
    image_height: Optional[int] = None


class BatchAnnotateRequest(BaseModel):
    images: List[ImageAnnotateInput]


class TopCriticalReannotate(BaseModel):
    name: str
    score: float = 0.0
    risk: Optional[str] = None


class ReannotateRequest(BaseModel):
    """Request body for re-annotation: same regions (or edited) + top_critical to rebuild annotated image URL."""
    public_id: str
    regions: List[RegionInput] = []
    top_critical: TopCriticalReannotate
    image_width: Optional[int] = None
    image_height: Optional[int] = None


@router.post("/reannotate")
def reannotate(req: ReannotateRequest) -> Dict[str, Any]:
    """
    Rebuild the annotated X-ray image URL with the given regions and top_critical.
    Does not re-run the pipeline; only calls Cloudinary URL builder.
    Returns { "annotated_url": "..." } so the frontend can update the displayed image.
    """
    regions_dict = [r.model_dump() for r in req.regions]
    top = req.top_critical
    risk = (top.risk or get_risk_level(float(top.score))).strip()
    top_critical = {"name": top.name, "score": top.score, "risk": risk}
    annotated_url = build_annotated_image_url_with_text(
        req.public_id,
        regions=regions_dict,
        top_critical=top_critical,
        image_width=req.image_width,
        image_height=req.image_height,
    )
    return {"annotated_url": annotated_url}


@router.get("/warmup")
def warmup():
    """
    Preload the X-ray model into memory (stateful/persistent).
    Call after deploy or on a schedule so pipeline results return in seconds.
    Returns {"ok": true, "model_loaded": true} when ready.
    """
    try:
        from ...ai_agents.torch_xray_model.model import get_model
        model = get_model()
        return {"ok": True, "model_loaded": model is not None}
    except Exception as e:
        return {"ok": False, "model_loaded": False, "error": str(e)}


@router.get("/backboard-test")
def backboard_test():
    """
    Test Backboard.io API key and connectivity (GET /assistants).
    Returns {"ok": true, "assistants_count": N} or {"ok": false, "error": "..."}.
    """
    return check_connection()


@router.post("/run")
async def run_diagnosis_pipeline(
    file: UploadFile = File(...),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Expected image file")
    content = await file.read()
    run_id = f"run_{hash(content) % 10**10}"
    study_id = f"study_{run_id}"
    prompt = get_report_prompt()
    state = run_pipeline_sync(run_id, study_id, content, prompt)
    return state


@router.post("/annotate-batch")
def annotate_batch(req: BatchAnnotateRequest) -> List[Dict[str, Any]]:
    """
    Run X-ray AI pipeline annotations on multiple images.
    For each image: Cloudinary annotation (regions color-coded by risk, text overlay),
    risk assigned from score if missing (High >0.62, Moderate 0.5–0.62, Low ≤0.5).
    Returns JSON array: [{ filename, top_critical: { name, score, risk }, annotated_url }].
    """
    payload = [img.model_dump() for img in req.images]
    return run_batch_annotate(payload)
