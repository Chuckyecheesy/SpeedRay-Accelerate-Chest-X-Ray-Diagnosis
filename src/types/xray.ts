/** X-ray image, study, and viewer types for SpeedRay */

export interface XRayImage {
  id: string;
  url: string;
  publicId?: string;
  width: number;
  height: number;
  metadata?: Record<string, unknown>;
}

export interface XRayStudy {
  id: string;
  patientId?: string;
  images: XRayImage[];
  createdAt: string;
  updatedAt: string;
}

export interface Viewport {
  zoom: number;
  panX: number;
  panY: number;
  windowCenter: number;
  windowWidth: number;
}

export type ViewportAction = 'zoomIn' | 'zoomOut' | 'pan' | 'reset' | 'windowLevel';
