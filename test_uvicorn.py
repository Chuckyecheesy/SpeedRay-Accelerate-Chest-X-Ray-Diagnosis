#!/usr/bin/env python3
"""Test uvicorn startup directly."""

import sys
import os
import time

# Basic logging
def log_debug(message, data=None):
    try:
        log_entry = {
            "sessionId": "853f04",
            "location": "test_uvicorn.py",
            "message": message,
            "data": data or {},
            "timestamp": int(time.time() * 1000)
        }
        with open("/Applications/SpeedRay/.cursor/debug-853f04.log", "a") as f:
            f.write(str(log_entry).replace("'", '"') + '\n')
    except Exception:
        pass

log_debug("Testing uvicorn startup")

try:
    import uvicorn
    log_debug("Uvicorn imported successfully")
    
    # Try to create a simple FastAPI app
    from fastapi import FastAPI
    simple_app = FastAPI()
    
    @simple_app.get("/")
    def root():
        return {"status": "test"}
    
    log_debug("Simple FastAPI app created")
    
    # Try to run uvicorn programmatically for a few seconds
    import threading
    import signal
    
    def run_server():
        try:
            uvicorn.run(simple_app, host="0.0.0.0", port=8000, log_level="info")
        except Exception as e:
            log_debug("Uvicorn run failed", {"error": str(e)})
    
    log_debug("Starting uvicorn in thread")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait a bit then check if server is running
    time.sleep(3)
    log_debug("Checking if server started")
    
    # Try to make a request to ourselves
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000", timeout=2)
        log_debug("Server test request", {"status_code": response.status_code, "response": response.text[:100]})
    except Exception as e:
        log_debug("Server test request failed", {"error": str(e)})
    
except Exception as e:
    log_debug("Uvicorn test failed", {"error": str(e)})

log_debug("Uvicorn test completed")
print("Uvicorn test completed")