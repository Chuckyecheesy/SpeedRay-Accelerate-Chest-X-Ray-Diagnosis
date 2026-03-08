/** Anomaly score and region types for SpeedRay TorchXRayModel */

export interface AnomalyRegion {
  x: number;
  y: number;
  width: number;
  height: number;
  score: number;
  label?: string;
}

export interface DiseaseScore {
  name: string;
  score: number;
}

export interface TopCritical {
  name: string;
  score: number;
}

/** Backend POST /pipeline/run full response (so frontend can skip redundant steps). */
export interface FullPipelineResponse {
  run_id?: string;
  study_id?: string;
  upload_result?: { url?: string; public_id?: string; secure_url?: string };
  anomaly_result?: { score?: number; regions?: unknown[]; diseases?: DiseaseScore[]; top_critical?: TopCritical };
  rag_context?: { chunks?: string[]; citations?: unknown[] };
  report?: { summary?: string; findings?: unknown[]; impression?: string };
  annotated_image_url?: string;
  audio_url?: string;
  risk_result?: { level?: string; confidence?: number };
  log_tx_signature?: string;
}

export interface AnomalyResult {
  score: number;
  regions: AnomalyRegion[];
  model_loaded?: boolean;
  error?: string;
  diseases?: DiseaseScore[];
  /** Single highest critical finding (from backend top_critical or detected). */
  top_critical?: TopCritical;
  annotated_url?: string;
  /** When present, backend already ran full pipeline; use this to skip RAG/report/audio/risk/log steps. */
  fullPipeline?: FullPipelineResponse;
}
