"""API key and model config for SpeedRay Gemini."""

import os

from ...config import get_settings

_settings = get_settings()
GEMINI_API_KEY = os.environ.get("SPEEDRAY_GEMINI_API_KEY", "") or (_settings.gemini_api_key or "")
# Default: use a stable model ID (no -latest; see ai.google.dev/gemini-api/docs/models).
GEMINI_MODEL = os.environ.get("SPEEDRAY_GEMINI_MODEL", "gemini-2.0-flash")
