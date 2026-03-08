#!/usr/bin/env python3
"""Robust server startup script with comprehensive error handling."""

import sys
import os
import time
import traceback
from pathlib import Path

def log_to_file(message):
    """Simple file logging that always works."""
    try:
        with open("/Applications/SpeedRay/.cursor/debug-853f04.log", "a") as f:
            timestamp = int(time.time() * 1000)
            f.write(f'{{"sessionId":"853f04","timestamp":{timestamp},"message":"{message}"}}\n')
    except Exception:
        pass

def main():
    print("=== SPEEDRAY SERVER STARTUP ===")
    log_to_file("Server startup script started")
    
    # Ensure we're in the right directory
    os.chdir("/opt/speedray")
    print(f"Working directory: {os.getcwd()}")
    log_to_file(f"Working directory set to {os.getcwd()}")
    
    # Add current directory to Python path
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
        print("Added current directory to Python path")
        log_to_file("Added current directory to Python path")
    
    # Check virtual environment
    venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print(f"Virtual environment active: {venv_active}")
    log_to_file(f"Virtual environment active: {venv_active}")
    
    if not venv_active:
        print("WARNING: Virtual environment not active!")
        log_to_file("WARNING: Virtual environment not active")
    
    # Test critical imports
    try:
        import fastapi
        print(f"✓ FastAPI: {fastapi.__version__}")
        log_to_file(f"FastAPI imported successfully: {fastapi.__version__}")
    except Exception as e:
        print(f"✗ FastAPI import failed: {e}")
        log_to_file(f"FastAPI import failed: {str(e)}")
        return False
    
    try:
        import uvicorn
        print(f"✓ Uvicorn: {uvicorn.__version__}")
        log_to_file(f"Uvicorn imported successfully: {uvicorn.__version__}")
    except Exception as e:
        print(f"✗ Uvicorn import failed: {e}")
        log_to_file(f"Uvicorn import failed: {str(e)}")
        return False
    
    # Test app import
    try:
        from backend.api.main import app
        print(f"✓ FastAPI app imported: {app.title}")
        log_to_file(f"FastAPI app imported successfully: {app.title}")
    except Exception as e:
        print(f"✗ App import failed: {e}")
        log_to_file(f"App import failed: {str(e)}")
        traceback.print_exc()
        return False
    
    # Try multiple binding approaches
    binding_configs = [
        ("127.0.0.1", 8000),  # localhost only
        ("0.0.0.0", 8000),    # all interfaces
        ("0.0.0.0", 8001),    # different port
    ]
    
    for host, port in binding_configs:
        try:
            print(f"\n=== ATTEMPTING TO START SERVER ON {host}:{port} ===")
            log_to_file(f"Attempting to start server on {host}:{port}")
            
            # Use uvicorn programmatically with explicit config
            config = uvicorn.Config(
                app=app,
                host=host,
                port=port,
                log_level="info",
                access_log=True,
                timeout_keep_alive=30,
                loop="asyncio"
            )
            server = uvicorn.Server(config)
            
            print(f"Server config created, starting...")
            log_to_file(f"Server config created for {host}:{port}")
            
            # Start server (this will block)
            server.run()
            
        except Exception as e:
            print(f"✗ Server failed on {host}:{port}: {e}")
            log_to_file(f"Server failed on {host}:{port}: {str(e)}")
            traceback.print_exc()
            continue
    
    print("All binding attempts failed")
    log_to_file("All server binding attempts failed")
    return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        log_to_file("Server stopped by user (KeyboardInterrupt)")
    except Exception as e:
        print(f"Fatal error: {e}")
        log_to_file(f"Fatal error: {str(e)}")
        traceback.print_exc()