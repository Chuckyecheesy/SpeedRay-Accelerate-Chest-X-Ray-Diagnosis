/** ElevenLabs audio generation step for SpeedRay pipeline */

import { textToSpeech } from '../../ai_agents/ElevenLabs';
import type { PipelineRunState } from '../types';

export async function generateAudioStep(
  state: PipelineRunState
): Promise<Partial<PipelineRunState>> {
  const text =
    state.report?.impression ?? state.report?.summary ?? 'No report available.';
  const result = await textToSpeech(text);
  return {
    audioUrl: result.url || undefined,
    updatedAt: new Date().toISOString(),
  };
}
