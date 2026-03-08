/** Gemini API calls for report generation in SpeedRay (via backend) */

import { API_BASE } from '../../config';
import type { GeminiReport } from './types';

export async function generateReport(
  runId: string,
  ragContext: string,
  anomalySummary: string,
  suspectedDiseases?: string[]
): Promise<GeminiReport> {
  const res = await fetch(`${API_BASE}/report/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      run_id: runId,
      rag_context: ragContext,
      anomaly_summary: anomalySummary,
      suspected_diseases: suspectedDiseases ?? [],
    }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return {
    summary: data.summary ?? '',
    findings: data.findings ?? [],
    impression: data.impression ?? '',
    raw: data.raw,
  };
}

export async function getReport(runId: string): Promise<GeminiReport> {
  const res = await fetch(`${API_BASE}/report/${runId}`);
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return {
    summary: data.summary ?? '',
    findings: data.findings ?? [],
    impression: data.impression ?? '',
  };
}
