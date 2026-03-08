"""AI endpoints: anomaly/disease detection (SpeedRay)."""

from fastapi import APIRouter, File, UploadFile, HTTPException, Query

from ...ai_agents.torch_xray_model import run_anomaly_detection
from ...pipeline.runners import _detected_disease_names

router = APIRouter(prefix="/ai", tags=["ai"])


def _add_detected_to_result(result: dict) -> dict:
    """Add detected (primary critical finding with score) to anomaly result."""
    result["detected"] = _detected_disease_names(result)
    return result


@router.get("/anomaly")
def get_anomaly(url: str = Query(..., description="Image URL to run detection on")):
    """Run chest X-ray anomaly and 14-disease detection on image at URL."""
    result = run_anomaly_detection(image_url=url)
    return _add_detected_to_result(result)


@router.post("/anomaly")
async def post_anomaly(file: UploadFile = File(...)):
    """Run chest X-ray anomaly and 14-disease detection on uploaded image."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Expected image file")
    content = await file.read()
    result = run_anomaly_detection(image_url="", image_bytes=content)
    return _add_detected_to_result(result)
