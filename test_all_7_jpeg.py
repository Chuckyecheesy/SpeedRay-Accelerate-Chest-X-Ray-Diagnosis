#!/usr/bin/env python3
"""Run the X-ray model on project-root chest X-ray images (JPEGs + edema.jpg + hernia.png) and print results."""

import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))

# All images to test (7 JPEGs + edema, hernia)
IMAGES = [
    "atelectasis.jpeg",
    "cardiomegaly.jpeg",
    "effusion.jpeg",
    "mass.jpeg",
    "normalxray.jpeg",
    "pneumonia.jpeg",
    "pneumothorax.jpeg",
    "edema.jpg",
    "hernia.png",
]


def main():
    try:
        import torch
        import torchxrayvision
    except ImportError as e:
        print("Missing dependency:", e)
        print("Install with: pip install -r backend/requirements.txt")
        sys.exit(1)

    from backend.ai_agents.torch_xray_model import run_anomaly_detection

    present = [n for n in IMAGES if (root / n).exists()]
    missing = [n for n in IMAGES if not (root / n).exists()]
    if missing:
        print("Missing images (skipped):", missing)
    if not present:
        print("No images found.")
        sys.exit(1)

    # Load model with first image
    with open(root / present[0], "rb") as f:
        first_bytes = f.read()
    first_result = run_anomaly_detection(image_url="", image_bytes=first_bytes)
    if not first_result.get("model_loaded"):
        print("Model failed to load. Check SPEEDRAY_TORCH_MODEL_TYPE and dependencies.")
        sys.exit(1)

    print("Running X-ray model on", len(present), "images\n")

    def print_result(name: str, result: dict) -> None:
        if "error" in result:
            print(f"  {name}: ERROR {result['error']}")
            return
        top = result.get("top_critical") or {}
        finding = top.get("name", "—")
        score = top.get("score", 0.0)
        print(f"  {name:22} {finding}  {score:.4f}")

    print_result(present[0], first_result)
    for name in present[1:]:
        path = root / name
        with open(path, "rb") as f:
            image_bytes = f.read()
        result = run_anomaly_detection(image_url="", image_bytes=image_bytes)
        print_result(name, result)
    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
