/** Solana uneditable log write after submission for SpeedRay */

import { API_BASE } from '../config';
import type { SolanaLogResult } from './types';

export async function submitLog(
  runId: string,
  studyId: string,
  payload: Record<string, unknown>
): Promise<SolanaLogResult> {
  const res = await fetch(`${API_BASE}/log/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ run_id: runId, study_id: studyId, payload }),
  });
  if (!res.ok) return { success: false, signature: null, error: await res.text() };
  const data = await res.json();
  return {
    success: data.success ?? false,
    signature: data.signature ?? null,
    error: data.error,
  };
}
