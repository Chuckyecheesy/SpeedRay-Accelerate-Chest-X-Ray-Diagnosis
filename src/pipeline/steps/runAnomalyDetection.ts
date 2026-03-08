/** TorchXRayModel anomaly detection step for SpeedRay pipeline */

import { runAnomalyDetection } from '../../ai_agents/TorchXRayModel';
import type { PipelineRunState } from '../types';

export async function runAnomalyDetectionStep(
  state: PipelineRunState,
  imageUrl: string,
  imageFile?: File
): Promise<Partial<PipelineRunState>> {
  const result = await runAnomalyDetection(imageUrl, imageFile);
  const fp = result.fullPipeline;
  const ur = fp?.upload_result;
  const annotatedUrl =
    result.annotated_url ||
    fp?.annotated_image_url ||
    ur?.url ||
    ur?.secure_url ||
    '';

  const partial: Partial<PipelineRunState> = {
    anomalyResult: {
      score: result.score,
      regions: result.regions,
      diseases: result.diseases ?? [],
      top_critical: result.top_critical,
    },
    uploadResult:
      annotatedUrl || ur
        ? {
            publicId: state.uploadResult?.publicId || ur?.public_id || '',
            url: annotatedUrl || ur?.url || ur?.secure_url || '',
          }
        : state.uploadResult,
    updatedAt: new Date().toISOString(),
  };

  if (fp?.report) {
    partial.report = {
      summary: fp.report.summary ?? '',
      findings: Array.isArray(fp.report.findings) ? fp.report.findings : [],
      impression: fp.report.impression ?? '',
    };
  }
  if (fp?.rag_context) {
    partial.ragContext = {
      chunks: Array.isArray(fp.rag_context.chunks) ? fp.rag_context.chunks : [],
      citations: Array.isArray(fp.rag_context.citations) ? fp.rag_context.citations : [],
    };
  }
  if (fp?.audio_url) partial.audioUrl = fp.audio_url;
  if (fp?.risk_result) {
    partial.riskResult = {
      level: fp.risk_result.level ?? 'Unknown',
      confidence: fp.risk_result.confidence ?? 0,
    };
  }
  if (fp?.log_tx_signature) partial.logTxSignature = fp.log_tx_signature;

  return partial;
}
