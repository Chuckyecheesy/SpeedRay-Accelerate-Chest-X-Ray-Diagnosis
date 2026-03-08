/** Pipeline run state and step I/O types for SpeedRay */

export interface PipelineRunState {
  runId: string;
  studyId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  currentStep?: string;
  uploadResult?: { publicId: string; url: string };
  anomalyResult?: {
    score: number;
    regions: unknown[];
    diseases?: { name: string; score: number }[];
    top_critical?: { name: string; score: number };
  };
  ragContext?: { chunks: string[]; citations: unknown[] };
  report?: { summary: string; findings: unknown[]; impression: string };
  audioUrl?: string;
  riskResult?: { level: string; confidence: number };
  logTxSignature?: string;
  error?: string;
  startedAt: string;
  updatedAt: string;
}

export type PipelineStepName =
  | 'uploadAndAnnotate'
  | 'runAnomalyDetection'
  | 'fetchRAGContext'
  | 'generateReport'
  | 'generateAudio'
  | 'runRiskPrediction'
  | 'submitLog';
