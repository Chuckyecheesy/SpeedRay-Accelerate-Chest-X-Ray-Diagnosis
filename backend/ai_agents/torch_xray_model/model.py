"""Model load and inference for SpeedRay XRayTorchModel."""

from typing import Any, List, Optional

from .config import DEVICE, MODEL_PATH, MODEL_TYPE, NIH_PATHOLOGIES

_model = None
_pathologies: Optional[List[str]] = None


def _load_torchxrayvision():
    """Load TorchXRayVision DenseNet trained on NIH ChestX-ray14."""
    import torch
    import torchxrayvision as xrv

    model = xrv.models.DenseNet(weights="densenet121-res224-nih")
    model = model.to(DEVICE)
    model.eval()
    pathologies = getattr(model, "pathologies", None) or NIH_PATHOLOGIES
    return model, pathologies


def _load_custom():
    """Load custom PyTorch model from path; output must be 14-dim."""
    import torch

    if not MODEL_PATH:
        return None, None
    model = torch.load(MODEL_PATH, map_location=DEVICE)
    if hasattr(model, "eval"):
        model.eval()
    return model, NIH_PATHOLOGIES


def load_model() -> Optional[Any]:
    """Lazy-load PyTorch XRay model (TorchXRayVision or custom)."""
    global _model, _pathologies
    if _model is not None:
        return _model

    if MODEL_TYPE == "torchxrayvision":
        try:
            _model, _pathologies = _load_torchxrayvision()
        except Exception:
            _model, _pathologies = None, None
    else:
        _model, _pathologies = _load_custom()

    return _model


def get_model() -> Optional[Any]:
    return load_model()


def get_pathologies() -> List[str]:
    """Return pathology names in model output order (14 for NIH)."""
    if _pathologies is not None:
        return _pathologies
    load_model()
    return _pathologies or NIH_PATHOLOGIES
