/** Auth0 redirect callback — show loading while SDK processes code, then redirect */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { ROUTES } from '../config';

export default function AuthCallbackPage() {
  const { isAuthenticated, isLoading, error } = useAuth0();
  const navigate = useNavigate();

  React.useEffect(() => {
    if (error) {
      navigate(ROUTES.HOME, { replace: true, state: { authError: error.message } });
      return;
    }
    if (!isLoading && isAuthenticated) {
      navigate(ROUTES.DEMO, { replace: true });
    }
  }, [isAuthenticated, isLoading, error, navigate]);

  if (error) {
    return (
      <div className="auth-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Sign-in failed. Redirecting…</p>
      </div>
    );
  }

  return (
    <div className="auth-page" style={{ padding: '2rem', textAlign: 'center' }}>
      <p style={{ color: 'var(--text-secondary)' }}>Completing sign in…</p>
    </div>
  );
}
