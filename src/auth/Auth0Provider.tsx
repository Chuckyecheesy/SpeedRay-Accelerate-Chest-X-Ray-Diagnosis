/** Auth0 React provider wrapper for SpeedRay */

import { Auth0Provider as Auth0ProviderBase } from '@auth0/auth0-react';
import { getEnv } from '../config';

const domain = getEnv('VITE_AUTH0_DOMAIN') ?? '';
const clientId = getEnv('VITE_AUTH0_CLIENT_ID') ?? '';
const audience = getEnv('VITE_AUTH0_AUDIENCE');
const callbackUrl = getEnv('VITE_AUTH0_CALLBACK_URL');

export const IS_AUTH0_CONFIG_DONE = !!(domain && clientId);

export function Auth0Provider({ children }: { children: React.ReactNode }) {
  if (!domain || !clientId) {
    return <>{children}</>;
  }

  const redirectUri = (typeof window !== 'undefined' && callbackUrl)
    ? callbackUrl
    : (typeof window !== 'undefined' ? window.location.origin + '/callback' : '');

  return (
    <Auth0ProviderBase
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: redirectUri,
        audience: audience ?? undefined,
        scope: 'openid profile email',
      }}
    >
      {children}
    </Auth0ProviderBase>
  );
}
