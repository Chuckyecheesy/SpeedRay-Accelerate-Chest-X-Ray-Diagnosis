/** RAG context and citation types for SpeedRay */

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
