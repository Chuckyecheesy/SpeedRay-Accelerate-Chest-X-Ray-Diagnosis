/** Renders annotations and metadata from Cloudinary on X-ray for SpeedRay */

import styles from './AnnotationOverlay.module.css';

export interface Annotation {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  label?: string;
  score?: number;
}

export interface AnnotationOverlayProps {
  annotations: Annotation[];
  imageWidth: number;
  imageHeight: number;
  containerWidth: number;
  containerHeight: number;
  className?: string;
}

export function AnnotationOverlay({
  annotations,
  imageWidth,
  imageHeight,
  containerWidth,
  containerHeight,
  className,
}: AnnotationOverlayProps) {
  const scaleX = imageWidth ? containerWidth / imageWidth : 1;
  const scaleY = imageHeight ? containerHeight / imageHeight : 1;

  return (
    <div className={`${styles.overlay} ${className ?? ''}`}>
      {annotations.map((a) => (
        <div
          key={a.id}
          className={styles.box}
          style={{
            left: a.x * scaleX,
            top: a.y * scaleY,
            width: a.width * scaleX,
            height: a.height * scaleY,
          }}
          title={a.label ?? `Score: ${a.score ?? ''}`}
        >
          {a.label && <span className={styles.label}>{a.label}</span>}
        </div>
      ))}
    </div>
  );
}
