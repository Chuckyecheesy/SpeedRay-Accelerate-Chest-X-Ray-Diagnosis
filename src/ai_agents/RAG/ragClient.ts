/** NoSQL RAG query client for SpeedRay (via backend) */

import { API_BASE } from '../../config';
import type { RAGContext } from './types';

const DEFAULT_CONFIDENCE_THRESHOLD = 0.5;

export async function fetchRAGContext(
  query: string,
  topK: number = 5,
  detectedDiseases?: { name: string; score: number }[]
): Promise<RAGContext> {
  const diseases =
    detectedDiseases?.filter((d) => d.score >= DEFAULT_CONFIDENCE_THRESHOLD).map((d) => d.name) ?? [];
  const params = new URLSearchParams({
    query: query,
    top_k: String(topK),
  });
  if (diseases.length) params.set('diseases', diseases.join(','));
  const res = await fetch(`${API_BASE}/rag/retrieve?${params.toString()}`);
  if (!res.ok) return { query, chunks: [], citations: [] };
  const data = await res.json();
  return {
    query: data.query ?? query,
    chunks: data.chunks ?? [],
    citations: data.citations ?? [],
  };
}
