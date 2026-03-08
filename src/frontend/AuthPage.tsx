import React from 'react';
import { useAuth } from '../auth/useAuth';
import { ROUTES } from '../config';
import { useNavigate } from 'react-router-dom';

export default function AuthPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  React.useEffect(() => {
    if (isAuthenticated) {
      navigate(ROUTES.DEMO);
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="auth-page animate-fade-in">
      <div className="bg-blur-circle" style={{ top: '-10%', left: '-10%' }}></div>
      <div className="bg-blur-circle" style={{ bottom: '-10%', right: '-10%', background: 'radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%)' }}></div>
      
      <div className="glass auth-card">
        <h1 style={{ fontSize: '3.5rem', marginBottom: '0.5rem', background: 'var(--gradient-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          SpeedRay
        </h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2.5rem', fontSize: '1.2rem' }}>
          AI-Powered Precision in Chest Radiography
        </p>
        
        <div style={{ marginBottom: '2rem' }}>
          <div className="glass" style={{ padding: '1.5rem', marginBottom: '1.5rem', textAlign: 'left', fontSize: '0.95rem' }}>
            <p style={{ marginBottom: '0.8rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center' }}>
              <span style={{ color: 'var(--accent-blue)', marginRight: '10px' }}>✦</span> Automated Anomaly Detection
            </p>
            <p style={{ marginBottom: '0.8rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center' }}>
              <span style={{ color: 'var(--accent-purple)', marginRight: '10px' }}>✦</span> RAG-Enhanced Medical Reasoning
            </p>
            <p style={{ color: 'var(--text-primary)', display: 'flex', alignItems: 'center' }}>
              <span style={{ color: 'var(--accent-blue)', marginRight: '10px' }}>✦</span> Secure Solana Verification
            </p>
          </div>
        </div>

        <button 
          className="btn-primary" 
          style={{ width: '100%', fontSize: '1.2rem', padding: '18px', borderRadius: '14px' }}
          onClick={() => login()}
        >
          Sign In as Professional
        </button>
        
        <p style={{ marginTop: '2rem', fontSize: '0.85rem', color: 'var(--text-secondary)', opacity: 0.7 }}>
          By signing in, you agree to our terms for medical diagnostic assistance.
        </p>
      </div>
    </div>
  );
}
