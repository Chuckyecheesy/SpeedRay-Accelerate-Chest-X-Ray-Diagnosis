#!/usr/bin/env python3
"""Manual server startup test."""

import sys
import os

print("=== MANUAL SERVER TEST ===")

# Ensure we're in the right directory and can import
sys.path.insert(0, os.getcwd())

try:
    print("Importing FastAPI app...")
    from backend.api.main import app
    print("✓ App imported successfully")
    
    print("Importing uvicorn...")
    import uvicorn
    print("✓ Uvicorn imported successfully")
    
    print("Starting server manually...")
    print("Server will run for 10 seconds then stop")
    
    # Run server with a timeout
    import signal
    import threading
    import time
    
    def timeout_handler(signum, frame):
        print("\nTimeout reached, stopping server")
        os._exit(0)
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)  # 10 second timeout
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except SystemExit:
        print("\nServer stopped by timeout")
    
except Exception as e:
    print(f"✗ Server startup failed: {e}")
    import traceback
    traceback.print_exc()

print("=== MANUAL SERVER TEST COMPLETE ===")