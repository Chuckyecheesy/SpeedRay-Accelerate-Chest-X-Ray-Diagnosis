/** Top-level routes and layout for SpeedRay */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Auth0Provider } from './auth';
import { WalletProvider } from './wallet';
import { ROUTES } from './config';
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
  return (
    <BrowserRouter>
      <Auth0Provider>
        <AppContent />
      </Auth0Provider>
    </BrowserRouter>
  );
}
