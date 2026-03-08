"""Sync/async pipeline runners for SpeedRay."""

from typing import Any, Dict, List

from ..storage import (
    add_annotation,
    build_annotated_image_url_with_text,
    diseases_to_annotations,
    regions_to_annotations,
    upload_image,
    submit_log,
)
from ..ai_agents.torch_xray_model import run_anomaly_detection
from ..ai_agents.torch_xray_model.config import CRITICAL_PATHOLOGIES, DEFAULT_CONFIDENCE_THRESHOLD
from ..ai_agents.rag import retrieve
from ..ai_agents.gemini_api import generate_diagnostic_report
from ..ai_agents.elevenlabs import text_to_speech
from ..ai_agents.presage import get_risk_prediction
from ..ai_agents.radiologist_assistant import get_radiologist_assistant_response
from ..ai_agents.risk_calculator import get_risk_level


def _detected_disease_names(anomaly_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return only the single highest critical finding. Uses top_critical when present."""
    top = anomaly_result.get("top_critical")
    if isinstance(top, dict) and top.get("name") is not None:
        return [{"name": top["name"], "score": float(top.get("score", 0))}]
    diseases = anomaly_result.get("diseases") or []
    above = [
        (d["name"], float(d["score"]))
        for d in diseases
        if isinstance(d, dict)
        and d.get("name") in CRITICAL_PATHOLOGIES
        and d.get("score", 0) >= DEFAULT_CONFIDENCE_THRESHOLD
    ]
    if not above:
        return []
    best = max(above, key=lambda x: x[1])
    return [{"name": best[0], "score": best[1]}]


def run_pipeline_sync(run_id: str, study_id: str, image_bytes: bytes, report_prompt: str) -> Dict[str, Any]:
    """Run full SpeedRay pipeline synchronously (upload -> anomaly -> RAG -> report -> audio -> risk -> log)."""
    import time as _time
    _t0 = _time.time()
    # #region agent log
    try:
        open("/Applications/SpeedRay/.cursor/debug-025a2b.log", "a").write('{"sessionId":"025a2b","hypothesisId":"H1","location":"pipeline/runners.py:entry","message":"Pipeline started","data":{"run_id":"' + str(run_id)[:50] + '","elapsed_ms":0},"timestamp":' + str(int(_time.time() * 1000)) + '}\n')
    except Exception: pass
    # #endregion
    state = {"run_id": run_id, "study_id": study_id, "error": None}

    # 1. Upload and annotate
    upload_result = upload_image(image_bytes, folder="speedray")
    # #region agent log
    try: open("/Applications/SpeedRay/.cursor/debug-025a2b.log", "a").write('{"sessionId":"025a2b","hypothesisId":"H1","location":"pipeline/runners.py:after_upload","message":"Step timing","data":{"step":"upload","elapsed_ms":int((_time.time()-_t0)*1000)},"timestamp":' + str(int(_time.time() * 1000)) + '}\n')
    except Exception: pass
    # #endregion
    state["upload_result"] = upload_result
    url = upload_result.get("secure_url") or upload_result.get("url") or ""
    public_id = upload_result.get("public_id") or ""

    # 2. Anomaly detection (time-bounded; first run can be 1–2 min)
    try:
        from concurrent.futures import ThreadPoolExecutor as _TPEanom
        with _TPEanom(max_workers=1) as _ex:
            _fut = _ex.submit(run_anomaly_detection, url, image_bytes)
            anomaly_result = _fut.result(timeout=120)
    except Exception as _e:
        anomaly_result = {"score": 0, "diseases": [], "regions": [], "top_critical": None}
        state["error"] = f"Anomaly detection timed out or failed: {_e!s}"[:150]
    state["anomaly_result"] = anomaly_result
    # #region agent log
    try: open("/Applications/SpeedRay/.cursor/debug-025a2b.log", "a").write('{"sessionId":"025a2b","hypothesisId":"H1","location":"pipeline/runners.py:after_anomaly","message":"Step timing","data":{"step":"anomaly","elapsed_ms":int((_time.time()-_t0)*1000)},"timestamp":' + str(int(_time.time() * 1000)) + '}\n')
    except Exception: pass
    # #endregion

    detected_diseases = _detected_disease_names(anomaly_result)  # list of {"name", "score"}

    # 2b. Annotate image in Cloudinary (bbox + severity) and build transformed URL
    width = upload_result.get("width") or 512
    height = upload_result.get("height") or 512
    annotations = diseases_to_annotations(detected_diseases, image_width=width, image_height=height)
    if annotations:
        add_annotation(public_id, annotations)
    
    # Use the enhanced URL with text overlay (disease | risk) and color-coded regions
    top = detected_diseases[0] if detected_diseases else {"name": "Finding", "score": 0.0}
    risk = get_risk_level(float(top.get("score", 0)))
    
    # Extract regions from anomaly result if present, otherwise build_annotated_image_url_with_text uses synthetic center
    regions = anomaly_result.get("regions", [])
    
    annotated_url = build_annotated_image_url_with_text(
        public_id, 
        regions=regions, 
        top_critical={"name": top["name"], "risk": risk},
        image_width=width,
        image_height=height
    )
    
    state["annotations"] = annotations
    state["annotated_image_url"] = annotated_url
    state["upload_result"]["url"] = annotated_url # Override primary URL for frontend
    detected_names = [d["name"] for d in detected_diseases]
    query = "chest x-ray findings " + " ".join(detected_names) if detected_names else "chest x-ray findings pneumonia opacity"

    # 3. RAG context (time-bounded)
    try:
        from concurrent.futures import ThreadPoolExecutor as _TPErag
        with _TPErag(max_workers=1) as _ex:
            _fut = _ex.submit(retrieve, query, top_k=3, detected_diseases=detected_names or None)
            rag_result = _fut.result(timeout=10)
    except Exception:
        rag_result = {"chunks": [], "citations": []}
    state["rag_context"] = rag_result
    # #region agent log
    try: open("/Applications/SpeedRay/.cursor/debug-025a2b.log", "a").write('{"sessionId":"025a2b","hypothesisId":"H1","location":"pipeline/runners.py:after_rag","message":"Step timing","data":{"step":"rag","elapsed_ms":int((_time.time()-_t0)*1000)},"timestamp":' + str(int(_time.time() * 1000)) + '}\n')
    except Exception: pass
    # #endregion

    # 4. Report (Gemini; time-bounded so pipeline cannot hang)
    try:
        from concurrent.futures import ThreadPoolExecutor as _TPEreport
        with _TPEreport(max_workers=1) as _ex:
            _fut = _ex.submit(
                generate_diagnostic_report,
                prompt=report_prompt,
                rag_context="\n".join(rag_result.get("chunks", [])),
                anomaly_summary=str(anomaly_result.get("score", 0)),
                suspected_diseases=detected_names,
            )
            report = _fut.result(timeout=45)
    except Exception as _e:
        report = {"summary": "", "findings": [], "impression": f"Report generation timed out or failed: {_e!s}"[:200]}
    state["report"] = report
    state["detected_diseases"] = detected_diseases  # name + score for each
    # #region agent log
    try: open("/Applications/SpeedRay/.cursor/debug-025a2b.log", "a").write('{"sessionId":"025a2b","hypothesisId":"H1","location":"pipeline/runners.py:after_report","message":"Step timing","data":{"step":"report","elapsed_ms":int((_time.time()-_t0)*1000)},"timestamp":' + str(int(_time.time() * 1000)) + '}\n')
    except Exception: pass
    # #endregion

    # 5. Audio from radiologist assistant spoken_explanation (same flow as assistant UI)
    top = detected_diseases[0] if detected_diseases else {"name": "Finding", "score": 0.0}
    risk = get_risk_level(float(top.get("score", 0)))
    assistant_input = {
        "filename": study_id,
        "top_critical": {"name": top["name"], "score": float(top.get("score", 0)), "risk": risk},
        "annotated_url": annotated_url,
        "diagnostic_report": {
            "explanation": report.get("summary", "") or report.get("impression", ""),
            "recommended_next_steps": report.get("recommended_next_steps", ""),
        },
        "doctor_response": "null",
    }
    assistant_res = get_radiologist_assistant_response(assistant_input)
    try:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as _ex:
            _fut = _ex.submit(text_to_speech, assistant_res["spoken_explanation"])
            audio_result = _fut.result(timeout=20)
    except Exception:
        audio_result = {"url": ""}
    state["audio_url"] = audio_result.get("url", "")
    # #region agent log
    try: open("/Applications/SpeedRay/.cursor/debug-025a2b.log", "a").write('{"sessionId":"025a2b","hypothesisId":"H1","location":"pipeline/runners.py:after_audio","message":"Step timing","data":{"step":"audio","elapsed_ms":int((_time.time()-_t0)*1000)},"timestamp":' + str(int(_time.time() * 1000)) + '}\n')
    except Exception: pass
    # #endregion

    # 6. Risk (time-bounded so pipeline cannot hang on Presage)
    try:
        from concurrent.futures import ThreadPoolExecutor as _TPE
        with _TPE(max_workers=1) as _ex:
            _fut = _ex.submit(
                get_risk_prediction,
                report.get("summary", ""),
                report.get("findings", []),
                anomaly_result.get("critical_score", anomaly_result.get("score", 0)),
            )
            risk_result = _fut.result(timeout=15)
    except Exception:
        risk_result = {"level": "Unknown", "confidence": 0.0}
    state["risk_result"] = risk_result
    # #region agent log
    try: open("/Applications/SpeedRay/.cursor/debug-025a2b.log", "a").write('{"sessionId":"025a2b","hypothesisId":"H1","location":"pipeline/runners.py:after_risk","message":"Step timing","data":{"step":"risk","elapsed_ms":int((_time.time()-_t0)*1000)},"timestamp":' + str(int(_time.time() * 1000)) + '}\n')
    except Exception: pass
    # #endregion

    # 7. Solana log (time-bounded so pipeline cannot hang)
    try:
        from concurrent.futures import ThreadPoolExecutor as _TPE2
        with _TPE2(max_workers=1) as _ex:
            _fut = _ex.submit(submit_log, run_id, study_id, {"report": report, "risk": risk_result})
            log_result = _fut.result(timeout=10)
    except Exception:
        log_result = {}
    state["log_tx_signature"] = log_result.get("signature")
    # #region agent log
    try: open("/Applications/SpeedRay/.cursor/debug-025a2b.log", "a").write('{"sessionId":"025a2b","hypothesisId":"H1","location":"pipeline/runners.py:after_log","message":"Step timing","data":{"step":"log","elapsed_ms":int((_time.time()-_t0)*1000),"total_ms":int((_time.time()-_t0)*1000)},"timestamp":' + str(int(_time.time() * 1000)) + '}\n')
    except Exception: pass
    try:
        _url = (state.get("annotated_image_url") or "")[:120]; _upload_url = (state.get("upload_result") or {}).get("url") or ""; _upload_url = _upload_url[:120] if _upload_url else ""
        open("/Applications/SpeedRay/.cursor/debug-025a2b.log", "a").write('{"sessionId":"025a2b","hypothesisId":"H2","location":"pipeline/runners.py:return","message":"Pipeline state before return","data":{"has_annotated_image_url": bool(state.get("annotated_image_url")), "total_elapsed_ms": int((_time.time()-_t0)*1000)},"timestamp":' + str(int(_time.time() * 1000)) + '}\n')
    except Exception: pass
    # #endregion
    return state
