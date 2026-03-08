/** Cloudinary image upload, annotation, metadata for SpeedRay */

import { API_BASE } from '../config';
import type { CloudinaryUploadResult } from './types';

export async function uploadImage(
  file: File,
  folder: string = 'speedray'
): Promise<CloudinaryUploadResult> {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_BASE}/upload/image`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return {
    url: data.url ?? '',
    secure_url: data.secure_url,
    public_id: data.public_id ?? '',
    width: data.width,
    height: data.height,
  };
}

export async function getMetadata(publicId: string): Promise<Record<string, unknown>> {
  const res = await fetch(
    `${API_BASE}/upload/metadata?public_id=${encodeURIComponent(publicId)}`
  );
  if (!res.ok) return {};
  return res.json();
}
