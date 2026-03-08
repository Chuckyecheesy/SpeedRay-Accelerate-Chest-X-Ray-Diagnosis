/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE?: string;
  readonly VITE_AUTH0_DOMAIN?: string;
  readonly VITE_AUTH0_CLIENT_ID?: string;
  readonly VITE_AUTH0_AUDIENCE?: string;
  readonly VITE_CLOUDINARY_CLOUD_NAME?: string;
  readonly VITE_SOLANA_RPC_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
