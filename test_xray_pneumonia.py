#!/usr/bin/env python3
"""Run the X-ray model on pneumonia.jpeg and print results."""

import sys
from pathlib import Path

# Run as: python test_xray_pneumonia.py   (from project root)
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))

def main():
    # Check deps so we can show a clear error
    try:
        import torch
        import torchxrayvision
    except ImportError as e:
        print("Missing dependency:", e)
        print("Install with: pip install -r backend/requirements.txt")
        print("Or: pip install torch torchvision torchxrayvision Pillow scikit-image")
        sys.exit(1)

    from backend.ai_agents.torch_xray_model import run_anomaly_detection

    image_path = root / "pneumonia.jpeg"
    if not image_path.exists():
        print(f"Image not found: {image_path}")
        sys.exit(1)

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    print("Running X-ray model on pneumonia.jpeg ...")
    result = run_anomaly_detection(image_url="", image_bytes=image_bytes)

    if not result.get("model_loaded"):
        print("Model failed to load. Check SPEEDRAY_TORCH_MODEL_TYPE and dependencies.")
        print(result)
        sys.exit(1)

    if "error" in result:
        print("Inference error:", result["error"])
        sys.exit(1)

    print("\n--- Results ---")
    print(f"Anomaly score (max finding): {result['score']:.4f}")
    print("\nDisease scores (14 pathologies):")
    diseases = [d for d in result.get("diseases", []) if (d.get("name") or "").strip()]
    for d in diseases:
        bar = "█" * int(d["score"] * 20) + "░" * (20 - int(d["score"] * 20))
        print(f"  {d['name']:22} {d['score']:.4f}  {bar}")
    print("\nPneumonia score:", next((d["score"] for d in result["diseases"] if d["name"] == "Pneumonia"), "N/A"))
    return 0

if __name__ == "__main__":
    sys.exit(main())
