/** API client to call Torch XRay backend for SpeedRay anomaly detection */

import { API_BASE } from '../../config';
import type { AnomalyResult, FullPipelineResponse } from './types';

export async function runAnomalyDetection(
  imageUrl: string,
  imageFile?: File
): Promise<AnomalyResult> {
  if (imageFile) {
    const form = new FormData();
    form.append('file', imageFile);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 180000); // 3 min
    const tStart = Date.now();
    // #region agent log
    fetch('http://127.0.0.1:7258/ingest/1a4b0efb-f996-45bb-bf9d-737f2bd4387e',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'025a2b'},body:JSON.stringify({sessionId:'025a2b',hypothesisId:'H1',location:'TorchXRayModel/client.ts:fetch_start',message:'Pipeline request started',data:{request_start_ms:tStart},timestamp:tStart})}).catch(()=>{});
    // #endregion
    let res: Response;
    try {
      res = await fetch(`${API_BASE}/pipeline/run`, {
        method: 'POST',
        body: form,
        signal: controller.signal,
      });
    } catch (e) {
      const tEnd = Date.now();
      fetch('http://127.0.0.1:7258/ingest/1a4b0efb-f996-45bb-bf9d-737f2bd4387e',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'025a2b'},body:JSON.stringify({sessionId:'025a2b',hypothesisId:'H1',location:'TorchXRayModel/client.ts:fetch_error',message:'Pipeline request failed',data:{duration_ms:tEnd-tStart,error:(e instanceof Error ? e.message : String(e)).slice(0,80)},timestamp:tEnd})}).catch(()=>{});
      clearTimeout(timeoutId);
      throw e;
    }
    clearTimeout(timeoutId);
    const tEnd = Date.now();
    // #region agent log
    fetch('http://127.0.0.1:7258/ingest/1a4b0efb-f996-45bb-bf9d-737f2bd4387e',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'025a2b'},body:JSON.stringify({sessionId:'025a2b',hypothesisId:'H1',location:'TorchXRayModel/client.ts:fetch_end',message:'Pipeline request ended',data:{duration_ms:tEnd-tStart,ok:res.ok},timestamp:tEnd})}).catch(()=>{});
    // #endregion
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    const ar = data?.anomaly_result ?? {};
    const detected = data?.detected_diseases;
    const topCritical = ar.top_critical ?? (Array.isArray(detected) && detected[0] ? { name: detected[0].name, score: detected[0].score } : undefined);
    const ur = data.upload_result;
    const annotatedUrl = data.annotated_image_url || ur?.url || ur?.secure_url;
    // #region agent log
    fetch('http://127.0.0.1:7258/ingest/1a4b0efb-f996-45bb-bf9d-737f2bd4387e',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'025a2b'},body:JSON.stringify({sessionId:'025a2b',hypothesisId:'H3',location:'TorchXRayModel/client.ts:runAnomalyDetection',message:'Pipeline run response',data:{has_annotated_image_url:!!data.annotated_image_url,has_upload_result_url:!!data.upload_result?.url,annotated_url_preview:(annotatedUrl||'').slice(0,80)},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    return {
      score: ar.score ?? 0,
      regions: ar.regions ?? [],
      model_loaded: ar.model_loaded,
      diseases: ar.diseases ?? [],
      top_critical: topCritical,
      annotated_url: annotatedUrl,
      fullPipeline: data as FullPipelineResponse,
    };
  }
  const res = await fetch(
    `${API_BASE}/ai/anomaly?url=${encodeURIComponent(imageUrl)}`
  );
  if (!res.ok) return { score: 0, regions: [], diseases: [] };
  const json = await res.json();
  const detected = json?.detected;
  const topCritical = json?.top_critical ?? (Array.isArray(detected) && detected[0] ? { name: detected[0].name, score: detected[0].score } : undefined);
  return { 
    ...json, 
    top_critical: topCritical ?? json.top_critical,
    annotated_url: json.annotated_image_url || imageUrl
  };
}
