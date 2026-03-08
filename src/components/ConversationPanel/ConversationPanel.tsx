/**
 * Conversation flow: bot explains how the photo links to the summary,
 * user can repeat, then yes/no; "no" shows recommendations and closes.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { textToSpeech } from '../../ai_agents/ElevenLabs';
import { API_BASE } from '../../config';

export interface ConversationPanelProps {
  isOpen: boolean;
  onClose: () => void;
  /** Summary from the report */
  summary: string;
  /** Impression from the report */
  impression: string;
  /** Top finding name (e.g. from anomaly result) */
  topFindingName: string;
  studyId: string;
  /** Score 0–1 for risk; optional */
  topFindingScore?: number;
  /** Region of the finding (e.g. from report findings); defaults to "the chest" */
  region?: string;
  className?: string;
}

type Phase = 'explaining' | 'repeat-prompt' | 'yes-no' | 'goodbye' | 'recommendations' | 'closing';

function getRisk(score: number): 'Low' | 'Moderate' | 'High' {
  if (score > 0.62) return 'High';
  if (score >= 0.5) return 'Moderate';
  return 'Low';
}

export function ConversationPanel({
  isOpen,
  onClose,
  summary: _summary,
  impression: _impression,
  topFindingName,
  studyId,
  topFindingScore = 0,
  region: _region = 'the chest',
  className,
}: ConversationPanelProps) {
  const [phase, setPhase] = useState<Phase>('explaining');
  const [explanationAudioUrl, setExplanationAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<string | null>(null);
  const [goodbyeAudioUrl, setGoodbyeAudioUrl] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const goodbyeAudioRef = useRef<HTMLAudioElement>(null);

  const riskLabel = getRisk(topFindingScore);
  const explanationText = [
    'Hello, I am the XRayAnalystBot.',
    `Image shows ${topFindingName} with ${riskLabel} risk from highlighted area,`,
    'and this links to result from document because of findings which was detected in the image.',
  ].join(' ');

  const loadAndPlayExplanation = useCallback(async () => {
    if (!explanationText.trim()) {
      setError('No report content to explain.');
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await textToSpeech(explanationText);
      if (result.error || !result.url) {
        setError(result.error || 'Could not generate audio.');
        setExplanationAudioUrl(null);
      } else {
        setExplanationAudioUrl(result.url);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to generate explanation.');
      setExplanationAudioUrl(null);
    } finally {
      setLoading(false);
    }
  }, [explanationText]);

  useEffect(() => {
    if (!isOpen) return;
    setPhase('explaining');
    setRecommendations(null);
    loadAndPlayExplanation();
  }, [isOpen, loadAndPlayExplanation]);

  useEffect(() => {
    if (!explanationAudioUrl || !audioRef.current) return;
    const el = audioRef.current;
    const onEnded = () => setPhase('repeat-prompt');
    el.addEventListener('ended', onEnded);
    el.play().catch(() => setError('Playback failed.'));
    return () => el.removeEventListener('ended', onEnded);
  }, [explanationAudioUrl]);

  const fetchRecommendations = useCallback(async () => {
    const risk = getRisk(topFindingScore);
    try {
      const res = await fetch(`${API_BASE}/report/diagnostic-summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: studyId,
          top_critical: { name: topFindingName, score: topFindingScore, risk },
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setRecommendations(data.recommended_next_steps ?? 'Clinical correlation and follow-up as indicated.');
    } catch (e) {
      setRecommendations('Clinical correlation and follow-up imaging or specialist referral as indicated.');
    }
  }, [studyId, topFindingName, topFindingScore]);

  useEffect(() => {
    if (!goodbyeAudioUrl || !goodbyeAudioRef.current) return;
    const el = goodbyeAudioRef.current;
    const onEnded = async () => {
      setGoodbyeAudioUrl(null);
      setPhase('recommendations');
      await fetchRecommendations();
      setTimeout(onClose, 4000);
    };
    el.addEventListener('ended', onEnded);
    el.play().catch(() => {
      setGoodbyeAudioUrl(null);
      setPhase('recommendations');
      fetchRecommendations().then(() => setTimeout(onClose, 4000));
    });
    return () => el.removeEventListener('ended', onEnded);
  }, [goodbyeAudioUrl, fetchRecommendations, onClose]);

  const handleRepeat = () => {
    if (audioRef.current && explanationAudioUrl) {
      audioRef.current.currentTime = 0;
      audioRef.current.play().catch(() => setError('Playback failed.'));
    }
  };

  const handleYes = () => {
    setPhase('closing');
    onClose();
  };

  const handleNo = async () => {
    setPhase('goodbye');
    try {
      const result = await textToSpeech('Goodbye.');
      if (result.url) setGoodbyeAudioUrl(result.url);
      else {
        setPhase('recommendations');
        await fetchRecommendations();
        setTimeout(() => onClose(), 4000);
      }
    } catch {
      setPhase('recommendations');
      await fetchRecommendations();
      setTimeout(() => onClose(), 4000);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className={className}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(0,0,0,0.6)',
          padding: '1.5rem',
        }}
        onClick={(e) => e.target === e.currentTarget && onClose()}
      >
        <motion.div
          layout
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          style={{
            background: 'var(--glass-bg)',
            border: '1px solid var(--glass-border)',
            borderRadius: '16px',
            padding: '2rem',
            maxWidth: '420px',
            width: '100%',
            boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
          }}
        >
          {explanationAudioUrl && <audio ref={audioRef} src={explanationAudioUrl} />}
          {goodbyeAudioUrl && <audio ref={goodbyeAudioRef} src={goodbyeAudioUrl} />}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Conversation
            </h3>

            {loading && phase === 'explaining' && (
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                Preparing explanation…
              </p>
            )}
            {error && (
              <p style={{ color: '#ef4444', fontSize: '0.9rem' }}>{error}</p>
            )}

            <AnimatePresence mode="wait">
              {phase === 'explaining' && !loading && explanationAudioUrl && (
                <motion.p
                  key="explaining"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}
                >
                  Playing: XRayAnalystBot greeting…
                </motion.p>
              )}
              {phase === 'repeat-prompt' && (
                <motion.div
                  key="repeat"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}
                >
                  <p style={{ color: 'var(--text-primary)', fontSize: '0.95rem' }}>
                    Would you like me to repeat that?
                  </p>
                  <button
                    type="button"
                    onClick={handleRepeat}
                    className="glass"
                    style={{
                      padding: '0.5rem 1rem',
                      borderRadius: '8px',
                      border: '1px solid var(--glass-border)',
                      cursor: 'pointer',
                      color: 'var(--accent-blue)',
                      fontWeight: 600,
                    }}
                  >
                    Repeat
                  </button>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                    When ready, answer:
                  </p>
                  <div style={{ display: 'flex', gap: '0.75rem' }}>
                    <button
                      type="button"
                      onClick={handleYes}
                      className="btn-primary"
                      style={{ flex: 1, padding: '0.6rem 1rem' }}
                    >
                      Yes
                    </button>
                    <button
                      type="button"
                      onClick={handleNo}
                      className="glass"
                      style={{
                        flex: 1,
                        padding: '0.6rem 1rem',
                        border: '1px solid var(--glass-border)',
                        background: 'transparent',
                        color: 'var(--text-primary)',
                        cursor: 'pointer',
                      }}
                    >
                      No
                    </button>
                  </div>
                </motion.div>
              )}
              {phase === 'goodbye' && (
                <motion.p
                  key="goodbye"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}
                >
                  Goodbye…
                </motion.p>
              )}
              {phase === 'recommendations' && (
                <motion.div
                  key="recs"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  style={{
                    padding: '1rem',
                    background: 'rgba(255,255,255,0.06)',
                    borderRadius: '8px',
                    border: '1px solid var(--glass-border)',
                  }}
                >
                  <h4 style={{ margin: '0 0 0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    Recommendations
                  </h4>
                  <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                    {recommendations ?? 'Loading…'}
                  </p>
                  <p style={{ margin: '0.75rem 0 0', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    Closing conversation…
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
