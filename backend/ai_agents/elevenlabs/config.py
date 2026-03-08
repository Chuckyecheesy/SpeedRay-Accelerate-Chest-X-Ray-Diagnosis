"""API key and voice config for SpeedRay ElevenLabs (from .env via Settings or os.environ)."""

import os

def _env_file_path():
    """Project root .env (same as backend.config.settings)."""
    return os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")), ".env")

def _read_key_from_env_file():
    """Read SPEEDRAY_ELEVENLABS_API_KEY directly from .env file as fallback."""
    path = _env_file_path()
    if not os.path.isfile(path):
        return ""
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("SPEEDRAY_ELEVENLABS_API_KEY=") and not line.startswith("#"):
                    return line.split("=", 1)[1].strip().strip("'\"").strip()
    except Exception:
        pass
    return ""

def _get_key():
    try:
        from backend.config.settings import get_settings
        s = get_settings()
        if s.elevenlabs_api_key:
            return s.elevenlabs_api_key
    except Exception:
        pass
    key = os.environ.get("SPEEDRAY_ELEVENLABS_API_KEY", "")
    if key:
        return key
    return _read_key_from_env_file()

def _get_voice_id():
    try:
        from backend.config.settings import get_settings
        s = get_settings()
        if s.elevenlabs_voice_id:
            return s.elevenlabs_voice_id
    except Exception:
        pass
    return os.environ.get("SPEEDRAY_ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

# For backward compatibility; read at import (Settings loads .env)
ELEVENLABS_API_KEY = _get_key()
ELEVENLABS_VOICE_ID = _get_voice_id()
