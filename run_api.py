#!/usr/bin/env python3
"""Run SpeedRay API from project root. Use this on the server so cwd and imports are correct.

  cd /opt/speedray && source venv/bin/activate && python run_api.py

Do NOT run uvicorn from inside backend/ (e.g. cd backend && uvicorn api.main:app) or
relative imports like from ...storage will fail.
"""

import os
import sys

# Project root = directory containing this script
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
os.chdir(PROJECT_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,
    )
