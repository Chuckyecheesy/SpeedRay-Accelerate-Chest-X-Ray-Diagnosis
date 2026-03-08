# SpeedRay — Architecture

## Data flow

1. **Upload** — User uploads chest X-ray → Cloudinary (image + metadata).
2. **Anomaly** — PyTorch XRayTorchModel runs on image → anomaly score and regions.
3. **RAG** — NoSQL retrieval over Kaggle + NHI datasets → context chunks.
4. **Report** — Gemini API generates deterministic diagnostic report (summary, findings, impression).
5. **Audio** — ElevenLabs turns impression/summary into spoken explanation.
6. **Risk** — Presage returns risk level and confidence.
7. **Log** — Solana stores uneditable log (run_id, report, risk) after submission.

Orchestration can run on Backboard.io or in-process (backend or frontend).

## Stack

- **Frontend:** React (Vite), Auth0, Reactiv-ClipKit Lab demo.
- **Backend:** FastAPI, Python ai_agents (Torch, Gemini, RAG, ElevenLabs, Presage), Cloudinary, Solana.
- **Deploy:** Vultr Serverless, Tailscale for secure demo.
