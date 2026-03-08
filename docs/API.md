# SpeedRay — API

Base URL: `http://localhost:8000` (or VITE_API_BASE).

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /upload/image | Upload X-ray image (multipart file) → Cloudinary |
| POST | /pipeline/run | Run full pipeline (multipart file) → state |
| POST | /report/generate | Generate report (JSON: run_id, rag_context, anomaly_summary) |
| GET | /report/{run_id} | Get report by run_id |
| GET | /rag/retrieve | RAG retrieve (query, top_k) |
| POST | /audio/generate | ElevenLabs TTS (JSON: text) |
| POST | /risk/predict | Presage risk (JSON: report_summary, findings, anomaly_score) |
| POST | /log/submit | Solana log (JSON: run_id, study_id, payload) |
| GET | /callback | Auth0 callback redirect |
