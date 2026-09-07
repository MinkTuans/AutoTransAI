import React, { useState } from 'react';

const STAGES = [
  { id: 'INGEST', label: '1. INGEST', desc: 'Import & Audio Extract', icon: '📥' },
  { id: 'ANALYZE', label: '2. ANALYZE', desc: 'STT & Timeline Cleanup', icon: '🔍' },
  { id: 'TRANSLATE', label: '3. TRANSLATE', desc: 'Glossary & Translation', icon: '🌐' },
  { id: 'DUB', label: '4. DUB', desc: 'Voice Mapping & Dubbing', icon: '🎙️' },
  { id: 'PRODUCE', label: '5. PRODUCE', desc: 'Subtitles & Final Render', icon: '🎬' },
  { id: 'PUBLISH', label: '6. PUBLISH', desc: 'SEO & YouTube Upload', icon: '🚀' },
];

export default function WorkflowTimeline({
  projectId,
  statusData,
  onStart,
  onPause,
  onResume,
  onCancel,
  onRetryStage,
  loadingAction,
}) {
  const [activeStage, setActiveStage] = useState('INGEST');

  if (!statusData) return null;

  const getStatusBadge = (status) => {
    switch (status) {
      case 'passed':
      case 'completed':
      case 'success':
        return <span style={{ background: '#10B981', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold' }}>🟢 Passed</span>;
      case 'running':
        return (
          <span style={{ background: '#2563EB', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <span className="spinner-icon">⚙️</span> Running...
          </span>
        );
      case 'paused':
        return <span style={{ background: '#D97706', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold' }}>⏸ Paused</span>;
      case 'needs_review':
        return <span style={{ background: '#F59E0B', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold' }}>🟡 Needs Review</span>;
      case 'failed':
        return <span style={{ background: '#EF4444', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold' }}>🔴 Failed</span>;
      case 'cancelled':
        return <span style={{ background: '#6B7280', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold' }}>⚪ Cancelled</span>;
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
  const isRunning = statusData.status === 'running';
  const isPaused = statusData.status === 'paused';

  return (
    <div style={{ background: '#1F2937', padding: '20px', borderRadius: '12px', color: '#F3F4F6', marginBottom: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>Unified 6-Stage Workflow Pipeline</h3>
          <p style={{ margin: '4px 0 0 0', color: '#9CA3AF', fontSize: '14px' }}>
            Status: {getStatusBadge(statusData.status)} | Progress: <strong style={{ color: '#60A5FA' }}>{statusData.overall_progress_pct || 0}%</strong> | Stage: <strong style={{ color: '#60A5FA' }}>{statusData.current_stage || 'INGEST'}</strong> — Step: <span>{statusData.current_step || 'Ready'}</span>
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {!isRunning && !isPaused && (
            <button
              onClick={onStart}
              disabled={loadingAction}
              style={{
                padding: '8px 16px',
                background: '#2563EB',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: loadingAction ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                fontSize: '13px',
                opacity: loadingAction ? 0.7 : 1,
              }}
            >
              {loadingAction === 'start' ? '⏳ Starting...' : '▶ Start Workflow'}
            </button>
          )}

          {isRunning && (
            <button
              onClick={onPause}
              disabled={loadingAction}
              style={{
                padding: '8px 16px',
                background: '#D97706',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: loadingAction ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                fontSize: '13px',
                opacity: loadingAction ? 0.7 : 1,
              }}
            >
              {loadingAction === 'pause' ? '⏳ Pausing...' : '⏸ Pause'}
            </button>
          )}

          {isPaused && (
            <button
              onClick={onResume}
              disabled={loadingAction}
              style={{
                padding: '8px 16px',
                background: '#059669',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: loadingAction ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                fontSize: '13px',
                opacity: loadingAction ? 0.7 : 1,
              }}
            >
              {loadingAction === 'resume' ? '⏳ Resuming...' : '▶ Resume'}
            </button>
          )}

          {(isRunning || isPaused) && onCancel && (
            <button
              onClick={onCancel}
              disabled={loadingAction}
              style={{
                padding: '8px 16px',
                background: '#DC2626',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: loadingAction ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                fontSize: '13px',
                opacity: loadingAction ? 0.7 : 1,
              }}
            >
              {loadingAction === 'cancel' ? '⏳ Cancelling...' : '🛑 Cancel'}
            </button>
          )}
        </div>
      </div>

      {/* 6 Stage Timeline Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px', marginBottom: '16px' }}>
        {STAGES.map((st) => {
          const stData = stagesMap[st.id] || {};
          const isCurrent = statusData.current_stage === st.id;
          const isSelected = activeStage === st.id;
          const isPassed = stData.status === 'passed' || stData.status === 'completed' || stData.status === 'success';
          const isFailed = stData.status === 'failed';
          const isStageRunning = stData.status === 'running' || (isCurrent && isRunning);

          let cardBorder = '1px solid #374151';
          let cardBg = isSelected ? '#374151' : '#111827';

          if (isStageRunning) {
            cardBorder = '2px solid #3B82F6';
            cardBg = isSelected ? '#1E3A8A' : '#1E293B';
          } else if (isPassed) {
            cardBorder = '2px solid #10B981';
            cardBg = isSelected ? '#064E3B' : '#062C22';
          } else if (isFailed) {
            cardBorder = '2px solid #EF4444';
            cardBg = isSelected ? '#7F1D1D' : '#450A0A';
          }

          return (
            <div
              key={st.id}
              onClick={() => setActiveStage(st.id)}
              className={isStageRunning ? 'stage-card-running' : ''}
              style={{
                background: cardBg,
                border: cardBorder,
                borderRadius: '8px',
                padding: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ fontSize: '20px', marginBottom: '4px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>{st.icon}</span>
                {isStageRunning && <span className="spinner-icon" style={{ fontSize: '14px' }}>⏳</span>}
              </div>
              <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#F3F4F6' }}>{st.label}</div>
              <div style={{ fontSize: '11px', color: '#9CA3AF', marginBottom: '8px' }}>{st.desc}</div>
              <div>{getStatusBadge(isStageRunning ? 'running' : (stData.status || (isPassed ? 'passed' : 'pending')))}</div>
            </div>
          );
        })}
      </div>

      {/* Stage Detail Drawer */}
      <div style={{ background: '#111827', padding: '16px', borderRadius: '8px', border: '1px solid #374151' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <h4 style={{ margin: 0, fontSize: '15px' }}>Stage Detail: {activeStage}</h4>
          {onRetryStage && (
            <button
              onClick={() => onRetryStage(activeStage)}
              disabled={loadingAction}
              style={{
                padding: '4px 10px',
                background: '#4F46E5',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: loadingAction ? 'not-allowed' : 'pointer',
                fontSize: '12px',
                fontWeight: 'bold',
              }}
            >
              🔄 Retry Stage {activeStage}
            </button>
          )}
        </div>

        <p style={{ fontSize: '13px', color: '#9CA3AF', margin: '0 0 12px 0' }}>
          Status: {getStatusBadge(selectedStageData.status)} | Retry Count: {selectedStageData.retry_count || 0}
        </p>

        {selectedStageData.error && (
          <div style={{ background: '#7F1D1D', color: '#FCA5A5', padding: '10px', borderRadius: '6px', fontSize: '13px', marginBottom: '12px' }}>
            ⚠️ Error: {selectedStageData.error}
          </div>
        )}

        {/* Steps breakdown list */}
        {selectedStageData.steps && selectedStageData.steps.length > 0 && (
          <div style={{ marginBottom: '12px' }}>
            <strong style={{ fontSize: '13px', color: '#D1D5DB' }}>Stage Steps Breakdown:</strong>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '8px', marginTop: '6px' }}>
              {selectedStageData.steps.map((stStep) => {
                const isStepRunning = stStep.status === 'running';
                const isStepPassed = stStep.status === 'success' || stStep.status === 'passed' || stStep.status === 'completed';
                const isStepFailed = stStep.status === 'failed';

                let stepBorder = '1px solid #374151';
                if (isStepRunning) stepBorder = '1px solid #3B82F6';
                else if (isStepPassed) stepBorder = '1px solid #10B981';
                else if (isStepFailed) stepBorder = '1px solid #EF4444';

                return (
                  <div
                    key={stStep.name}
                    className={isStepRunning ? 'stage-card-running' : ''}
                    style={{
                      background: isStepPassed ? '#062C22' : (isStepFailed ? '#450A0A' : '#1F2937'),
                      padding: '8px 12px',
                      borderRadius: '6px',
                      fontSize: '12px',
                      border: stepBorder,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <span style={{ fontFamily: 'monospace', color: '#E5E7EB', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {isStepRunning && <span className="spinner-icon">⏳</span>}
                      {stStep.name}
                    </span>
                    {getStatusBadge(stStep.status)}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {selectedStageData.qc_report && (
          <div style={{ fontSize: '13px' }}>
            <strong>QC Report:</strong>
            <pre style={{ background: '#1F2937', padding: '8px', borderRadius: '4px', color: '#A7F3D0', overflowX: 'auto', marginTop: '4px' }}>
              {JSON.stringify(selectedStageData.qc_report, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

