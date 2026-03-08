/** Env var parsing and validation for SpeedRay */

const env = {
  VITE_API_BASE: import.meta.env.VITE_API_BASE,
  VITE_AUTH0_DOMAIN: import.meta.env.VITE_AUTH0_DOMAIN,
  VITE_AUTH0_CLIENT_ID: import.meta.env.VITE_AUTH0_CLIENT_ID,
  VITE_AUTH0_AUDIENCE: import.meta.env.VITE_AUTH0_AUDIENCE,
  VITE_AUTH0_CALLBACK_URL: import.meta.env.VITE_AUTH0_CALLBACK_URL,
  VITE_AUTH0_LOGOUT_URL: import.meta.env.VITE_AUTH0_LOGOUT_URL,
  VITE_AUTH0_WEB_ORIGIN: import.meta.env.VITE_AUTH0_WEB_ORIGIN,
  VITE_CLOUDINARY_CLOUD_NAME: import.meta.env.VITE_CLOUDINARY_CLOUD_NAME,
} as const;

export function getEnv<K extends keyof typeof env>(key: K): (typeof env)[K] {
  return env[key];
}

export function requireEnv<K extends keyof typeof env>(key: K): NonNullable<(typeof env)[K]> {
  const value = env[key];
  if (value == null || value === '') {
    throw new Error(`SpeedRay: missing required env ${key}`);
  }
  return value as NonNullable<(typeof env)[K]>;
}

export default env;
