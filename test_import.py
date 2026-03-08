#!/usr/bin/env python3
"""Test script to check if we can import the FastAPI app."""

import sys
import os
sys.path.insert(0, '/opt/speedray')

# #region agent log
try:
    open("/Applications/SpeedRay/.cursor/debug-853f04.log", "a").write('{"sessionId":"853f04","hypothesisId":"H4","location":"test_import.py:start","message":"Testing import of FastAPI app","data":{"python_path":"' + str(sys.path[0]) + '","cwd":"' + os.getcwd() + '"},"timestamp":' + str(int(__import__('time').time() * 1000)) + '}\n')
except Exception:
    pass
# #endregion

try:
    from backend.api.main import app
    # #region agent log
    try:
        open("/Applications/SpeedRay/.cursor/debug-853f04.log", "a").write('{"sessionId":"853f04","hypothesisId":"H4","location":"test_import.py:import_success","message":"FastAPI app imported successfully","data":{"app_type":str(type(app)),"title":getattr(app, "title", "unknown")},"timestamp":' + str(int(__import__('time').time() * 1000)) + '}\n')
    except Exception:
        pass
    # #endregion
    print("SUCCESS: FastAPI app imported successfully")
except Exception as e:
    # #region agent log
    try:
        open("/Applications/SpeedRay/.cursor/debug-853f04.log", "a").write('{"sessionId":"853f04","hypothesisId":"H4","location":"test_import.py:import_error","message":"FastAPI app import failed","data":{"error":str(e)[:300],"error_type":type(e).__name__},"timestamp":' + str(int(__import__('time').time() * 1000)) + '}\n')
    except Exception:
        pass
    # #endregion
    print(f"ERROR: Failed to import FastAPI app: {e}")
    sys.exit(1)