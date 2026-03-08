/** Auth0 user and session types for SpeedRay */

export interface SpeedRayUser {
  sub: string;
  email?: string;
  name?: string;
  picture?: string;
  email_verified?: boolean;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: SpeedRayUser | null;
  isLoading: boolean;
  error?: Error;
}

export interface AuthTokens {
  accessToken: string;
  idToken?: string;
  expiresAt?: number;
}
