# SpeedRay — Instant Chest X-ray Diagnosis

Project overview, setup, and SpeedRay namespace. See `STRUCTURE.md` for the full folder and file tree.

## Quick start

**Backend (Python)**  
From repo root with `PYTHONPATH=.`:
```bash
pip install -r backend/requirements.txt
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (React + Vite)**  
```bash
npm install
npm run dev
```
Set `.env` from `.env.example` (e.g. `VITE_API_BASE=http://localhost:8000`). Open http://localhost:3006 to upload an X-ray and run the pipeline.
