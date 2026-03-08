#!/usr/bin/env python3
"""Ultra-simple test that prints to stdout."""

import sys
import os

print("=== SIMPLE DIAGNOSTIC ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")

# Check if we're in the right place
if os.path.exists("backend"):
    print("✓ Backend directory found")
    if os.path.exists("backend/api/main.py"):
        print("✓ Main API file found")
    else:
        print("✗ Main API file NOT found")
else:
    print("✗ Backend directory NOT found")
    print(f"Files in current directory: {os.listdir('.')}")

# Check virtual environment
venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
print(f"Virtual environment active: {venv_active}")

# Test basic imports
try:
    import fastapi
    print(f"✓ FastAPI available: {fastapi.__version__}")
except ImportError as e:
    print(f"✗ FastAPI not available: {e}")

try:
    import uvicorn
    print(f"✓ Uvicorn available: {uvicorn.__version__}")
except ImportError as e:
    print(f"✗ Uvicorn not available: {e}")

try:
    import pydantic_settings
    print(f"✓ Pydantic-settings available")
except ImportError as e:
    print(f"✗ Pydantic-settings not available: {e}")

# Test our app import
print("\n=== TESTING APP IMPORT ===")
try:
    sys.path.insert(0, os.getcwd())
    from backend.api.main import app
    print(f"✓ FastAPI app imported successfully: {type(app)}")
    print(f"✓ App title: {app.title}")
except Exception as e:
    print(f"✗ Failed to import FastAPI app: {e}")
    import traceback
    print("Full traceback:")
    traceback.print_exc()

print("\n=== DIAGNOSTIC COMPLETE ===")