#!/usr/bin/env python3
"""Test the X-ray pipeline on all 9 images (jpg, jpeg, png): upload, anomaly, risk, annotated URL."""

import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))

IMAGES = [
    "atelectasis.jpeg",
    "cardiomegaly.jpeg",
    "edema.jpg",
    "effusion.jpeg",
    "hernia.png",
    "mass.jpeg",
    "normalxray.jpeg",
    "pneumonia.jpeg",
    "pneumothorax.jpeg",
]


def main():
    present = [n for n in IMAGES if (root / n).exists()]
    missing = [n for n in IMAGES if not (root / n).exists()]
    if missing:
        print("Missing (skipped):", missing, file=sys.stderr)
    if not present:
        print("No images found.", file=sys.stderr)
        return 1

    # Load backend (env from .env)
    try:
        from backend.ai_agents.risk_calculator import get_risk_level
        from backend.ai_agents.torch_xray_model import run_anomaly_detection
        from backend.storage import upload_image, build_annotated_image_url_with_text
    except ImportError as e:
        print("Import error:", e, file=sys.stderr)
        return 1

    results = []
    for filename in present:
        path = root / filename
        with open(path, "rb") as f:
            image_bytes = f.read()
        # Upload to Cloudinary
        upload_result = upload_image(image_bytes, folder="speedray")
        public_id = upload_result.get("public_id") or f"speedray/{path.stem}"
        url = upload_result.get("secure_url") or upload_result.get("url") or ""
        width = upload_result.get("width") or 512
        height = upload_result.get("height") or 512
        # Anomaly detection
        anomaly = run_anomaly_detection(url, image_bytes=image_bytes)
        top = anomaly.get("top_critical") or {}
        name = top.get("name") or "Normal"
        score = float(top.get("score", 0.0))
        risk = get_risk_level(score)
        top_critical = {"name": name, "score": score, "risk": risk}
        # Annotated URL: coloured centre region (by risk) + text overlay
        annotated_url = build_annotated_image_url_with_text(
            public_id,
            regions=[],
            top_critical=top_critical,
            image_width=width,
            image_height=height,
        )
        results.append({
            "filename": filename,
            "top_critical": top_critical,
            "annotated_url": annotated_url,
        })

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
