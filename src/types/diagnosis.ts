/** Diagnosis result, report, and RAG types for SpeedRay */

export interface Finding {
  region: string;
  description: string;
  severity?: 'normal' | 'mild' | 'moderate' | 'severe';
  confidence?: number;
}

export interface DiagnosticReport {
  id: string;
  studyId: string;
  summary: string;
  findings: Finding[];
  impression: string;
  recommendations?: string[];
  generatedAt: string;
  modelVersion?: string;
}

export interface RAGCitation {
  source: string;
  snippet: string;
  score?: number;
}

export interface RAGContext {
  query: string;
  chunks: string[];
  citations: RAGCitation[];
}
