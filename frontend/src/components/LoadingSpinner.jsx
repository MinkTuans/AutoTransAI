import React from 'react';

/**
 * Reusable animated Spinner component with glowing ring and customizable sizes & text.
 */
export function LoadingSpinner({ size = 'md', label = null, sublabel = null, fullscreen = false }) {
  return (
    <div className={`loading-spinner-container ${fullscreen ? 'fullscreen' : ''}`}>
      <div className="loading-spinner-wrapper">
        <div className={`spinner-glow-ring ${size}`} />
      </div>
      {label && <div className="loading-label">{label}</div>}
      {sublabel && <div className="loading-sublabel">{sublabel}</div>}
    </div>
  );
}

/**
 * Micro spinner icon for buttons during async submission states.
 */
export function ButtonSpinner() {
  return <span className="button-spinner" role="status" aria-hidden="true" />;
}

/**
 * Glassmorphic overlay placed on top of cards, forms, or tables during processing.
 */
export function LoadingOverlay({ message = 'Đang xử lý...', submessage = 'Vui lòng chờ trong giây lát...' }) {
  return (
    <div className="loading-overlay">
      <LoadingSpinner size="lg" label={message} sublabel={submessage} />
    </div>
  );
}

/**
 * Shimmering skeleton loader for table rows, cards, or list placeholders.
 */
export function SkeletonLoader({ type = 'table', rows = 4, columns = 5 }) {
  if (type === 'table') {
    return (
      <div style={{ width: '100%' }}>
        {Array.from({ length: rows }).map((_, rIdx) => (
          <div key={rIdx} className="skeleton-table-row">
            {Array.from({ length: columns }).map((_, cIdx) => (
              <div
                key={cIdx}
                className="skeleton-bar"
                style={{
                  flex: cIdx === 0 ? 2 : 1,
                  height: '1.2rem',
                }}
              />
            ))}
          </div>
        ))}
      </div>
    );
  }

  if (type === 'card') {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.25rem', width: '100%' }}>
        {Array.from({ length: rows }).map((_, idx) => (
          <div key={idx} className="skeleton-card">
            <div className="skeleton-bar title" />
            <div className="skeleton-bar text" style={{ width: '90%' }} />
            <div className="skeleton-bar text" style={{ width: '65%' }} />
            <div className="skeleton-bar text" style={{ width: '40%', marginTop: '1rem' }} />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div style={{ width: '100%' }}>
      {Array.from({ length: rows }).map((_, idx) => (
        <div key={idx} style={{ marginBottom: '1rem' }}>
          <div className="skeleton-bar title" />
          <div className="skeleton-bar text" />
        </div>
      ))}
    </div>
  );
}

export default LoadingSpinner;
