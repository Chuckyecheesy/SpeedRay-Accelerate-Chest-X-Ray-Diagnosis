"""Cloudinary upload, annotation, metadata for SpeedRay backend.

Uses the Python SDK for:
- Uploading X-ray images
- Storing annotations (bounding box + severity) in image context
- Building transformed image URLs that overlay coloured anomaly regions and bboxes by severity.
"""

import base64
import io
import json
import urllib.parse
from typing import Any, Dict, List, Optional

# 1x1 pixel image URLs for solid-color overlays (Cloudinary has no l_solid; we use l_fetch)
# singlecolorimage.com returns a 1x1 PNG; we resize to desired w/h and set opacity.
_FETCH_1X1_RED = "https://singlecolorimage.com/get/ff0000/1x1"
_FETCH_1X1_YELLOW = "https://singlecolorimage.com/get/ffff00/1x1"
_FETCH_1X1_GREEN = "https://singlecolorimage.com/get/00ff00/1x1"
_FETCH_1X1_ORANGE = "https://singlecolorimage.com/get/ffa500/1x1"


def _fetch_layer_base64(url: str) -> str:
    """Base64-encode URL for Cloudinary l_fetch overlay (URL-safe, no padding)."""
    raw = base64.urlsafe_b64encode(url.encode("utf-8")).decode("ascii")
    return raw.rstrip("=")


def _risk_to_fetch_url(risk: str) -> str:
    """1x1 pixel URL for risk-based overlay (High=red, Moderate=yellow, Low=green)."""
    r = (risk or "Low").strip()
    return {
        "High": _FETCH_1X1_RED,
        "Moderate": _FETCH_1X1_YELLOW,
        "Low": _FETCH_1X1_GREEN,
    }.get(r, _FETCH_1X1_GREEN)


def _severity_to_fetch_url(severity: str) -> str:
    """1x1 pixel URL for severity-based overlay (high=red, medium=orange, low=yellow)."""
    s = (severity or "low").lower()
    return {
        "high": _FETCH_1X1_RED,
        "medium": _FETCH_1X1_ORANGE,
        "low": _FETCH_1X1_YELLOW,
    }.get(s, _FETCH_1X1_YELLOW)

from .config import (
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
    CLOUDINARY_CLOUD_NAME,
)

# Severity → overlay colour for anomaly/bbox (color names avoid URL comma issues)
SEVERITY_COLORS = {
    "high": "red",
    "medium": "orange",
    "low": "yellow",
}

# Risk (batch pipeline) → overlay colour: High=red, Moderate=yellow, Low=green
RISK_COLORS = {
    "High": "red",
    "Moderate": "yellow",
    "Low": "green",
}


def _score_to_severity(score: float) -> str:
    """Map model score to severity for annotation colouring."""
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def diseases_to_annotations(
    diseases: List[Dict[str, Any]],
    image_width: int = 512,
    image_height: int = 512,
) -> List[Dict[str, Any]]:
    """Convert disease list (name, score) to annotation list (bbox + severity).

    When the model does not output bounding boxes, creates one annotation per finding
    as a center region (or full image) so the transformed image can colour by severity.
    """
    out: List[Dict[str, Any]] = []
    for i, d in enumerate(diseases or []):
        name = d.get("name") or "Finding"
        score = float(d.get("score", 0))
        if score < 0.2:
            continue
        severity = _score_to_severity(score)
        # Synthetic bbox: center 40% of image so overlays don't cover everything
        margin_w = int(image_width * 0.3)
        margin_h = int(image_height * 0.3)
        w = max(20, image_width - 2 * margin_w)
        h = max(20, image_height - 2 * margin_h)
        x = margin_w
        y = margin_h
        out.append({
            "id": f"ann-{i}",
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "label": name,
            "score": score,
            "severity": severity,
        })
    return out


def _get_cloudinary():
    try:
        import cloudinary
        import cloudinary.uploader
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
        )
        return cloudinary
    except ImportError:
        return None


def _severity_to_color(severity: str) -> str:
    """Map severity level to overlay colour for anomaly/bbox."""
    s = (severity or "low").lower()
    return SEVERITY_COLORS.get(s, SEVERITY_COLORS["low"])


def _risk_to_color(risk: str) -> str:
    """Map risk level to overlay colour (High=red, Moderate=yellow, Low=green)."""
    r = (risk or "Low").strip()
    return RISK_COLORS.get(r, RISK_COLORS["Low"])


def regions_to_annotations(
    regions: List[Dict[str, Any]],
    risk: str,
) -> List[Dict[str, Any]]:
    """Convert regions [{x1, y1, x2, y2}, ...] to annotation list with x, y, width, height, risk."""
    out: List[Dict[str, Any]] = []
    for i, r in enumerate(regions or []):
        x1 = float(r.get("x1", 0))
        y1 = float(r.get("y1", 0))
        x2 = float(r.get("x2", 0))
        y2 = float(r.get("y2", 0))
        x = int(min(x1, x2))
        y = int(min(y1, y2))
        w = max(1, int(abs(x2 - x1)))
        h = max(1, int(abs(y2 - y1)))
        out.append({"x": x, "y": y, "width": w, "height": h, "risk": risk or "Low", "id": f"r{i}"})
    return out


def upload_image(
    file_content: bytes,
    public_id: Optional[str] = None,
    folder: str = "speedray",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Upload X-ray image to Cloudinary. Returns result with url, public_id, etc."""
    cloudinary = _get_cloudinary()
    if not cloudinary:
        return {"url": "", "public_id": public_id or "local", "secure_url": ""}

    opts = {"folder": folder}
    if public_id:
        opts["public_id"] = public_id
    if metadata:
        opts["context"] = "|".join(f"{k}={v}" for k, v in metadata.items())

    result = cloudinary.uploader.upload(
        io.BytesIO(file_content) if isinstance(file_content, bytes) else file_content,
        **opts,
    )
    return {
        "url": result.get("url", ""),
        "secure_url": result.get("secure_url", ""),
        "public_id": result.get("public_id", ""),
        "width": result.get("width"),
        "height": result.get("height"),
    }


def add_annotation(
    public_id: str,
    annotations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Store annotation metadata (bounding box + severity) in Cloudinary context.

    Each annotation is expected to have: x, y, width, height, label (optional), severity (high|medium|low).
    """
    cloudinary = _get_cloudinary()
    if not cloudinary:
        return {"success": False, "public_id": public_id}

    if not annotations:
        return {"success": True, "public_id": public_id}

    try:
        # Store annotations as JSON in custom context (key=value; value must be string)
        payload = json.dumps(annotations)
        # Cloudinary context values are escaped; keep under single-key to avoid parsing issues
        context_pairs = [f"annotations={urllib.parse.quote(payload)}"]
        cloudinary.uploader.explicit(
            public_id,
            type="upload",
            context=context_pairs,
        )
        return {"success": True, "public_id": public_id}
    except Exception:
        return {"success": False, "public_id": public_id}


def build_annotated_image_url(
    public_id: str,
    annotations: List[Dict[str, Any]],
    image_width: Optional[int] = None,
    image_height: Optional[int] = None,
    fill_opacity: float = 0.25,
) -> str:
    """Build a Cloudinary URL that overlays coloured anomaly regions and bounding boxes by severity.

    Each annotation should have: x, y, width, height, severity (high|medium|low), and optional label.
    - Colours anomaly regions with a semi-transparent fill (fill_opacity).
    - Draws a bounding box with severity-based colour (border_opacity).

    Uses Cloudinary transformations only (Python SDK); no server-side image generation.
    """
    cloudinary = _get_cloudinary()
    if not cloudinary:
        base = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/upload"
        return f"{base}/{public_id}" if public_id else ""

    try:
        from cloudinary import CloudinaryImage
    except ImportError:
        base = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/upload"
        return f"{base}/{public_id}" if public_id else ""

    if not annotations:
        return cloudinary.CloudinaryImage(public_id).build_url()

    # Build chained raw transformations: one fetched 1x1 color overlay per annotation (severity)
    # Cloudinary has no l_solid; we use l_fetch with a 1x1 pixel image URL.
    parts = []
    for ann in annotations:
        x = int(ann.get("x", 0))
        y = int(ann.get("y", 0))
        w = max(1, int(ann.get("width", 10)))
        h = max(1, int(ann.get("height", 10)))
        severity = ann.get("severity", "low")
        fetch_url = _severity_to_fetch_url(severity)
        fetch_b64 = _fetch_layer_base64(fetch_url)
        o_val = int(round(fill_opacity * 100))
        part = f"l_fetch:{fetch_b64}/w_{w},h_{h},o_{o_val}/g_north_west,x_{x},y_{y}/fl_layer_apply"
        parts.append(part)

    raw = "/".join(parts)
    return cloudinary.CloudinaryImage(public_id).build_url(
        transformation=[{"raw_transformation": raw}],
        secure=True
    )


def build_annotated_image_url_with_text(
    public_id: str,
    regions: List[Dict[str, Any]],
    top_critical: Dict[str, Any],
    fill_opacity: float = 0.25,
    image_width: Optional[int] = None,
    image_height: Optional[int] = None,
) -> str:
    """
    Build Cloudinary URL with region overlays (color by risk: High=red, Moderate=yellow, Low=green)
    and a text overlay showing disease name and risk.
    regions: [{x1, y1, x2, y2}, ...]; top_critical: {name, score, risk}.
    When regions is empty, pass image_width/image_height to draw a synthetic centre region so the
    anomaly area is still coloured.
    """
    cloudinary = _get_cloudinary()
    if not cloudinary:
        base = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/upload"
        return f"{base}/{public_id}" if public_id else ""

    try:
        from cloudinary import CloudinaryImage
    except ImportError:
        base = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/upload"
        return f"{base}/{public_id}" if public_id else ""

    risk = (top_critical.get("risk") or "Low").strip()
    name = (top_critical.get("name") or "Finding").strip()
    # Use " - " to avoid pipe breaking URL; keep label short for overlay visibility
    text_content = f"{name} - {risk}"
    text_encoded = urllib.parse.quote(text_content, safe="")

    # When no regions given, use a synthetic centre region so the anomaly area is coloured
    regions_to_draw: List[Dict[str, Any]] = list(regions or [])
    if not regions_to_draw and image_width and image_height and image_width > 0 and image_height > 0:
        margin_w = int(image_width * 0.25)
        margin_h = int(image_height * 0.25)
        x1 = margin_w
        y1 = margin_h
        x2 = image_width - margin_w
        y2 = image_height - margin_h
        regions_to_draw = [{"x1": x1, "y1": y1, "x2": max(x2, x1 + 1), "y2": max(y2, y1 + 1)}]

    fetch_url = _risk_to_fetch_url(risk)
    fetch_b64 = _fetch_layer_base64(fetch_url)
    parts = []
    for r in regions_to_draw:
        x1 = float(r.get("x1", 0))
        y1 = float(r.get("y1", 0))
        x2 = float(r.get("x2", 0))
        y2 = float(r.get("y2", 0))
        x = int(min(x1, x2))
        y = int(min(y1, y2))
        w = max(1, int(abs(x2 - x1)))
        h = max(1, int(abs(y2 - y1)))
        o_val = int(round(fill_opacity * 100))
        part = f"l_fetch:{fetch_b64}/w_{w},h_{h},o_{o_val}/g_north_west,x_{x},y_{y}/fl_layer_apply"
        parts.append(part)
    # Text overlay: disease name and risk (top-left). co_white for visibility on dark X-rays.
    text_part = f"l_text:Arial_24:{text_encoded}/co_white,g_north_west,x_10,y_10/fl_layer_apply"
    parts.append(text_part)
    raw = "/".join(parts)
    return CloudinaryImage(public_id).build_url(
        transformation=[{"raw_transformation": raw}],
        secure=True
    )


def get_metadata(public_id: str) -> Dict[str, Any]:
    """Fetch image metadata and context from Cloudinary. Parses stored annotations if present."""
    cloudinary = _get_cloudinary()
    if not cloudinary:
        return {}

    try:
        result = cloudinary.api.resource(public_id)
        context = result.get("context", {}) or {}
        custom = context.get("custom", {}) or {}
        annotations_raw = custom.get("annotations")
        annotations = []
        if annotations_raw:
            try:
                annotations = json.loads(urllib.parse.unquote(annotations_raw))
            except (json.JSONDecodeError, TypeError):
                pass
        return {
            "url": result.get("secure_url"),
            "width": result.get("width"),
            "height": result.get("height"),
            "context": context,
            "annotations": annotations,
        }
    except Exception:
        return {}
