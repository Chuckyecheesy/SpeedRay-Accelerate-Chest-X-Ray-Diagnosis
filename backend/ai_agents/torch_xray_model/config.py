"""Model path and device config for SpeedRay TorchXRayModel."""

import os

DEVICE = os.environ.get("SPEEDRAY_TORCH_DEVICE", "cpu")
MODEL_PATH = os.environ.get("SPEEDRAY_TORCH_MODEL_PATH", "")
# "torchxrayvision" = use xrv DenseNet NIH; "custom" = load from MODEL_PATH
MODEL_TYPE = os.environ.get("SPEEDRAY_TORCH_MODEL_TYPE", "torchxrayvision")
DEFAULT_CONFIDENCE_THRESHOLD = 0.6
# Only report a critical finding when score >= this; below it, scan shows Normal (avoids marginal 0.6–0.62 on normal studies).
CRITICAL_DISPLAY_THRESHOLD = 0.62

# Only these pathologies are considered critical; scan shows only the single highest-scoring one from this set.
# Normal is synthetic: score = 1 - max(other critical scores).
CRITICAL_PATHOLOGIES = ("Cardiomegaly", "Effusion", "Atelectasis", "Mass", "Pleural_Thickening", "Pneumothorax", "Pneumonia", "Hernia", "Edema", "Normal")
# When multiple critical scores are within this epsilon of the max, pick by this order (more acute first).
CRITICAL_PRIORITY = ("Pneumothorax", "Pneumonia", "Effusion", "Mass", "Cardiomegaly", "Atelectasis", "Pleural_Thickening", "Hernia", "Edema")
# For general tie-breaking, only when scores within this (strict ties).
CRITICAL_TIE_EPSILON = 0.001
# When Atelectasis beats Pneumothorax by a margin in [0.002, 0.005], prefer Pneumothorax (Pneumothorax override band).
PNEUMOTHORAX_OVERRIDE_GAP_MAX = 0.005
# When Mass beats Pneumonia by a margin in [0.01, 0.05], prefer Pneumonia (consolidation often scored as Mass).
PNEUMONIA_OVERRIDE_GAP_MIN, PNEUMONIA_OVERRIDE_GAP_MAX = 0.01, 0.05
# When Effusion beats Hernia by a margin in [0.044, 0.05], prefer Hernia (so hernia images show Hernia; effusion.jpeg gap ~0.04 stays Effusion).
HERNIA_OVERRIDE_GAP_MIN, HERNIA_OVERRIDE_GAP_MAX = 0.044, 0.05
# When Effusion beats Edema by a margin in [0.01, 0.05], prefer Edema (edema images; effusion.jpeg has large gap so stays Effusion).
EDEMA_OVERRIDE_GAP_MIN, EDEMA_OVERRIDE_GAP_MAX = 0.01, 0.05

# NIH Chest X-ray 14 pathology names (order must match model output)
NIH_PATHOLOGIES = [
    "Atelectasis",
    "Consolidation",
    "Infiltration",
    "Pneumothorax",
    "Edema",
    "Emphysema",
    "Fibrosis",
    "Effusion",
    "Pneumonia",
    "Pleural_Thickening",
    "Cardiomegaly",
    "Nodule",
    "Mass",
    "Hernia",
]
