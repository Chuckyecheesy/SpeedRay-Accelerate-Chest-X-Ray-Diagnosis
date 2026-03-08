"""Audio generation endpoint for SpeedRay frontend."""

from fastapi import APIRouter
from pydantic import BaseModel
from ...ai_agents.elevenlabs import text_to_speech

router = APIRouter(prefix="/audio", tags=["audio"])


class AudioRequest(BaseModel):
    text: str


@router.get("/status")
def audio_status():
    """Check if ElevenLabs API key is configured (for debugging)."""
    try:
        from ...ai_agents.elevenlabs.config import _get_key
        key = _get_key()
    except Exception:
        key = ""
    return {"configured": bool(key)}


@router.post("/generate")
def generate_audio(req: AudioRequest):
    return text_to_speech(req.text)
