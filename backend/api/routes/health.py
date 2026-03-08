"""Health check for Vultr/deployment (SpeedRay)."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "SpeedRay"}

@router.get("/ping")
def ping():
    return {"status": "ok", "message": "Heartbeat received"}
