# SpeedRay backend — overview and run instructions.

## Run the API

From the **project root** (so `backend` is the top-level package):

```bash
cd /Applications/SpeedRay
uvicorn backend.api.main:app --reload
```

Then open http://127.0.0.1:8000. Do not run uvicorn from inside `backend/` (e.g. `cd backend && uvicorn api.main:app`) or relative imports like `from ...storage` will fail.
