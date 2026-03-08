/** Backboard.io pipeline definition and run for SpeedRay */

import type { PipelineRunState } from './types';
import {
  uploadAndAnnotate,
  runAnomalyDetectionStep,
  fetchRAGContextStep,
  generateReportStep,
  generateAudioStep,
  runRiskPredictionStep,
  submitLogStep,
} from './steps';

const STEP_ORDER = [
  'uploadAndAnnotate',
  'runAnomalyDetection',
  'fetchRAGContext',
  'generateReport',
  'generateAudio',
  'runRiskPrediction',
  'submitLog',
] as const;

export interface RunPipelineOptions {
  runId: string;
  studyId: string;
  file: File;
  onStateChange?: (state: PipelineRunState) => void;
}

export async function runPipeline(
  options: RunPipelineOptions
): Promise<PipelineRunState> {
  const { runId, studyId, file, onStateChange } = options;
  const now = new Date().toISOString();
  let state: PipelineRunState = {
    runId,
    studyId,
    status: 'running',
    startedAt: now,
    updatedAt: now,
  };

  const update = (partial: Partial<PipelineRunState>) => {
    state = { ...state, ...partial };
    onStateChange?.(state);
  };

  try {
    let imageUrl = '';
    if (!file) {
      state.currentStep = 'uploadAndAnnotate';
      update(await uploadAndAnnotate(state, file));
      imageUrl = state.uploadResult?.url ?? '';
    }

    state.currentStep = 'runAnomalyDetection';
    update(await runAnomalyDetectionStep(state, imageUrl, file));

    const backendAlreadyDone = !!state.report;

    if (!backendAlreadyDone) {
      state.currentStep = 'fetchRAGContext';
      update(await fetchRAGContextStep(state));

      state.currentStep = 'generateReport';
      update(await generateReportStep(state));

      state.currentStep = 'generateAudio';
      update(await generateAudioStep(state));

      state.currentStep = 'runRiskPrediction';
      update(await runRiskPredictionStep(state));

      state.currentStep = 'submitLog';
      update(await submitLogStep(state));
    }

    update({ status: 'completed', currentStep: undefined });
  } catch (err) {
    update({
      status: 'failed',
      error: err instanceof Error ? err.message : String(err),
    });
  }

  return state;
}
