import { useAuth0 } from '@auth0/auth0-react';
import { useState } from 'react';
import { getEnv } from '../config';
import { IS_AUTH0_CONFIG_DONE } from './Auth0Provider';
import type { UseAuthReturn } from './types';

export function useAuth(): UseAuthReturn {
  if (!IS_AUTH0_CONFIG_DONE) {
    return useMockAuth();
  }
  return useRealAuth();
}

function useRealAuth(): UseAuthReturn {
  const {
    isAuthenticated,
    user,
    isLoading,
    loginWithRedirect,
    logout: auth0Logout,
    getAccessTokenSilently,
  } = useAuth0();

  const login = () => loginWithRedirect();
  const logoutUrl = getEnv('VITE_AUTH0_LOGOUT_URL') ?? (typeof window !== 'undefined' ? window.location.origin : '');
  const logout = () => auth0Logout({ logoutParams: { returnTo: logoutUrl } });
  const getAccessToken = async () => {
    try {
      return await getAccessTokenSilently();
    } catch {
      return undefined;
    }
  };

  return {
    isAuthenticated: !!isAuthenticated,
    user: user ? {
      sub: user.sub || '',
      email: user.email,
      name: user.name,
      picture: user.picture,
      email_verified: user.email_verified,
    } : null,
    isLoading,
    login,
    logout,
    getAccessToken,
  };
}

function useMockAuth(): UseAuthReturn {
  const [auth, setAuth] = useState(false);
  
  return {
    isAuthenticated: auth,
    user: auth ? {
      sub: 'mock_123',
      email: 'doctor@speedray.ai',
      name: 'Dr. Mockingbird',
      picture: '',
      email_verified: true,
    } : null,
    isLoading: false,
    login: () => setAuth(true),
    logout: () => setAuth(false),
    getAccessToken: async () => 'mock_token',
  };
}
