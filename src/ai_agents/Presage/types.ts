/** Risk score and factor types for SpeedRay Presage */

export interface RiskResult {
  level: string;
  confidence: number;
  factors?: string[];
  error?: string;
}
