/** Auth user and token types for SpeedRay */

import type { SpeedRayUser } from '../types';

export type { SpeedRayUser };

export interface Auth0Config {
  domain: string;
  clientId: string;
  authorizationParams: {
    redirect_uri: string;
    audience?: string;
    scope?: string;
  };
}

export interface UseAuthReturn {
  isAuthenticated: boolean;
  user: SpeedRayUser | null;
  isLoading: boolean;
  login: () => void;
  logout: () => void;
  getAccessToken: () => Promise<string | undefined>;
}
