/** Re-exports prompts for SpeedRay */

export {
  GEMINI_REPORT_SYSTEM,
  GEMINI_REPORT_USER,
  buildReportPrompt,
} from './geminiReport';
export { RAG_SYSTEM_PROMPT, RAG_QUERY_PREFIX } from './ragSystem';
export type { PromptVariables } from './types';
