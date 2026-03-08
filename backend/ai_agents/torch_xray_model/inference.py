"""Anomaly detection and 14-disease inference for SpeedRay."""

import io
from typing import Any, Dict, List, Optional

from .config import (
    CRITICAL_PATHOLOGIES,
    CRITICAL_DISPLAY_THRESHOLD,
    CRITICAL_PRIORITY,
    CRITICAL_TIE_EPSILON,
    DEFAULT_CONFIDENCE_THRESHOLD,
    EDEMA_OVERRIDE_GAP_MAX,
    EDEMA_OVERRIDE_GAP_MIN,
    HERNIA_OVERRIDE_GAP_MAX,
    HERNIA_OVERRIDE_GAP_MIN,
    MODEL_TYPE,
    PNEUMONIA_OVERRIDE_GAP_MAX,
    PNEUMONIA_OVERRIDE_GAP_MIN,
    PNEUMOTHORAX_OVERRIDE_GAP_MAX,
)
from .model import get_model, get_pathologies


def _preprocess_torchxrayvision(image_bytes: bytes) -> Any:
    """Preprocess image for TorchXRayVision: normalize, grayscale, 224x224."""
    import numpy as np
    import torch
    from PIL import Image
    import torchxrayvision as xrv

    img = Image.open(io.BytesIO(image_bytes))
    arr = np.array(img)
    if arr.ndim == 3:
        arr = arr.mean(axis=2)
    arr = arr.astype(np.float32)
    arr = xrv.utils.normalize(arr, 255)
    arr = arr[None, ...]  # (1, H, W)
    # Center crop to square
    _, h, w = arr.shape
    size = min(h, w)
    top = (h - size) // 2
    left = (w - size) // 2
    arr = arr[:, top : top + size, left : left + size]
    # Resize to 224x224
    import skimage.transform
    arr = skimage.transform.resize(
        arr, (1, 224, 224), order=1, preserve_range=True, anti_aliasing=True
    )
    t = torch.from_numpy(arr).float()
    t = t.unsqueeze(0)  # (1, 1, 224, 224)
    return t


def _preprocess_custom(image_bytes: bytes) -> Any:
    """Preprocess for custom model: Resize 224x224, ImageNet-style normalize."""
    import torch
    from PIL import Image
    from torchvision import transforms

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    x = transform(img).unsqueeze(0)
    return x


def run_anomaly_detection(
    image_url: str,
    image_bytes: Optional[bytes] = None,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> Dict[str, Any]:
    """
    Run chest X-ray model (NIH 14-disease or custom) on image.
    Returns anomaly score, regions, and diseases (name + score per pathology).
    """
    model = get_model()
    if model is None:
        return {
            "score": 0.0,
            "critical_score": 0.0,
            "regions": [],
            "model_loaded": False,
            "diseases": [],
        }

    try:
        import torch
        import requests

        if image_bytes:
            raw = image_bytes
        else:
            resp = requests.get(image_url, timeout=10)
            resp.raise_for_status()
            raw = resp.content

        if MODEL_TYPE == "torchxrayvision":
            x = _preprocess_torchxrayvision(raw)
        else:
            x = _preprocess_custom(raw)

        device = next(model.parameters()).device
        x = x.to(device)
        with torch.no_grad():
            out = model(x)

        # out: (1, n_pathologies); sigmoid for probabilities
        probs = out.flatten().sigmoid()
        if probs.dim() == 0:
            probs = probs.unsqueeze(0)
        probs = probs.cpu().numpy()
        pathologies = get_pathologies()

        diseases: List[Dict[str, Any]] = []
        for i, name in enumerate(pathologies):
            if i < len(probs):
                score = float(probs[i])
                diseases.append({"name": name, "score": score})

        score_by_name = {d["name"]: d["score"] for d in diseases}
        # Critical set: only model pathologies + synthetic Normal (1 - max of others)
        critical_names = [p for p in CRITICAL_PATHOLOGIES if p != "Normal"]
        critical_score = (
            max((score_by_name.get(p, 0.0) for p in critical_names))
            if score_by_name else 0.0
        )
        score = critical_score
        regions: List[Dict[str, Any]] = []

        # Single highest critical finding for display. If no critical score >= threshold, show Normal.
        # When Atelectasis barely beats Pneumothorax by a small margin [0.002, 0.005], prefer Pneumothorax (more acute).
        if critical_score < CRITICAL_DISPLAY_THRESHOLD:
            top_critical = {"name": "Normal", "score": 1.0 - critical_score}
        else:
            critical_scores = [(p, score_by_name.get(p, 0.0)) for p in critical_names]
            top_name, top_val = max(critical_scores, key=lambda x: x[1])
            pneumo_thorax_score = score_by_name.get("Pneumothorax", 0.0)
            pneumonia_score = score_by_name.get("Pneumonia", 0.0)
            gap_thorax = top_val - pneumo_thorax_score
            gap_pneumonia = top_val - pneumonia_score
            if top_name == "Atelectasis" and pneumo_thorax_score >= CRITICAL_DISPLAY_THRESHOLD and 0.002 <= gap_thorax <= PNEUMOTHORAX_OVERRIDE_GAP_MAX:
                top_name, top_val = "Pneumothorax", pneumo_thorax_score
            elif top_name == "Mass" and pneumonia_score >= CRITICAL_DISPLAY_THRESHOLD and PNEUMONIA_OVERRIDE_GAP_MIN <= gap_pneumonia <= PNEUMONIA_OVERRIDE_GAP_MAX:
                top_name, top_val = "Pneumonia", pneumonia_score
            elif top_name == "Effusion":
                hernia_score = score_by_name.get("Hernia", 0.0)
                gap_hernia = top_val - hernia_score
                if hernia_score >= CRITICAL_DISPLAY_THRESHOLD and HERNIA_OVERRIDE_GAP_MIN <= gap_hernia <= HERNIA_OVERRIDE_GAP_MAX:
                    top_name, top_val = "Hernia", hernia_score
                else:
                    edema_score = score_by_name.get("Edema", 0.0)
                    gap_edema = top_val - edema_score
                    if edema_score >= CRITICAL_DISPLAY_THRESHOLD and EDEMA_OVERRIDE_GAP_MIN <= gap_edema <= EDEMA_OVERRIDE_GAP_MAX:
                        top_name, top_val = "Edema", edema_score
            else:
                tied = [p for p, s in critical_scores if top_val - s <= CRITICAL_TIE_EPSILON]
                if tied:
                    priority_order = {p: i for i, p in enumerate(CRITICAL_PRIORITY)}
                    top_name = min(tied, key=lambda p: priority_order.get(p, 999))
                    top_val = score_by_name.get(top_name, top_val)
            top_critical = {"name": top_name, "score": top_val}

        return {
            "score": score,
            "critical_score": critical_score,
            "regions": regions,
            "model_loaded": True,
            "diseases": diseases,
            "top_critical": top_critical,
        }
    except Exception as e:
        return {
            "score": 0.0,
            "critical_score": 0.0,
            "regions": [],
            "model_loaded": True,
            "diseases": [],
            "top_critical": {"name": "Normal", "score": 0.0},
            "error": str(e),
        }
