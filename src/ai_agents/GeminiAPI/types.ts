/** Report schema and prompt types for SpeedRay GeminiAPI */

export interface ReportFinding {
  region: string;
  description: string;
  severity?: string;
  confidence?: number;
}

export interface GeminiReport {
  summary: string;
  findings: ReportFinding[];
  impression: string;
  raw?: string;
}
