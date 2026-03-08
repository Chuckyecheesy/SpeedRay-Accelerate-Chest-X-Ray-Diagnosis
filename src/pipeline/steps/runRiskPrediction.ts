/** Presage risk prediction step for SpeedRay pipeline */

import { getRiskPrediction } from '../../ai_agents/Presage';
import type { PipelineRunState } from '../types';

export async function runRiskPredictionStep(
  state: PipelineRunState
): Promise<Partial<PipelineRunState>> {
  const report = state.report;
  const summary = report?.summary ?? '';
  const findings = report?.findings ?? [];
  const anomalyScore = state.anomalyResult?.score ?? 0;
  const risk = await getRiskPrediction(summary, findings, anomalyScore);
  return {
    riskResult: { level: risk.level, confidence: risk.confidence },
    updatedAt: new Date().toISOString(),
  };
}
