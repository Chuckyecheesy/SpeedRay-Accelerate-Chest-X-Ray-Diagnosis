# X-ray test fixtures for reliability tests

- **normal/** — Place chest X-rays with no pneumonia/consolidation (normal or other findings only). Used for specificity: expect few/no Pneumonia or Consolidation scores above threshold.
- **positive/** — Place chest X-rays with known pneumonia or consolidation. Used for sensitivity.

At least one image in **positive/** is required. If **positive/** is empty, the runner uses `pneumonia.jpeg` in the project root as the single positive. For **normal/**, add one or more normal chest X-rays to run Step 1 and threshold specificity.

**Where to get images (chest X-ray only; no abdomen):**
- NIH ChestX-ray14: https://nihcc.app.box.com/v/ChestXray-NIHCC (select “Normal” or use the CSV to pick negative Pneumonia/Consolidation).
- RSNA Pneumonia Challenge (Kaggle): train set has normal and pneumonia labels.
- You can also use your own de-identified chest X-rays.

Copy or symlink images into `normal/` and `positive/`. Supported: `.jpg`, `.jpeg`, `.png`.

**How to run the reliability tests (from project root):**
```bash
pip install -r backend/requirements.txt
PYTHONPATH=. python3 run_xray_reliability_tests.py --threshold 0.5
```
Optional: `--fixtures-dir PATH`, `--repeatability-runs N`.
