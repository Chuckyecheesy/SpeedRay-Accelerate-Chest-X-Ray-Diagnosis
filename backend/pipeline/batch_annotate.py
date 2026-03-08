"""Batch annotation: run X-ray pipeline annotations on multiple images (Cloudinary + risk)."""

import os
from typing import Any, Dict, List

from ..ai_agents.risk_calculator import get_risk_level
from ..storage import build_annotated_image_url_with_text

CLOUDINARY_FOLDER = "speedray"


def _public_id_from_filename(filename: str) -> str:
    """Derive Cloudinary public_id from filename (e.g. pneumonia.jpeg -> speedray/pneumonia)."""
    base = os.path.splitext(filename or "image")[0]
    return f"{CLOUDINARY_FOLDER}/{base}".replace(" ", "_")


def run_batch_annotate(images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    For each image: assign risk if missing, build Cloudinary annotated URL (regions + text).
    Returns list of { filename, top_critical: { name, score, risk }, annotated_url }.
    """
    result: List[Dict[str, Any]] = []
    for img in images or []:
        filename = img.get("filename") or "image"
        top = img.get("top_critical") or {}
        name = top.get("name") or "Finding"
        score = float(top.get("score", 0.0))
        risk = top.get("risk")
        if risk not in ("Low", "Moderate", "High"):
            risk = get_risk_level(score)
        top_critical = {"name": name, "score": score, "risk": risk}
        regions = img.get("regions") or []
        public_id = img.get("public_id") or _public_id_from_filename(filename)
        image_width = img.get("image_width")
        image_height = img.get("image_height")
        annotated_url = build_annotated_image_url_with_text(
            public_id,
            regions,
            top_critical,
            image_width=image_width,
            image_height=image_height,
        )
        result.append({
            "filename": filename,
            "top_critical": top_critical,
            "annotated_url": annotated_url,
        })
    return result
