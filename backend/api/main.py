"""FastAPI app entry; SpeedRay API."""

import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .routes import health, upload, pipeline, report, auth_callback, rag, audio, risk, log, ai

# Path for idle-shutdown: last activity timestamp (frontend/API use). Updated by middleware.
_SPEEDRAY_ACTIVITY_FILE = Path(__file__).resolve().parent.parent.parent / ".speedray_last_activity"


def _preload_xray_model():
    """Load X-ray model into memory so first request returns in seconds (stateful/persistent)."""
    try:
        from ..ai_agents.torch_xray_model.model import load_model
        load_model()
    except Exception:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Preload AI model at startup so pipeline results return in seconds instead of 1–2 min."""
    import threading
    t = threading.Thread(target=_preload_xray_model, daemon=True)
    t.start()
    yield
    # shutdown: nothing to tear down; model stays in process until exit


app = FastAPI(title="SpeedRay API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3006",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3006",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _activity_tracking_middleware(request: Request, call_next):
    """Record last activity time when frontend/API is used (skip / and /health for idle shutdown)."""
    response = await call_next(request)
    if request.url.path not in ("/", "/health"):
        try:
            _SPEEDRAY_ACTIVITY_FILE.write_text(str(int(time.time())))
        except Exception:
            pass
    return response


app.middleware("http")(_activity_tracking_middleware)


@app.get("/")
def root():
    return {"service": "SpeedRay API", "docs": "/docs", "health": "/health"}

app.include_router(health.router)
app.include_router(upload.router)
app.include_router(pipeline.router)
app.include_router(report.router)
app.include_router(auth_callback.router)
app.include_router(rag.router)
app.include_router(audio.router)
app.include_router(risk.router)
app.include_router(log.router)
app.include_router(ai.router)
