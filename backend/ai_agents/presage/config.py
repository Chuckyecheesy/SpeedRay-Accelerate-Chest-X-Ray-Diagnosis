"""Presage endpoint config for SpeedRay."""

import os

PRESAGE_BASE_URL = os.environ.get("SPEEDRAY_PRESAGE_BASE_URL", "")
PRESAGE_API_KEY = os.environ.get("SPEEDRAY_PRESAGE_API_KEY", "")
