"""Backend constants and namespace for SpeedRay."""

SPEEDRAY_NAMESPACE = "SpeedRay"

PIPELINE_STEP_NAMES = [
    "uploadAndAnnotate",
    "runAnomalyDetection",
    "fetchRAGContext",
    "generateReport",
    "generateAudio",
    "runRiskPrediction",
    "submitLog",
]
