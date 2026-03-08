/** Cloudinary upload + annotation step for SpeedRay pipeline */

import { uploadImage } from '../../storage';
import type { PipelineRunState } from '../types';

export async function uploadAndAnnotate(
  state: PipelineRunState,
  file: File
): Promise<Partial<PipelineRunState>> {
  const result = await uploadImage(file);
  return {
    uploadResult: { publicId: result.public_id, url: result.secure_url ?? result.url },
    updatedAt: new Date().toISOString(),
  };
}
