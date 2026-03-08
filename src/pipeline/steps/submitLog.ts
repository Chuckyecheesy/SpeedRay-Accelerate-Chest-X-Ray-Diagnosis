/** Solana uneditable log submission step for SpeedRay pipeline */

import { submitLog } from '../../storage';
import type { PipelineRunState } from '../types';

export async function submitLogStep(
  state: PipelineRunState
): Promise<Partial<PipelineRunState>> {
  const result = await submitLog(state.runId, state.studyId, {
    report: state.report,
    risk: state.riskResult,
    anomalyScore: state.anomalyResult?.score,
  });
  return {
    logTxSignature: result.signature ?? undefined,
    updatedAt: new Date().toISOString(),
  };
}
