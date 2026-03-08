/** Gemini report generation step for SpeedRay pipeline */

import { generateReport } from '../../ai_agents/GeminiAPI';

import type { PipelineRunState } from '../types';

const REPORT_CONFIDENCE_THRESHOLD = 0.5;

export async function generateReportStep(
  state: PipelineRunState
): Promise<Partial<PipelineRunState>> {
  const ragChunks = state.ragContext?.chunks ?? [];
  const anomalyScore = state.anomalyResult?.score ?? 0;
  const diseases = state.anomalyResult?.diseases ?? [];
  const suspectedDiseases = diseases
    .filter((d) => d.score >= REPORT_CONFIDENCE_THRESHOLD)
    .map((d) => d.name);
  // Prompt building happens implicitly in generateReport via system prompts now, 
  // or is handled there. We pass ragChunks and anomalySummary directly.
  const report = await generateReport(
    state.runId,
    ragChunks.join('\n'),
    String(anomalyScore),
    suspectedDiseases.length ? suspectedDiseases : undefined
  );
  return {
    report: {
      summary: report.summary,
      findings: report.findings,
      impression: report.impression,
    },
    updatedAt: new Date().toISOString(),
  };
}
