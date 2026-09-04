import React, { useState, useEffect } from 'react';

const STAGES = [
  { id: 'INGEST', label: '1. INGEST', desc: 'Import & Audio Extract', icon: '📥' },
  { id: 'ANALYZE', label: '2. ANALYZE', desc: 'STT & Timeline Cleanup', icon: '🔍' },
  { id: 'TRANSLATE', label: '3. TRANSLATE', desc: 'Glossary & Translation', icon: '🌐' },
  { id: 'DUB', label: '4. DUB', desc: 'Voice Mapping & Dubbing', icon: '🎙️' },
  { id: 'PRODUCE', label: '5. PRODUCE', desc: 'Subtitles & Final Render', icon: '🎬' },
  { id: 'PUBLISH', label: '6. PUBLISH', desc: 'SEO & YouTube Upload', icon: '🚀' },
];

export default function WorkflowTimeline({ projectId, statusData, onStart, onPause, onResume }) {
  const [activeStage, setActiveStage] = useState('INGEST');

  if (!statusData) return null;

  const getStatusBadge = (status) => {
    switch (status) {
      case 'passed':
      case 'completed':
      case 'success':
        return <span style={{ background: '#10B981', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '12px' }}>🟢 Passed</span>;
      case 'running':
        return <span style={{ background: '#3B82F6', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '12px' }}>🔵 Running</span>;
      case 'needs_review':
        return <span style={{ background: '#F59E0B', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '12px' }}>🟡 Needs Review</span>;
      case 'failed':
        return <span style={{ background: '#EF4444', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '12px' }}>🔴 Failed</span>;
      default:
        return <span style={{ background: '#4B5563', color: '#9CA3AF', padding: '2px 8px', borderRadius: '12px', fontSize: '12px' }}>⚪ Waiting</span>;
    }
  };

  const stagesMap = {};
  if (statusData.stages) {
    statusData.stages.forEach((st) => {
      stagesMap[st.name] = st;
    });
  }

  const selectedStageData = stagesMap[activeStage] || {};

  return (
    <div style={{ background: '#1F2937', padding: '20px', borderRadius: '12px', color: '#F3F4F6', marginBottom: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>Unified 6-Stage Workflow Pipeline</h3>
          <p style={{ margin: '4px 0 0 0', color: '#9CA3AF', fontSize: '14px' }}>
            Current Stage: <strong style={{ color: '#60A5FA' }}>{statusData.current_stage || 'INGEST'}</strong> — Step: <span>{statusData.current_step || 'Ready'}</span>
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={onStart}
            style={{ padding: '8px 16px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
          >
            ▶ Start Workflow
          </button>
          <button
            onClick={onPause}
            style={{ padding: '8px 16px', background: '#D97706', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
          >
            ⏸ Pause
          </button>
          <button
            onClick={onResume}
            style={{ padding: '8px 16px', background: '#059669', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
          >
            🔄 Resume
          </button>
        </div>
      </div>

      {/* 6 Stage Timeline Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px', marginBottom: '16px' }}>
        {STAGES.map((st) => {
          const stData = stagesMap[st.id] || {};
          const isCurrent = statusData.current_stage === st.id;
          const isSelected = activeStage === st.id;

          return (
            <div
              key={st.id}
              onClick={() => setActiveStage(st.id)}
              style={{
                background: isSelected ? '#374151' : '#111827',
                border: isCurrent ? '2px solid #3B82F6' : '1px solid #374151',
                borderRadius: '8px',
                padding: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ fontSize: '20px', marginBottom: '4px' }}>{st.icon}</div>
              <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#F3F4F6' }}>{st.label}</div>
              <div style={{ fontSize: '11px', color: '#9CA3AF', marginBottom: '8px' }}>{st.desc}</div>
              <div>{getStatusBadge(stData.status)}</div>
            </div>
          );
        })}
      </div>

      {/* Stage Detail Drawer */}
      <div style={{ background: '#111827', padding: '16px', borderRadius: '8px', border: '1px solid #374151' }}>
        <h4 style={{ margin: '0 0 8px 0', fontSize: '15px' }}>Stage Detail: {activeStage}</h4>
        <p style={{ fontSize: '13px', color: '#9CA3AF', margin: '0 0 8px 0' }}>
          Status: {getStatusBadge(selectedStageData.status)} | Retry Count: {selectedStageData.retry_count || 0}
        </p>

        {selectedStageData.error && (
          <div style={{ background: '#7F1D1D', color: '#FCA5A5', padding: '10px', borderRadius: '6px', fontSize: '13px', marginBottom: '8px' }}>
            ⚠️ Error: {selectedStageData.error}
          </div>
        )}

        {selectedStageData.qc_report && (
          <div style={{ fontSize: '13px' }}>
            <strong>QC Report:</strong>
            <pre style={{ background: '#1F2937', padding: '8px', borderRadius: '4px', color: '#A7F3D0', overflowX: 'auto' }}>
              {JSON.stringify(selectedStageData.qc_report, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
