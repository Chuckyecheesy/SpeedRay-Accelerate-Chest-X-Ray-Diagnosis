/** App-wide constants and SpeedRay namespace */

export const SPEEDRAY_NAMESPACE = 'SpeedRay';

export const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';

export const ROUTES = {
  HOME: '/',
  DEMO: '/demo',
  LOGIN: '/login',
  CALLBACK: '/callback',
  DASHBOARD: '/dashboard',
} as const;

export const PIPELINE_STEPS = [
  'uploadAndAnnotate',
  'runAnomalyDetection',
  'fetchRAGContext',
  'generateReport',
  'generateAudio',
  'runRiskPrediction',
  'submitLog',
] as const;
