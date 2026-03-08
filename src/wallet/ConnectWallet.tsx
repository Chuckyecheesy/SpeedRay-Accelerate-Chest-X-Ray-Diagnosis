/**
 * Connect / disconnect Solana wallet button for SpeedRay.
 * Uses the wallet adapter modal to select Phantom, Solflare, etc.
 */

import { useRef } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';

export function ConnectWallet() {
  const { publicKey, connected } = useWallet();
  const buttonRef = useRef<HTMLDivElement>(null);

  return (
    <div ref={buttonRef} className="wallet-adapter-wrap">
      <WalletMultiButton
        className="speedray-wallet-button"
        style={{
          background: 'var(--gradient-primary)',
          color: 'white',
          border: 'none',
          padding: '0.5rem 1rem',
          borderRadius: '12px',
          fontWeight: 600,
          cursor: 'pointer',
        }}
      />
      {connected && publicKey && (
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginLeft: '0.5rem' }}>
          {publicKey.toBase58().slice(0, 4)}…{publicKey.toBase58().slice(-4)}
        </span>
      )}
    </div>
  );
}
