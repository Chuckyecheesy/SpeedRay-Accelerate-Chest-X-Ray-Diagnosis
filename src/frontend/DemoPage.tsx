import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ROUTES, API_BASE } from '../config';
import { XRayViewer } from '../components/XRayViewer';
import { ReportPanel } from '../components/ReportPanel';
import { AudioExplanation } from '../components/AudioExplanation';
import { ConversationPanel } from '../components/ConversationPanel';
import { SubmissionLog } from '../components/SubmissionLog';
import { ConnectWallet } from '../wallet';
import { runPipeline } from '../pipeline';
import type { PipelineRunState } from '../pipeline';

type Step = 'UPLOAD' | 'RESULTS';

export function DemoPage() {
  const [state, setState] = useState<PipelineRunState | null>(null);
  const [step, setStep] = useState<Step>('UPLOAD');
  const [isDragging, setIsDragging] = useState(false);
  const [previewImageUrl, setPreviewImageUrl] = useState<string | null>(null);
  const [conversationOpen, setConversationOpen] = useState(false);
  const [erReceivedPopupOpen, setErReceivedPopupOpen] = useState(false);
  const [showReportScrollButton, setShowReportScrollButton] = useState(false);
  const [reportZoom, setReportZoom] = useState(1);
  const [reannotateLoading, setReannotateLoading] = useState(false);
  const reportScrollRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const reportZoomIn = useCallback(() => setReportZoom((z) => Math.min(z + 0.15, 1.8)), []);
  const reportZoomOut = useCallback(() => setReportZoom((z) => Math.max(z - 0.15, 0.6)), []);
  const reportZoomReset = useCallback(() => setReportZoom(1), []);

  const closeErReceivedPopup = useCallback(() => {
    setErReceivedPopupOpen(false);
    navigate(ROUTES.HOME);
  }, [navigate]);

  const handleFile = useCallback((f: File) => {
    const runId = `run_${Date.now()}`;
    const studyId = `study_${runId}`;
    const now = new Date().toISOString();
    const blobUrl = URL.createObjectURL(f);
    setPreviewImageUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return blobUrl;
    });
    setState({
      runId,
      studyId,
      status: 'running',
      startedAt: now,
      updatedAt: now,
    });
    setStep('RESULTS');
    runAnalysis(f, runId, studyId, blobUrl);
  }, []);

  const runAnalysis = async (f: File, runId: string, studyId: string, blobUrl: string) => {
    try {
      const result = await runPipeline({
        runId,
        studyId,
        file: f,
        onStateChange: setState,
      });
      setState(result);
      if (result?.uploadResult?.url) {
        URL.revokeObjectURL(blobUrl);
        setPreviewImageUrl(null);
      }
      // #region agent log
      const u = result?.uploadResult?.url ?? '';
      const impression = result?.report?.impression ?? '';
      fetch('http://127.0.0.1:7258/ingest/1a4b0efb-f996-45bb-bf9d-737f2bd4387e',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'025a2b'},body:JSON.stringify({sessionId:'025a2b',hypothesisId:'H3',location:'DemoPage.tsx:runAnalysis',message:'Result uploadResult.url and report',data:{url_preview:(u||'').slice(0,80),hasUrl:!!u,impression_preview:(impression||'').slice(0,300),has_report_error:impression.startsWith('Error:')},timestamp:Date.now()})}).catch(()=>{});
      // #endregion
    } catch (err) {
      console.error(err);
      const msg = err instanceof Error ? err.message : String(err);
      const errorMsg = msg.includes('abort') ? 'Request timed out (3 min). Try again or use a smaller image.' : msg;
      setState((prev) => (prev ? { ...prev, status: 'failed', error: errorMsg, updatedAt: new Date().toISOString() } : {
        runId,
        studyId,
        status: 'failed',
        error: errorMsg,
        startedAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }));
    }
  };

  const onNewScan = useCallback(() => {
    if (previewImageUrl) {
      URL.revokeObjectURL(previewImageUrl);
      setPreviewImageUrl(null);
    }
    setState(null);
    setStep('UPLOAD');
  }, [previewImageUrl]);

  const onRefreshAnnotation = useCallback(async () => {
    if (!state?.uploadResult?.publicId || !state?.anomalyResult) return;
    setReannotateLoading(true);
    try {
      const top = state.anomalyResult.top_critical;
      const score = typeof top?.score === 'number' ? top.score : 0;
      const risk = score > 0.62 ? 'High' : score > 0.5 ? 'Moderate' : 'Low';
      const res = await fetch(`${API_BASE}/pipeline/reannotate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          public_id: state.uploadResult.publicId,
          regions: state.anomalyResult.regions ?? [],
          top_critical: {
            name: top?.name ?? 'Finding',
            score,
            risk,
          },
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      const url = data?.annotated_url;
      if (url && state.uploadResult) {
        setState((prev) => prev && prev.uploadResult ? { ...prev, uploadResult: { ...prev.uploadResult, url }, updatedAt: new Date().toISOString() } : prev);
      }
    } catch (err) {
      console.error('Reannotate failed:', err);
    } finally {
      setReannotateLoading(false);
    }
  }, [state?.uploadResult?.publicId, state?.uploadResult, state?.anomalyResult]);

  useEffect(() => () => { if (previewImageUrl) URL.revokeObjectURL(previewImageUrl); }, [previewImageUrl]);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  };

  const handleSign = useCallback(() => {
    if (!state?.report) return;
    const now = new Date().toISOString();
    setState((prev) => prev ? { ...prev, logTxSignature: 'Signed', updatedAt: now } : prev);
    setErReceivedPopupOpen(true);
  }, [state?.report]);

  return (
    <div className="demo-page" style={{
      minHeight: '100vh',
      padding: '2rem',
      background: 'linear-gradient(160deg, #0a0c12 0%, #05070a 40%, #020305 100%)',
    }}>
      <AnimatePresence mode="wait">
        {step === 'UPLOAD' && (
          <motion.div 
            key="upload"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            style={{ maxWidth: '800px', margin: '10vh auto' }}
          >
            <h1 style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '2.5rem' }}>Upload Case</h1>
            <div 
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={onDrop}
              className="glass"
              style={{
                height: '400px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                border: isDragging ? '2px dashed var(--accent-blue)' : '2px dashed var(--glass-border)',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onClick={() => document.getElementById('fileInput')?.click()}
            >
              <input 
                id="fileInput"
                type="file" 
                style={{ display: 'none' }} 
                onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              />
              <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🩻</div>
              <h3>Drag & Drop Chest X-ray</h3>
              <p style={{ color: 'var(--text-secondary)' }}>or click to browse locally</p>
            </div>
          </motion.div>
        )}

        {step === 'RESULTS' && (
          <motion.div 
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="results-container"
            style={{ 
              width: '100%',
              maxWidth: '1800px',
              margin: '0 auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
            }}
          >
            {state?.error && (
              <div className="glass" style={{ padding: '1rem 1.5rem', color: 'var(--text-primary)', borderLeft: '4px solid #ef4444' }}>
                <strong>Error:</strong> {state.error}
              </div>
            )}
            {/* Single box: top = X-ray + report, bottom = action bar. No overlap: content scrolls if needed, bar stays fixed at bottom. */}
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                height: 'calc(100vh - 6rem)',
                minHeight: 480,
                overflow: 'hidden',
                border: '1px solid var(--glass-border)',
                borderRadius: '16px',
                background: 'var(--bg-darker)',
              }}
            >
              {/* Content area: grid must fill height so report column gets real height and scrolls (no cutoff). */}
              <div style={{ 
                flex: 1,
                minHeight: 280,
                height: 0,
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                padding: '1rem',
              }}>
                <div style={{
                  flex: 1,
                  minHeight: 0,
                  display: 'grid',
                  gridTemplateColumns: 'minmax(220px, 0.58fr) minmax(420px, 1.42fr)',
                  gridTemplateRows: '1fr',
                  gap: '1rem',
                }}>
                <div className="glass" style={{
                  display: 'flex',
                  flexDirection: 'column',
                  overflow: 'hidden',
                  position: 'relative',
                  background: '#0a0a0f',
                  border: '1px solid var(--glass-border)',
                  borderRadius: '12px',
                  minHeight: 0,
                }}>
                  <XRayViewer imageUrl={state?.uploadResult?.url || previewImageUrl || ''} />
                  {!state?.uploadResult?.url && !previewImageUrl && (
                    <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#000' }}>
                      <p style={{ color: 'var(--text-secondary)' }}>Awaiting image source...</p>
                    </div>
                  )}
                </div>
                <div style={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  overflow: 'hidden',
                  minHeight: 0,
                  background: 'var(--glass-bg)',
                  border: '1px solid var(--glass-border)',
                  borderRadius: '12px',
                  position: 'relative',
                }}>
                  <div
                    ref={reportScrollRef}
                    className="report-panel-scroll"
                    onScroll={() => {
                      const el = reportScrollRef.current;
                      setShowReportScrollButton(!!(el && el.scrollTop > 80));
                    }}
                    style={{ flex: 1, overflow: 'auto', minHeight: 0 }}
                  >
                    <div style={{ zoom: reportZoom, minHeight: '100%' } as React.CSSProperties}>
                      <ReportPanel
                          summary={state?.report?.summary}
                          findings={state?.report?.findings as never[]}
                          impression={state?.report?.impression}
                          isLoading={state?.status === 'running' && !state?.report && !state?.error}
                          studyId={state?.studyId}
                        />
                    </div>
                  </div>
                  {/* Report zoom: Zoom in | Reset | Zoom out */}
                  <div style={{
                    position: 'absolute',
                    top: '0.5rem',
                    right: '0.5rem',
                    zIndex: 10,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.25rem',
                    background: 'rgba(10, 12, 18, 0.85)',
                    padding: '0.4rem',
                    borderRadius: '10px',
                    border: '1px solid var(--glass-border)',
                  }}>
                    <span style={{ fontSize: '0.6rem', color: 'var(--text-secondary)', fontWeight: 600, textAlign: 'center', marginBottom: '0.1rem' }}>Report zoom</span>
                    <button type="button" className="btn-primary" style={{ padding: '5px 10px', minWidth: '36px', fontSize: '1rem' }} onClick={reportZoomIn} title="Zoom in">+</button>
                    <button type="button" className="btn-primary" style={{ padding: '5px 10px', minWidth: '36px', fontSize: '0.85rem' }} onClick={reportZoomReset} title="Reset zoom">⟲</button>
                    <button type="button" className="btn-primary" style={{ padding: '5px 10px', minWidth: '36px', fontSize: '1rem' }} onClick={reportZoomOut} title="Zoom out">−</button>
                  </div>
                  {showReportScrollButton && (
                    <button
                      type="button"
                      onClick={() => {
                        const el = reportScrollRef.current;
                        if (!el) return;
                        const impression = el.querySelector('[data-section="impression"]');
                        if (impression) {
                          impression.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        } else {
                          el.scrollTo({ top: 0, behavior: 'smooth' });
                        }
                      }}
                      style={{
                        position: 'absolute',
                        bottom: '1rem',
                        right: '1rem',
                        zIndex: 10,
                        padding: '0.5rem 0.85rem',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        background: 'var(--gradient-primary)',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        boxShadow: '0 2px 12px rgba(59, 130, 246, 0.4)',
                      }}
                    >
                      Scroll to Impression
                    </button>
                  )}
                </div>
                </div>
              </div>
              {/* Bottom bar: slightly compact — Select wallet | Play (Hear AI) | Conversation | Submit */}
              <div
                style={{ 
                  flexShrink: 0,
                  padding: '0.5rem 1.25rem', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '0.5rem',
                  borderTop: '1px solid var(--glass-border)',
                  background: 'rgba(10, 12, 18, 0.98)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                  <ConnectWallet />
                  <AudioExplanation audioUrl={state?.audioUrl} />
                  {state?.report && (
                    <button
                      type="button"
                      className="glass"
                      onClick={() => setConversationOpen(true)}
                    style={{
                      padding: '0.4rem 0.85rem',
                      borderRadius: '8px',
                      fontSize: '0.9rem',
                        border: '1px solid var(--glass-border)',
                        cursor: 'pointer',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                      }}
                    >
                      Conversation
                    </button>
                  )}
                  {state?.uploadResult?.publicId && state?.anomalyResult && (
                    <button
                      type="button"
                      className="glass"
                      onClick={onRefreshAnnotation}
                      disabled={reannotateLoading}
                      style={{
                        padding: '0.4rem 0.85rem',
                        borderRadius: '8px',
                        fontSize: '0.9rem',
                        border: '1px solid var(--glass-border)',
                        cursor: reannotateLoading ? 'wait' : 'pointer',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                      }}
                      title="Re-build annotated image with current regions"
                    >
                      {reannotateLoading ? 'Refreshing…' : 'Refresh annotation'}
                    </button>
                  )}
                  <SubmissionLog
                    signature={state?.logTxSignature}
                    runId={state?.runId}
                    submittedAt={state?.updatedAt}
                  />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <button 
                    className="btn-primary" 
                    style={{ background: 'transparent', border: '1px solid var(--glass-border)', boxShadow: 'none', padding: '0.4rem 0.85rem', fontSize: '0.9rem' }} 
                    onClick={onNewScan}
                  >
                    New Scan
                  </button>
                  <button
                    type="button"
                    className="btn-primary"
                    style={{ minWidth: '88px', padding: '0.4rem 0.85rem', fontSize: '0.9rem' }}
                    onClick={handleSign}
                    disabled={!state?.report || state?.logTxSignature === 'Signed'}
                    aria-label="Submit"
                  >
                    {state?.logTxSignature === 'Signed' ? 'Submitted' : 'Submit'}
                  </button>
                </div>
              </div>
            </div>

            {erReceivedPopupOpen && (
              <div
                role="dialog"
                aria-modal="true"
                style={{
                  position: 'fixed',
                  inset: 0,
                  zIndex: 1001,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'rgba(0,0,0,0.6)',
                  padding: '1.5rem',
                }}
                onClick={closeErReceivedPopup}
              >
                <div
                  className="glass"
                  style={{
                    padding: '2rem',
                    borderRadius: '16px',
                    maxWidth: '360px',
                    textAlign: 'center',
                    border: '1px solid var(--glass-border)',
                    boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
                  }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <p style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '1.5rem', lineHeight: 1.5 }}>
                    ER department has received the result.
                  </p>
                  <button
                    type="button"
                    className="btn-primary"
                    onClick={closeErReceivedPopup}
                  >
                    OK
                  </button>
                </div>
              </div>
            )}

            <ConversationPanel
              isOpen={conversationOpen}
              onClose={() => setConversationOpen(false)}
              summary={state?.report?.summary ?? ''}
              impression={state?.report?.impression ?? ''}
              topFindingName={
                state?.anomalyResult?.top_critical?.name ??
                state?.anomalyResult?.diseases?.[0]?.name ??
                'Finding'
              }
              studyId={state?.studyId ?? ''}
              topFindingScore={
                state?.anomalyResult?.top_critical?.score ??
                state?.anomalyResult?.diseases?.[0]?.score ??
                0
              }
              region={
                (state?.report?.findings as { region?: string }[])?.[0]?.region ?? 'the chest'
              }
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
