/** Storage response and log types for SpeedRay */

export interface CloudinaryUploadResult {
  url: string;
  secure_url?: string;
  public_id: string;
  width?: number;
  height?: number;
}

export interface SolanaLogResult {
  success: boolean;
  signature: string | null;
  error?: string;
}
