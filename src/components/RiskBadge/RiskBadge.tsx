/** Presage risk level and confidence display for SpeedRay */

import styles from './RiskBadge.module.css';

export interface RiskBadgeProps {
  level: string;
  confidence: number;
  className?: string;
}

const LEVEL_COLORS: Record<string, string> = {
  low: '#22c55e',
  medium: '#eab308',
  high: '#ef4444',
  unknown: '#6b7280',
  error: '#6b7280',
};

export function RiskBadge({ level, confidence, className }: RiskBadgeProps) {
  const color = LEVEL_COLORS[level.toLowerCase()] ?? LEVEL_COLORS.unknown;

  return (
    <div className={`${styles.badge} ${className ?? ''}`} style={{ borderColor: color }}>
      <span className={styles.level} style={{ color }}>{level}</span>
      <span className={styles.confidence}>
        {Math.round(confidence * 100)}% confidence
      </span>
    </div>
  );
}
