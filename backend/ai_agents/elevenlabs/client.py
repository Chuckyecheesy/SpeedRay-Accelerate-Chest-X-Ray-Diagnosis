"""ElevenLabs TTS client for SpeedRay."""

from typing import Optional

from .config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, _get_key, _get_voice_id


def text_to_speech(text: str, voice_id: Optional[str] = None) -> dict:
    """Generate audio explanation from text via ElevenLabs. Returns url or base64 audio."""
    api_key = _get_key() or ELEVENLABS_API_KEY
    if not api_key:
        return {"url": "", "error": "API not configured"}

    vid = voice_id or _get_voice_id() or ELEVENLABS_VOICE_ID
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=api_key)
        # convert() returns Iterator[bytes]; join chunks to get full audio
        chunks = client.text_to_speech.convert(vid, text=text)
        audio = b"".join(chunks)
        import base64
        b64 = base64.b64encode(audio).decode("utf-8")
        return {"url": f"data:audio/mpeg;base64,{b64}", "error": None}
    except Exception as e:
        return {"url": "", "error": str(e)}
