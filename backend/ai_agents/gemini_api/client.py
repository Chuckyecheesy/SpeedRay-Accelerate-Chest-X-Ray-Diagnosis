"""Gemini API client for report (SpeedRay). OpenAI models used as fallback when all Gemini models fail."""

from typing import Any, Dict, List, Optional

from ...config import get_settings
from .config import GEMINI_API_KEY, GEMINI_MODEL

# Gemini fallbacks per https://ai.google.dev/gemini-api/docs/models (use stable IDs; avoid -latest).
# Call ListModels (v1beta/models) to see current list and supported methods.
_GEMINI_FALLBACK_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash-8b",
    "gemini-1.0-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-3.1-flash-lite-preview",
    "gemini-3-flash-preview",
]

# OpenAI fallback models per https://developers.openai.com/api/docs/models (chat completions).
# Order: frontier / most capable first, then older and cost-efficient.
OPENAI_FALLBACK_MODELS = [
    "gpt-5.4",
    "gpt-5.4-pro",
    "gpt-5.2",
    "gpt-5.1",
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
]


def generate_diagnostic_report(
    prompt: str,
    rag_context: str,
    anomaly_summary: str,
    suspected_diseases: Optional[List[str]] = None,
    system_instruction: str = "You are a radiology assistant. Output a very short report that discusses ONLY the single finding the image model detected. Do not list other body systems, do not say 'no other findings,' do not add multiple impression items. One finding only — e.g. if the finding is Pneumonia, the entire report talks only about pneumonia.",
) -> Dict[str, Any]:
    """Call Gemini to produce a deterministic diagnostic report."""
    if not GEMINI_API_KEY:
        return {
            "summary": "",
            "findings": [],
            "impression": "API not configured.",
        }

    suspected = (suspected_diseases or [])[:1]
    diseases_blurb = (
        f"\n\nDetected finding (discuss ONLY this — do not list other diseases or body systems): {suspected[0]}."
        if suspected
        else "\n\nNo specific finding from the image model. Give one short impression line only."
    )
    full_prompt = (
        f"{prompt}{diseases_blurb}\n\nContext:\n{rag_context}\n\nAnomaly summary:\n{anomaly_summary}"
    )

    try:
        # #region agent log
        try:
            _log = open("/Applications/SpeedRay/.cursor/debug-025a2b.log", "a"); _log.write('{"sessionId":"025a2b","hypothesisId":"H1","location":"gemini_api/client.py:generate_diagnostic_report","message":"Gemini model and attempt","data":{"model": "' + str(GEMINI_MODEL) + '"},"timestamp":' + str(int(__import__("time").time() * 1000)) + '}\n'); _log.close()
        except Exception: pass
        # #endregion
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        models_to_try = [GEMINI_MODEL]
        for m in _GEMINI_FALLBACK_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)
        last_error = None
        for model_id in models_to_try:
            try:
                model = genai.GenerativeModel(model_id, system_instruction=system_instruction)
                response = model.generate_content(full_prompt)
                text = response.text if response and response.text else ""
                return _parse_report_text(text)
            except Exception as e:
                last_error = e
                err_str = str(e)
                is_quota = "429" in err_str or "quota" in err_str.lower()
                is_404 = "404" in err_str or "not found" in err_str.lower()
                if (is_quota or is_404) and model_id != models_to_try[-1]:
                    continue
                raise
        if last_error is not None:
            report = _try_openai_report(full_prompt, system_instruction)
            if report is not None:
                return report
            raise last_error
    except Exception as e:
        # #region agent log
        try:
            _err = str(e).replace("\\", "\\\\").replace('"', "'")[:200]
            _log = open("/Applications/SpeedRay/.cursor/debug-025a2b.log", "a"); _log.write('{"sessionId":"025a2b","hypothesisId":"H1","location":"gemini_api/client.py:exception","message":"Gemini exception","data":{"error":"' + _err + '"},"timestamp":' + str(int(__import__("time").time() * 1000)) + '}\n'); _log.close()
        except Exception: pass
        # #endregion
        return {
            "summary": "",
            "findings": [],
            "impression": f"Error: {e}",
        }


def _try_openai_report(full_prompt: str, system_instruction: str) -> Optional[Dict[str, Any]]:
    """Fallback: try OpenAI chat models in order when all Gemini models fail. Returns None if no key or all fail."""
    settings = get_settings()
    api_key = (getattr(settings, "openai_api_key", None) or "").strip()
    if not api_key:
        api_key = __import__("os").environ.get("SPEEDRAY_OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": full_prompt},
    ]
    for model in OPENAI_FALLBACK_MODELS:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1024,
            )
            text = (resp.choices[0].message.content or "").strip()
            if not text:
                continue
            return _parse_report_text(text)
        except Exception:
            continue
    return None


def _parse_report_text(text: str) -> Dict[str, Any]:
    """Parse free-form report into summary, findings, impression."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    summary = lines[0] if lines else ""
    findings: List[Dict[str, Any]] = []
    impression = ""
    for i, line in enumerate(lines[1:], 1):
        if line.lower().startswith("impression"):
            impression = line.split(":", 1)[-1].strip() if ":" in line else " ".join(lines[i + 1 :])
            break
        if line and not line.lower().startswith("impression"):
            findings.append({"region": "general", "description": line})
    if not impression and lines:
        impression = lines[-1]
    return {
        "summary": summary,
        "findings": findings,
        "impression": impression,
        "raw": text,
    }
