#!/usr/bin/env python3
"""Basic diagnostic script to identify import issues."""

import sys
import os
import traceback

# Basic logging without imports
def log_debug(message, data=None):
    try:
        import time
        log_entry = {
            "sessionId": "853f04",
            "location": "debug_basic.py",
            "message": message,
            "data": data or {},
            "timestamp": int(time.time() * 1000)
        }
        with open("/Applications/SpeedRay/.cursor/debug-853f04.log", "a") as f:
            f.write(str(log_entry).replace("'", '"') + '\n')
    except Exception:
        pass

log_debug("Starting basic diagnostic", {"cwd": os.getcwd(), "python_version": sys.version})

# Test 1: Check if we're in the right directory
if os.path.exists("backend"):
    log_debug("Backend directory found", {"status": "ok"})
else:
    log_debug("Backend directory NOT found", {"status": "error", "files": os.listdir(".")})

# Test 2: Check if virtual environment is active
venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
log_debug("Virtual environment check", {"active": venv_active, "prefix": sys.prefix})

# Test 3: Try importing basic dependencies
try:
    import fastapi
    log_debug("FastAPI import", {"status": "success", "version": getattr(fastapi, '__version__', 'unknown')})
except Exception as e:
    log_debug("FastAPI import", {"status": "failed", "error": str(e)})

try:
    import pydantic
    log_debug("Pydantic import", {"status": "success", "version": getattr(pydantic, '__version__', 'unknown')})
except Exception as e:
    log_debug("Pydantic import", {"status": "failed", "error": str(e)})

try:
    import uvicorn
    log_debug("Uvicorn import", {"status": "success", "version": getattr(uvicorn, '__version__', 'unknown')})
except Exception as e:
    log_debug("Uvicorn import", {"status": "failed", "error": str(e)})

# Test 4: Try importing our settings
try:
    sys.path.insert(0, os.getcwd())
    from backend.config.settings import get_settings
    settings = get_settings()
    log_debug("Settings import", {"status": "success", "api_port": settings.api_port})
except Exception as e:
    log_debug("Settings import", {"status": "failed", "error": str(e), "traceback": traceback.format_exc()})

# Test 5: Try importing the main app
try:
    from backend.api.main import app
    log_debug("Main app import", {"status": "success", "app_type": str(type(app))})
except Exception as e:
    log_debug("Main app import", {"status": "failed", "error": str(e), "traceback": traceback.format_exc()})

log_debug("Basic diagnostic completed")
print("Basic diagnostic completed - check debug log for results")