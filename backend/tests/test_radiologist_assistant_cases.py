#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from backend.ai_agents.radiologist_assistant import get_radiologist_assistant_response

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
    res_null = get_radiologist_assistant_response(case_null)
    print("--- Case: doctor_response=null ---")
    print(json.dumps(res_null, indent=2))
    assert res_null["conversation_status"] == "open"
    assert "Please review" in res_null["next_action"]
    assert "NIH 14" in res_null["spoken_explanation"]
    assert "https://cloudinary.com/sample_xray_annotated.jpg" in res_null["spoken_explanation"]

    # Case 2: doctor_response is "accept"
    case_accept = base_input.copy()
    case_accept["doctor_response"] = "accept"
    res_accept = get_radiologist_assistant_response(case_accept)
    print("\n--- Case: doctor_response=accept ---")
    print(json.dumps(res_accept, indent=2))
    assert res_accept["conversation_status"] == "closed"
    assert "Solana" in res_accept["next_action"]

    # Case 3: doctor_response is "reject"
    case_reject = base_input.copy()
    case_reject["doctor_response"] = "reject"
    res_reject = get_radiologist_assistant_response(case_reject)
    print("\n--- Case: doctor_response=reject ---")
    print(json.dumps(res_reject, indent=2))
    assert res_reject["conversation_status"] == "closed"
    assert "sputum culture" in res_reject["next_action"]

    # Case 4: doctor_response is unexpected
    case_fail = base_input.copy()
    case_fail["doctor_response"] = "invalid_state"
    res_fail = get_radiologist_assistant_response(case_fail)
    print("\n--- Case: doctor_response=invalid_state ---")
    print(json.dumps(res_fail, indent=2))
    assert res_fail["conversation_status"] == "open"
    assert "manual interpretation" in res_fail["next_action"]

if __name__ == "__main__":
    test_radiologist_assistant()
    print("\nAll tests passed successfully!")
