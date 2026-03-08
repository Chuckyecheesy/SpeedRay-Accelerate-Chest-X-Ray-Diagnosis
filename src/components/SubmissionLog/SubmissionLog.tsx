export interface SubmissionLogProps {
  signature?: string | null;
  runId?: string;
  submittedAt?: string;
  className?: string;
}

export function SubmissionLog({
  signature,
  runId,
  submittedAt,
  className,
}: SubmissionLogProps) {
  if (!signature && !runId) return null;
  // Show "Verified" and timestamp only after user has signed (signature is set)
  if (!signature) return null;

  return (
    <div className={className} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 8px #22c55e' }}></div>
        <span style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-primary)' }}>Verified on Solana</span>
      </div>
      
      {signature && signature !== 'Signed' && (
        <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', display: 'flex', gap: '0.5rem' }}>
          <span>TX:</span>
          <code style={{ 
            background: 'rgba(255,255,255,0.05)', 
            padding: '1px 4px', 
            borderRadius: '4px',
            maxWidth: '120px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {signature}
          </code>
        </div>
      )}
      
      {submittedAt && (
        <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
          {new Date(submittedAt).toLocaleString()}
        </span>
      )}
    </div>
  );
}
