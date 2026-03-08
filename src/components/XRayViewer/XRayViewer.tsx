import { useCallback, useState } from 'react';
import { motion } from 'framer-motion';

export interface XRayViewerProps {
  imageUrl: string;
  alt?: string;
  className?: string;
}

export function XRayViewer({ imageUrl, alt = 'Chest X-ray', className }: XRayViewerProps) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });

  const zoomIn = useCallback(() => setZoom((z) => Math.min(z + 0.25, 3)), []);
  const zoomOut = useCallback(() => setZoom((z) => Math.max(z - 0.25, 0.5)), []);
  const reset = useCallback(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, []);

  return (
    <div className={`xray-viewer-container ${className ?? ''}`} style={{
      width: '100%',
      height: '100%',
      minHeight: 240,
      position: 'relative',
      overflow: 'hidden',
      background: '#000',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <motion.div
        animate={{
          x: pan.x,
          y: pan.y,
          scale: zoom,
        }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: zoom > 1 ? 'grab' : 'default',
          width: '100%',
          height: '100%',
          minHeight: 0,
        }}
      >
        <img 
          src={imageUrl} 
          alt={alt} 
          style={{ 
            maxWidth: '100%',
            maxHeight: '100%',
            width: 'auto',
            height: 'auto',
            objectFit: 'contain',
            objectPosition: 'center',
            pointerEvents: 'none',
            display: 'block',
          }} 
          draggable={false} 
        />
      </motion.div>

      {/* Zoom controls: right edge, vertical — do not cover image */}
      <div className="glass" style={{
        position: 'absolute',
        top: '50%',
        right: '0.5rem',
        transform: 'translateY(-50%)',
        padding: '0.35rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.25rem',
        zIndex: 20
      }}>
        <button className="btn-primary" style={{ padding: '6px 12px', minWidth: '36px' }} onClick={zoomIn} title="Zoom in">+</button>
        <button className="btn-primary" style={{ padding: '6px 12px', minWidth: '36px' }} onClick={reset} title="Reset view">⟲</button>
        <button className="btn-primary" style={{ padding: '6px 12px', minWidth: '36px' }} onClick={zoomOut} title="Zoom out">−</button>
      </div>

      <div style={{
        position: 'absolute',
        top: '0.5rem',
        left: '0.5rem',
        padding: '0.35rem 0.75rem',
        background: 'rgba(0,0,0,0.5)',
        borderRadius: '6px',
        fontSize: '0.75rem',
        color: 'var(--text-secondary)',
        backdropFilter: 'blur(4px)'
      }}>
        AI Annotated View
      </div>
    </div>
  );
}
