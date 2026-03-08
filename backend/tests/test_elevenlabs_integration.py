#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from backend.ai_agents.radiologist_assistant import get_radiologist_assistant_response
from backend.ai_agents.elevenlabs.client import text_to_speech

def test_elevenlabs_integration():
    # 1. Get a response from the Radiologist Assistant
    input_data = {
        "filename": "pneumothorax.jpeg",
        "top_critical": {"name": "Pneumothorax", "score": 0.95, "risk": "High"},
        "doctor_response": "null",
        "diagnostic_report": {
            "explanation": "Visible visceral pleural line and absent lung markings.",
        }
    }
    
    assistant_res = get_radiologist_assistant_response(input_data)
    text_to_convert = assistant_res["spoken_explanation"]
    
    print(f"Text to convert: {text_to_convert}\n")
    
    # Check if API key is set
    api_key = os.environ.get("SPEEDRAY_ELEVENLABS_API_KEY")
    if not api_key:
        print("WARNING: SPEEDRAY_ELEVENLABS_API_KEY environment variable is not set.")
        print("The test will run in 'check mode' but won't actually hit the API.")
        return

    # 2. Call ElevenLabs TTS
    print("Calling ElevenLabs API...")
    tts_res = text_to_speech(text_to_convert)
    
    if tts_res.get("error"):
        print(f"Error from ElevenLabs: {tts_res['error']}")
    else:
        print("Success! Audio data (base64) received.")
        # print(f"Audio URL/Data: {tts_res['url'][:100]}...")

if __name__ == "__main__":
    test_elevenlabs_integration()
