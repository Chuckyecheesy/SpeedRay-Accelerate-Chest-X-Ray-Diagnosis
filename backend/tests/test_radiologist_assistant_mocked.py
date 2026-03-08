#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to sys.path
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

# Mock the storage.solana_client and diagnostic_summary to avoid cascading imports
sys.modules['backend.storage.solana_client'] = MagicMock()
import backend.storage.solana_client as mock_solana
mock_solana.submit_log.return_value = {"success": True, "signature": "mock_tx_123"}

# We can't easily mock relative imports for the module under test if we import it normally.
# But we can import it after mocking.
# However, radiologist_assistant.py uses relative imports. 
# Let's try to import it by manually setting its package.

import importlib.util

def load_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # Set the package so relative imports work if we have the parent in sys.path
    module.__package__ = 'backend.ai_agents'
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

try:
    path = str(root / 'ai_agents' / 'radiologist_assistant.py')
    assistant = load_module_from_path('backend.ai_agents.radiologist_assistant', path)
except Exception as e:
    print(f"Failed to load module: {e}")
    # Fallback: if we can't load it with relative imports even with mocking, 
    # we might need to change the imports in the file to absolute for the test.
    sys.exit(1)

def test_radiologist_assistant():
    base_input = {
        "filename": "pneumonia.jpeg",
        "top_critical": {"name": "Pneumonia", "score": 0.89, "risk": "High"},
        "annotated_url": "https://cloudinary.com/sample_xray_annotated.jpg",
        "diagnostic_report": {
            "explanation": "Pneumonia on X-ray shows focal or multifocal consolidation.",
            "recommended_next_steps": "Correlate with clinical picture; cultures and antibiotics."
        }
    }

    # Case 1: doctor_response is "null"
    case_null = base_input.copy()
    case_null["doctor_response"] = "null"
    res_null = assistant.get_radiologist_assistant_response(case_null)
    print("--- Case: doctor_response=null ---")
    # print(json.dumps(res_null, indent=2))
    assert res_null["conversation_status"] == "open"
    assert "Please review" in res_null["next_action"]
    print("OK")

    # Case 2: doctor_response is "accept"
    case_accept = base_input.copy()
    case_accept["doctor_response"] = "accept"
    res_accept = assistant.get_radiologist_assistant_response(case_accept)
    print("\n--- Case: doctor_response=accept ---")
    # print(json.dumps(res_accept, indent=2))
    assert res_accept["conversation_status"] == "closed"
    assert "Solana" in res_accept["next_action"]
    print("OK")

    # Case 3: doctor_response is "reject"
    case_reject = base_input.copy()
    case_reject["doctor_response"] = "reject"
    res_reject = assistant.get_radiologist_assistant_response(case_reject)
    print("\n--- Case: doctor_response=reject ---")
    # print(json.dumps(res_reject, indent=2))
    assert res_reject["conversation_status"] == "closed"
    assert "manual re-evaluation" in res_reject["next_action"]
    print("OK")

if __name__ == "__main__":
    test_radiologist_assistant()
    print("\nAll tests passed successfully!")
