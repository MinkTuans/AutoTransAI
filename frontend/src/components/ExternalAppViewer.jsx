import React from 'react';

export default function ExternalAppViewer({ appKey, appUrl, appTitle, onBack }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 70px)', width: '100%' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justify: 'space-between',
        padding: '10px 20px',
        backgroundColor: '#0f172a',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        color: '#fff'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <button
            onClick={onBack}
            style={{
              padding: '6px 14px',
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '6px',
              color: '#fff',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            ← Quay lại Chọn ứng dụng
          </button>
          <span style={{ fontWeight: '600', fontSize: '1.1rem' }}>{appTitle}</span>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8', background: '#1e293b', padding: '3px 8px', borderRadius: '4px' }}>
            {appUrl}
          </span>
        </div>
        <button
          onClick={() => window.open(appUrl, '_blank')}
          style={{
            padding: '6px 14px',
            backgroundColor: '#3b82f6',
            border: 'none',
            borderRadius: '6px',
            color: '#fff',
            cursor: 'pointer',
            fontWeight: '500'
          }}
        >
          Mở trong thẻ mới ↗
        </button>
      </div>

      <iframe
        src={appUrl}
        title={appTitle}
        style={{
          width: '100%',
          height: '100%',
          border: 'none',
          backgroundColor: '#0f172a'
        }}
      />
    </div>
  );
}
