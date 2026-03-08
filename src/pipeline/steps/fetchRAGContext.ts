/** RAG (Kaggle/NHI) context fetch step for SpeedRay pipeline */

import { fetchRAGContext } from '../../ai_agents/RAG';
import { RAG_QUERY_PREFIX } from '../../prompts';
import type { PipelineRunState } from '../types';

export async function fetchRAGContextStep(
  state: PipelineRunState
): Promise<Partial<PipelineRunState>> {
  const diseases = state.anomalyResult?.diseases;
  const query =
    diseases?.length ?
      `${RAG_QUERY_PREFIX} ${diseases.map((d) => d.name).join(' ')}` :
      RAG_QUERY_PREFIX;
  const context = await fetchRAGContext(query, 5, diseases);
  return {
    ragContext: { chunks: context.chunks, citations: context.citations },
    updatedAt: new Date().toISOString(),
  };
}
