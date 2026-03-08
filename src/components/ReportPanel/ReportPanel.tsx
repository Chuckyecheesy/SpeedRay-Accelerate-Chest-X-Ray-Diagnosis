import React, { useEffect, useRef } from 'react';
import type { Finding } from '../../types';

export interface ReportPanelProps {
  summary?: string;
  findings?: Finding[];
  impression?: string;
  isLoading?: boolean;
  className?: string;
  studyId?: string;
  patientName?: string;
}

const editableBlockStyle: React.CSSProperties = {
  outline: 'none',
  cursor: 'text',
  minHeight: '1.2em',
};
const editableBlockFocusStyle = {
  ...editableBlockStyle,
  boxShadow: '0 0 0 1px rgba(0,0,0,0.1)',
  borderRadius: '2px',
};

export function ReportPanel({
  summary = '',
  findings = [],
  impression = '',
  isLoading = false,
  className,
  studyId = 'N/A',
  patientName = 'ANONYMOUS',
}: ReportPanelProps) {
  const summaryRef = useRef<HTMLParagraphElement>(null);
  const impressionRef = useRef<HTMLParagraphElement>(null);
  const findingRefs = useRef<(HTMLParagraphElement | HTMLDivElement | null)[]>([]);

  // Sync editable blocks from props when report changes (e.g. new pipeline result)
  useEffect(() => {
    if (summaryRef.current) summaryRef.current.innerText = summary;
  }, [summary]);
  useEffect(() => {
    if (impressionRef.current) impressionRef.current.innerText = impression;
  }, [impression]);
  useEffect(() => {
    findingRefs.current = findingRefs.current.slice(0, findings.length);
    findings.forEach((f, i) => {
      const r = findingRefs.current[i];
      if (!r) return;
      const desc = f.description + (f.severity ? ` [${f.severity.toUpperCase()}]` : '');
      r.innerText = desc;
    });
  }, [findings]);

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        background: '#fff',
        borderRadius: '8px',
        padding: '2rem',
        gap: '1rem',
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '3px solid #eee',
          borderTopColor: '#2563eb',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }} />
        <p style={{ color: '#333', fontWeight: 500 }}>Generating medical report...</p>
        <p style={{ color: '#666', fontSize: '0.875rem' }}>Generating report… Results usually ready in seconds.</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div className={className} style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      background: '#fff', 
      color: '#1a1a1a',
      padding: '1.5rem',
      borderRadius: '4px',
      boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
      fontFamily: '"Inter", serif',
      minHeight: '100%',
      minWidth: 'max(100%, 620px)',
      boxSizing: 'border-box',
      overflowWrap: 'break-word',
      wordBreak: 'break-word',
      position: 'relative'
    }}>
      {/* Paper Header */}
      <div style={{ 
        borderBottom: '2px solid #1a1a1a', 
        paddingBottom: '0.75rem', 
        marginBottom: '1rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-end'
      }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, letterSpacing: '-0.03em', color: '#000' }}>SPEEDRAY MEDICAL</h2>
          <p style={{ margin: 0, fontSize: '0.65rem', color: '#666', fontWeight: 600 }}>RADIOLOGY DEPARTMENT | AI-ASSISTED ANALYSIS</p>
        </div>
        <div style={{ textAlign: 'right', fontSize: '0.65rem', fontWeight: 500 }}>
          <p style={{ margin: 0 }}>STUDY ID: <span style={{ fontWeight: 700 }}>{studyId}</span></p>
          <p style={{ margin: 0 }}>PATIENT: <span style={{ fontWeight: 700 }}>{patientName}</span></p>
          <p style={{ margin: 0 }}>DATE: {new Date().toLocaleDateString()}</p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {summary && (
          <section>
            <h4 style={{ color: '#000', textTransform: 'uppercase', fontSize: '0.65rem', fontWeight: 800, letterSpacing: '0.05em', marginBottom: '0.4rem', borderBottom: '1px solid #eee', paddingBottom: '0.15rem' }}>Clinical Summary</h4>
            <p
              ref={summaryRef}
              contentEditable
              suppressContentEditableWarning
              style={{ fontSize: '0.82rem', lineHeight: '1.5', color: '#333', ...editableBlockStyle }}
              onFocus={(e) => Object.assign(e.currentTarget.style, editableBlockFocusStyle)}
              onBlur={(e) => Object.assign(e.currentTarget.style, editableBlockStyle)}
              title="Click to edit"
            />
          </section>
        )}

        {findings.length > 0 && (
          <section>
            <h4 style={{ color: '#000', textTransform: 'uppercase', fontSize: '0.65rem', fontWeight: 800, letterSpacing: '0.05em', marginBottom: '0.4rem', borderBottom: '1px solid #eee', paddingBottom: '0.15rem' }}>Observations & Findings</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
              {findings.map((f, i) => (
                <div key={i} style={{ paddingLeft: '0.6rem', borderLeft: '2px solid #eee' }}>
                  <strong style={{ color: '#000', display: 'block', marginBottom: '0.15rem', fontSize: '0.8rem' }}>{f.region}</strong>
                  <p
                    ref={(el) => { findingRefs.current[i] = el; }}
                    contentEditable
                    suppressContentEditableWarning
                    style={{ fontSize: '0.8rem', color: '#444', lineHeight: '1.45', ...editableBlockStyle }}
                    onFocus={(e) => Object.assign(e.currentTarget.style, editableBlockFocusStyle)}
                    onBlur={(e) => Object.assign(e.currentTarget.style, editableBlockStyle)}
                    title="Click to edit"
                  />
                </div>
              ))}
            </div>
          </section>
        )}

        {impression && (
          <section data-section="impression" style={{ marginTop: 'auto', paddingTop: '1rem' }}>
            <div style={{ background: '#f8f9fa', padding: '0.85rem', border: '1px solid #eee' }}>
              <h4 style={{ color: '#000', textTransform: 'uppercase', fontSize: '0.65rem', fontWeight: 800, letterSpacing: '0.05em', marginBottom: '0.4rem' }}>Impression</h4>
              <p
                ref={impressionRef}
                contentEditable
                suppressContentEditableWarning
                style={{ fontSize: '0.9rem', fontWeight: 700, color: '#000', lineHeight: '1.35', ...editableBlockStyle }}
                onFocus={(e) => Object.assign(e.currentTarget.style, editableBlockFocusStyle)}
                onBlur={(e) => Object.assign(e.currentTarget.style, editableBlockStyle)}
                title="Click to edit"
              />
            </div>
          </section>
        )}

        {!summary && !findings.length && !impression && (
          <div style={{ padding: '4rem 0', textAlign: 'center' }}>
            <div style={{ width: '40px', height: '40px', border: '3px solid #eee', borderTopColor: '#000', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 1.5rem' }}></div>
            <p style={{ color: '#999', fontSize: '0.88rem', fontStyle: 'italic' }}>Awaiting diagnostic results...</p>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          </div>
        )}
      </div>

      {/* Footer / Watermark */}
      <div style={{ marginTop: '2rem', paddingTop: '0.6rem', borderTop: '1px solid #eee', textAlign: 'center', fontSize: '0.58rem', color: '#aaa', letterSpacing: '0.1em' }}>
        ELECTRONICALLY VERIFIED BY SPEEDRAY AI | SECURE LOG: SOLANA MAINNET
        <span style={{ display: 'block', marginTop: '0.25rem', color: '#bbb' }}>Click any report text to edit (add or remove characters).</span>
      </div>
    </div>
  );
}
