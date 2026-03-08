"""Pipeline DAG definition for SpeedRay (Backboard.io)."""

from ..config import PIPELINE_STEP_NAMES

PIPELINE_ID = "speedray_diagnosis"
STEPS = list(PIPELINE_STEP_NAMES)

DAG = [
    ("uploadAndAnnotate", []),
    ("runAnomalyDetection", ["uploadAndAnnotate"]),
    ("fetchRAGContext", ["uploadAndAnnotate"]),
    ("generateReport", ["runAnomalyDetection", "fetchRAGContext"]),
    ("generateAudio", ["generateReport"]),
    ("runRiskPrediction", ["generateReport"]),
    ("submitLog", ["generateReport", "runRiskPrediction"]),
]
