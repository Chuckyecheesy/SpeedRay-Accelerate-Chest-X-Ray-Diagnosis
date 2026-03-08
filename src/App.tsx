/** Top-level routes and layout for SpeedRay */

import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Auth0Provider } from './auth';
import { WalletProvider } from './wallet';
import { ROUTES, API_BASE } from './config';
import AuthPage from './frontend/AuthPage';
import AuthCallbackPage from './frontend/AuthCallbackPage';
import { DemoPage } from './frontend/DemoPage';

/** Wrap only demo/dashboard with Solana wallet so auth page never hits RPC (avoids "Connection Failed" on login). */
function DemoWithWallet() {
  return (
    <WalletProvider>
      <DemoPage />
    </WalletProvider>
  );
}

function AppContent() {
  return (
    <Routes>
      <Route path={ROUTES.HOME} element={<AuthPage />} />
      <Route path={ROUTES.CALLBACK} element={<AuthCallbackPage />} />
      <Route path={ROUTES.DEMO} element={<DemoWithWallet />} />
      <Route path={ROUTES.DASHBOARD} element={<WalletProvider><div>Dashboard (SpeedRay)</div></WalletProvider>} />
      <Route path="*" element={<Navigate to={ROUTES.HOME} replace />} />
    </Routes>
  );
}

export default function App() {
  useEffect(() => {
    // Heartbeat to prevent Vultr instance from shutting down while frontend is open
    const interval = setInterval(() => {
      fetch(`${API_BASE}/ping`).catch(() => {});
    }, 60000); // every 60 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <BrowserRouter>
      <Auth0Provider>
        <AppContent />
      </Auth0Provider>
    </BrowserRouter>
  );
}
