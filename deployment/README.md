# SpeedRay deployment — Vultr, Tailscale, Backboard.io

## Overview

- **API (backend):** FastAPI app with PyTorch/TorchXRayVision (NIH 14-disease model), Gemini, RAG, ElevenLabs, Cloudinary, Presage, Solana. Deploy on a **Vultr VPS or container** (see [vultr/README.md](vultr/README.md)). Vultr Serverless Inference is LLM-focused; for this API + custom model, use a VPS or container.
- **Pipeline orchestration:** Backboard.io (DAG: upload → anomaly → RAG → report → audio → risk → log).
- **Secure access:** Tailscale for demo or internal access.

## Quick start (Vultr VPS)

1. Create a Vultr VPS (Ubuntu 24.04, ≥2GB RAM recommended).
2. Follow [vultr/README.md](vultr/README.md) to install Python deps, set env vars, and run `uvicorn` or Gunicorn from `backend/`.
3. Configure Cloudinary, Gemini, ElevenLabs (and optionally Backboard, Solana, Presage, Auth0) per [vultr/serverless.yaml](vultr/serverless.yaml).

## Stateful / fast pipeline (results in seconds)

The API **preloads the X-ray model** at startup so the first request does not wait 1–2 minutes. The model stays in memory (stateful/persistent) for the lifetime of the process.

- **Startup:** A background thread loads the model when the server starts; after it finishes, all pipeline runs return in seconds.
- **Optional warmup:** After deploy or after a cold start, call **`GET /pipeline/warmup`** to ensure the model is loaded. Returns `{"ok": true, "model_loaded": true}` when ready.

## Backboard.io

Pipeline definition and deployment notes: [backboard/README.md](backboard/README.md).

## Env vars

See [vultr/serverless.yaml](vultr/serverless.yaml) for the full list of `SPEEDRAY_*` variables.
