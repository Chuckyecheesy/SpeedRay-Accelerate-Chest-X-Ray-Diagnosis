/** Risk prediction API client for SpeedRay (via backend) */

import { API_BASE } from '../../config';
import type { RiskResult } from './types';

export async function getRiskPrediction(
  reportSummary: string,
  findings: unknown[],
  anomalyScore: number
): Promise<RiskResult> {
  const res = await fetch(`${API_BASE}/risk/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      report_summary: reportSummary,
      findings: findings,
      anomaly_score: anomalyScore,
    }),
  });
  if (!res.ok) return { level: 'error', confidence: 0, error: await res.text() };
  const data = await res.json();
  return {
    level: data.level ?? 'unknown',
    confidence: data.confidence ?? 0,
    factors: data.factors,
  };
}
