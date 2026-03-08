#!/usr/bin/env python3
"""
X-ray model reliability tests: Steps 1–4, sanity vs TorchXRayVision, threshold metrics.

Run from project root:
  PYTHONPATH=/Applications/SpeedRay python3 run_xray_reliability_tests.py [--fixtures-dir PATH] [--threshold 0.5]

Requires: normal/ and positive/ under fixtures dir (see backend/tests/fixtures/xray/README.md).
If positive/ is empty, uses project root pneumonia.jpeg as single positive.
"""

import argparse
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Image extensions to consider (chest X-ray only; no abdomen)
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def _collect_images(dir_path: Path):
    if not dir_path.is_dir():
        return []
    return sorted([p for p in dir_path.iterdir() if p.suffix.lower() in IMAGE_EXTS])


def _run_inference(run_fn, image_path: Path):
    with open(image_path, "rb") as f:
        raw = f.read()
    return run_fn(image_url="", image_bytes=raw)


def _get_scores(result):
    """Return dict pathology -> score for first 14 named diseases."""
    if not result.get("model_loaded") or "error" in result:
        return None
    items = [(d["name"], d["score"]) for d in result.get("diseases", []) if (d.get("name") or "").strip()]
    return dict(items[:14])


def _above_threshold(scores, threshold, labels=None):
    if not scores:
        return False
    if labels is None:
        from backend.ai_agents.torch_xray_model.config import CRITICAL_PATHOLOGIES
        labels = CRITICAL_PATHOLOGIES
    return any(scores.get(l, 0) >= threshold for l in labels)


def main():
    parser = argparse.ArgumentParser(description="X-ray reliability tests")
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=ROOT / "backend" / "tests" / "fixtures" / "xray",
        help="Directory containing normal/ and positive/ subdirs",
    )
    parser.add_argument("--threshold", type=float, default=0.5, help="Decision threshold")
    parser.add_argument("--repeatability-runs", type=int, default=5, help="Runs for Step 3")
    args = parser.parse_args()

    try:
        import torch
        import torchxrayvision
    except ImportError as e:
        print("Missing dependency:", e)
        print("Install with: pip install -r backend/requirements.txt")
        sys.exit(1)

    from backend.ai_agents.torch_xray_model import run_anomaly_detection
    from backend.ai_agents.torch_xray_model.inference import _preprocess_torchxrayvision
    from backend.ai_agents.torch_xray_model.model import get_model

    normal_dir = args.fixtures_dir / "normal"
    positive_dir = args.fixtures_dir / "positive"
    normals = _collect_images(normal_dir)
    positives = _collect_images(positive_dir)
    if not positives and (ROOT / "pneumonia.jpeg").exists():
        positives = [ROOT / "pneumonia.jpeg"]

    if not positives:
        print("No positive images. Add chest X-rays to fixtures/xray/positive/ or place pneumonia.jpeg in project root.")
        sys.exit(1)

    th = args.threshold
    print(f"Fixtures: {len(normals)} normal, {len(positives)} positive | threshold = {th}")
    print()

    # ---- Step 1: Normal X-rays (few/no findings above threshold) ----
    print("--- Step 1: Normal X-rays ---")
    if not normals:
        print("No normal images in", normal_dir, "- skip. Add images for specificity check.")
    else:
        for path in normals:
            result = _run_inference(run_anomaly_detection, path)
            scores = _get_scores(result)
            above = _above_threshold(scores, th)
            status = "ABOVE threshold (FP)" if above else "below threshold (TN)"
            print(f"  {path.name}: Pn={scores.get('Pneumonia', 0):.4f}, Con={scores.get('Consolidation', 0):.4f}, Ptx={scores.get('Pneumothorax', 0):.4f}, Eff={scores.get('Effusion', 0):.4f} -> {status}")
    print()

    # ---- Step 2: Other pathologies (skipped; no abdomen) ----
    print("--- Step 2: Other pathologies ---")
    print("Skipped (no abdomen; optional other-chest pathologies can be added to positive/ or a separate folder later).")
    print()

    # ---- Step 3: Repeatability ----
    print("--- Step 3: Repeatability ---")
    sample = positives[0]
    results = [_run_inference(run_anomaly_detection, sample) for _ in range(args.repeatability_runs)]
    scores_list = [_get_scores(r) for r in results]
    if any(s is None for s in scores_list):
        print("  FAIL: model error in at least one run")
    else:
        first = scores_list[0]
        same = all(s == first for s in scores_list)
        print(f"  {sample.name} x{args.repeatability_runs}: scores identical = {same}")
        if not same:
            for i, s in enumerate(scores_list):
                print(f"    run {i+1}: Pneumonia={s.get('Pneumonia')}, Consolidation={s.get('Consolidation')}")
    print()

    # ---- Step 4: Preprocessing robustness (format: same image JPEG vs PNG) ----
    print("--- Step 4: Preprocessing robustness (JPEG vs PNG) ---")
    with open(sample, "rb") as f:
        raw_jpeg = f.read()
    from PIL import Image
    buf = io.BytesIO()
    Image.open(io.BytesIO(raw_jpeg)).save(buf, format="PNG")
    raw_png = buf.getvalue()
    r_j = run_anomaly_detection(image_url="", image_bytes=raw_jpeg)
    r_p = run_anomaly_detection(image_url="", image_bytes=raw_png)
    s_j = _get_scores(r_j)
    s_p = _get_scores(r_p)
    if s_j is None or s_p is None:
        print("  FAIL: model error on JPEG or PNG")
    else:
        diff = max(abs(s_j.get(n, 0) - s_p.get(n, 0)) for n in (s_j.keys() | s_p.keys()))
        ok = diff < 0.01
        print(f"  Max score difference (JPEG vs PNG): {diff:.6f} -> {'PASS (similar)' if ok else 'CHECK (large diff)'}")
    print()

    # ---- Sanity vs TorchXRayVision ----
    print("--- Sanity vs TorchXRayVision ---")
    with open(sample, "rb") as f:
        raw = f.read()
    pipeline_result = run_anomaly_detection(image_url="", image_bytes=raw)
    model = get_model()
    if model is None:
        print("  FAIL: model not loaded")
    else:
        import torch
        x = _preprocess_torchxrayvision(raw)
        device = next(model.parameters()).device
        x = x.to(device)
        with torch.no_grad():
            out = model(x)
        probs = out.flatten().sigmoid().cpu().numpy()
        pipeline_scores = _get_scores(pipeline_result)
        if pipeline_scores is None:
            print("  FAIL: pipeline returned no scores")
        else:
            pathologies = list(pipeline_scores.keys())
            max_diff = 0.0
            for i, name in enumerate(pathologies):
                if i < len(probs):
                    a = pipeline_scores[name]
                    b = float(probs[i])
                    max_diff = max(max_diff, abs(a - b))
            match = max_diff < 1e-5
            print(f"  Pipeline vs raw model (first {len(pathologies)} pathologies): max diff = {max_diff:.2e} -> {'PASS (match)' if match else 'MISMATCH'}")
    print()

    # ---- Threshold: sensitivity / specificity ----
    print(f"--- Threshold {th} (critical: Pneumonia, Consolidation, Pneumothorax, Effusion): sensitivity / specificity ---")
    tp = fp = 0
    for path in positives:
        result = _run_inference(run_anomaly_detection, path)
        if _above_threshold(_get_scores(result), th):
            tp += 1
    for path in normals:
        result = _run_inference(run_anomaly_detection, path)
        if _above_threshold(_get_scores(result), th):
            fp += 1
    n_pos = len(positives)
    n_norm = len(normals)
    fn = n_pos - tp
    tn = n_norm - fp
    sensitivity = tp / n_pos if n_pos else 0
    specificity = tn / n_norm if n_norm else 0
    print(f"  Positives: {tp}/{n_pos} above threshold (TP); {fn} below (FN)")
    print(f"  Normals:  {tn}/{n_norm} below threshold (TN); {fp} above (FP)")
    print(f"  Sensitivity (TP/(TP+FN)): {sensitivity:.4f}")
    print(f"  Specificity (TN/(TN+FP)): {specificity:.4f}")
    if n_norm == 0:
        print("  (Add normal images for meaningful specificity.)")
    print()
    print("Done.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
