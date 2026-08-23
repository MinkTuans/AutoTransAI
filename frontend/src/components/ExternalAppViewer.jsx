import React from 'react';

export default function ExternalAppViewer({
  appKey,
  appUrl,
  appTitle,
  onBack,
  isHeaderCollapsed,
  onToggleHeaderCollapse,
}) {
  return (
    <div
      className="external-app-container"
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '100%',
        backgroundColor: '#0f172a',
      }}
    >
      {!isHeaderCollapsed ? (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 16px',
            backgroundColor: '#0f172a',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            color: '#fff',
            transition: 'all 0.3s ease',
            zIndex: 10,
            boxSizing: 'border-box',
          }}
        >
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
                fontWeight: '500',
              }}
              title="Quay lại danh sách chọn ứng dụng"
            >
              ← Quay lại Chọn ứng dụng
            </button>
            <span style={{ fontWeight: '600', fontSize: '1.1rem' }}>{appTitle}</span>
            <span
              style={{
                fontSize: '0.85rem',
                color: '#94a3b8',
                background: '#1e293b',
                padding: '3px 8px',
                borderRadius: '4px',
              }}
            >
              {appUrl}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              onClick={() => window.open(appUrl, '_blank')}
              style={{
                padding: '6px 14px',
                backgroundColor: '#3b82f6',
                border: 'none',
                borderRadius: '6px',
                color: '#fff',
                cursor: 'pointer',
                fontWeight: '500',
              }}
              title="Mở ứng dụng này trong một thẻ trình duyệt mới"
            >
              Mở trong thẻ mới ↗
            </button>

            <button
              onClick={onToggleHeaderCollapse}
              style={{
                padding: '6px 12px',
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '6px',
                color: '#38bdf8',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '0.9rem',
              }}
              title="Thu gọn toàn bộ thanh điều khiển và Header chính"
            >
              ▲ Thu gọn
            </button>
          </div>
        </div>
      ) : (
        <div
          style={{
            display: 'flex',
            justifyContent: 'flex-end',
            padding: '4px 12px',
            backgroundColor: '#0f172a',
            borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
            zIndex: 10,
            boxSizing: 'border-box',
          }}
        >
          <button
            onClick={onToggleHeaderCollapse}
            style={{
              padding: '2px 10px',
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '4px',
              color: '#38bdf8',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '0.8rem',
            }}
            title="Mở rộng toàn bộ thanh điều khiển và Header chính"
          >
            ▼ Mở rộng
          </button>
        </div>
      )}

      <iframe
        src={appUrl}
        title={appTitle}
        style={{
          width: '100%',
          flex: 1,
          border: 'none',
          backgroundColor: '#0f172a',
        }}
      />
    </div>
  );
}

