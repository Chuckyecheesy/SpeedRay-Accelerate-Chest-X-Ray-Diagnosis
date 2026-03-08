/** Text-to-speech for explanation in SpeedRay via backend */

import { API_BASE } from '../../config';
import type { AudioResult } from './types';

export async function textToSpeech(text: string): Promise<AudioResult> {
  const res = await fetch(`${API_BASE}/audio/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) return { url: '', error: await res.text() };
  const data = await res.json();
  return { url: data.url ?? '', error: data.error ?? null };
}
