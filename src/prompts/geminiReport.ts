/** Gemini deterministic diagnostic report prompt for SpeedRay */

export const GEMINI_REPORT_SYSTEM = `You are a radiology assistant for SpeedRay. Output a structured chest X-ray diagnostic report. Be concise and deterministic.`;

export const GEMINI_REPORT_USER = `Generate a structured chest X-ray diagnostic report.

Context from reference datasets:
{{ragContext}}

Anomaly detection summary:
{{anomalySummary}}

Include:
1) Brief summary (1-2 sentences)
2) Findings by region (list)
3) Impression (conclusion)`;

export function buildReportPrompt(vars: {
  ragContext?: string;
  anomalySummary?: string;
}): string {
  return GEMINI_REPORT_USER.replace('{{ragContext}}', vars.ragContext ?? '')
    .replace('{{anomalySummary}}', vars.anomalySummary ?? '');
}
