import React, { useState } from 'react';

const STAGES = [
  { id: 'INGEST', label: '1. INGEST', desc: 'Import & Audio Extract', icon: '📥' },
  { id: 'ANALYZE', label: '2. ANALYZE', desc: 'STT & Timeline Cleanup', icon: '🔍' },
  { id: 'TRANSLATE', label: '3. TRANSLATE', desc: 'Glossary & Translation', icon: '🌐' },
  { id: 'DUB', label: '4. DUB', desc: 'Voice Mapping & Dubbing', icon: '🎙️' },
  { id: 'PRODUCE', label: '5. PRODUCE', desc: 'Subtitles & Final Render', icon: '🎬' },
  { id: 'PUBLISH', label: '6. PUBLISH', desc: 'SEO & YouTube Upload', icon: '🚀' },
];

const STAGE_ORDER_MAP = {
  CREATED: { id: 'INGEST', idx: 1 },
  QUEUED: { id: 'INGEST', idx: 1 },
  INGEST: { id: 'INGEST', idx: 1 },
  EXTRACTING_AUDIO: { id: 'INGEST', idx: 1 },
  ANALYZE: { id: 'ANALYZE', idx: 2 },
  TRANSCRIBING: { id: 'ANALYZE', idx: 2 },
  STT: { id: 'ANALYZE', idx: 2 },
  TRANSLATE: { id: 'TRANSLATE', idx: 3 },
  TRANSLATING: { id: 'TRANSLATE', idx: 3 },
  SEGMENT_EDITING: { id: 'TRANSLATE', idx: 3 },
  DUB: { id: 'DUB', idx: 4 },
  GENERATING_TTS: { id: 'DUB', idx: 4 },
  SYNTHESIZING: { id: 'DUB', idx: 4 },
  SYNCING_AUDIO: { id: 'DUB', idx: 4 },
  PRODUCE: { id: 'PRODUCE', idx: 5 },
  RENDERING: { id: 'PRODUCE', idx: 5 },
  RENDER_DONE: { id: 'PRODUCE', idx: 5 },
  PUBLISH: { id: 'PUBLISH', idx: 6 },
  PUBLISHING: { id: 'PUBLISH', idx: 6 },
  COMPLETED: { id: 'PUBLISH', idx: 6 },
};

export default function WorkflowTimeline({
  projectId,
  statusData,
  job,
  pipelineError,
  onStart,
  onPause,
  onResume,
  onCancel,
  onRetryStage,
  onRetryJob,
  onOpenLogs,
  loadingAction,
  lastPollTime,
  lastApiResponseTime,
  segments = [],
}) {
  const [selectedStageOverride, setSelectedStageOverride] = useState(null);
  const [showDebug, setShowDebug] = useState(false);

  if (!statusData && !job) return null;

  const currentJob = job || {};
  const currentStatus = job?.status || statusData?.status || 'not_started';
  const overallProgress = job?.overall_progress_pct ?? statusData?.overall_progress_pct ?? 0;

  // Resolve active stage unambiguously
  const curStageObj = STAGE_ORDER_MAP[job?.stage] || STAGE_ORDER_MAP[statusData?.current_stage] || { id: 'INGEST', idx: 1 };
  const currentStageName = currentStatus === 'completed' ? 'PUBLISH' : curStageObj.id;
  const curStageIdx = currentStatus === 'completed' ? 6 : curStageObj.idx;
  const activeStage = selectedStageOverride || currentStageName;

  const formatTime = (sec) => {
    if (!sec || isNaN(sec)) return '00:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'passed':
      case 'completed':
      case 'success':
        return <span style={{ background: '#10B981', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 'bold' }}>🟢 Passed</span>;
      case 'running':
      case 'processing':
        return (
          <span style={{ background: '#2563EB', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 'bold', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <span className="spinner-icon">⚙️</span> Running...
          </span>
        );
      case 'paused':
        return <span style={{ background: '#D97706', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 'bold' }}>⏸ Paused</span>;
      case 'needs_review':
      case 'segment_editing':
        return <span style={{ background: '#F59E0B', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 'bold' }}>🟡 Chờ xác nhận</span>;
      case 'failed':
        return <span style={{ background: '#EF4444', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 'bold' }}>🔴 Failed</span>;
      case 'cancelled':
        return <span style={{ background: '#6B7280', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 'bold' }}>⚪ Cancelled</span>;
      default:
        return <span style={{ background: '#334155', color: '#94a3b8', padding: '2px 8px', borderRadius: '12px', fontSize: '11px' }}>⚪ Waiting</span>;
    }
  };

  const getHeartbeatBadge = (currentJobObj) => {
    if (!currentJobObj || !currentJobObj.status) return null;
    const st = currentJobObj.status;
    const heartbeat = currentJobObj.heartbeat || {};
    const ageSec = heartbeat.age_seconds ?? 999;

    if (st === 'failed') return <span style={{ color: '#f87171', fontSize: '12px', fontWeight: 'bold' }}>🔴 FAILED</span>;
    if (st === 'completed') return <span style={{ color: '#4ade80', fontSize: '12px', fontWeight: 'bold' }}>🟢 COMPLETED</span>;
    if (st === 'cancelled') return <span style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>⚪ CANCELLED</span>;
    if (st === 'segment_editing') return <span style={{ color: '#6ee7b7', fontSize: '12px', fontWeight: 'bold' }}>🟢 Phase 1 Done (Chờ xác nhận bản dịch)</span>;
    if (st === 'stalled') return <span style={{ color: '#fb923c', fontSize: '12px', fontWeight: 'bold' }}>🟠 STALLED</span>;

    if (heartbeat.active && ageSec <= 15) {
      return <span style={{ color: '#4ade80', fontSize: '12px', fontWeight: 'bold' }}>🟢 Worker Active ({Math.round(ageSec)}s)</span>;
    }
    if (ageSec <= 45) {
      return <span style={{ color: '#facc15', fontSize: '12px', fontWeight: 'bold' }}>🟡 Processing ({Math.round(ageSec)}s)</span>;
    }
    return <span style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>⚪ Worker Idle</span>;
  };

  const stagesMap = {};
  if (statusData?.stages) {
    statusData.stages.forEach((st) => {
      stagesMap[st.name] = st;
    });
  }

  const selectedStageData = stagesMap[activeStage] || {};
  const isRunning = currentStatus === 'running' || ['extracting_audio', 'stt', 'translating', 'generating_tts', 'syncing_audio', 'rendering'].includes(currentStatus);
  const isPaused = currentStatus === 'paused';
  const isFailed = currentStatus === 'failed' || Boolean(pipelineError);

  return (
    <div style={{ background: '#0f172a', border: `1px solid ${isFailed ? '#ef4444' : '#334155'}`, borderRadius: '12px', padding: '16px 20px', color: '#F3F4F6' }}>
      
      {/* Top Bar: Title & Main Control Buttons */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '20px' }}>🚀</span>
          <div>
            <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', color: isFailed ? '#fca5a5' : '#818cf8', display: 'flex', alignItems: 'center', gap: '8px' }}>
              Unified 6-Stage Workflow Pipeline
              {job?.id && <span style={{ fontSize: '12px', color: '#94a3b8', background: '#1e293b', padding: '2px 8px', borderRadius: '6px', border: '1px solid #334155' }}>Job: {job.id}</span>}
            </h3>
            <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span>Trạng thái: {getStatusBadge(currentStatus)}</span>
              <span>•</span>
              <span>Tiến độ: <strong style={{ color: isFailed ? '#fca5a5' : '#60a5fa' }}>{overallProgress}%</strong></span>
              <span>•</span>
              <span>Stage: <strong style={{ color: '#60a5fa' }}>{currentStageName}</strong></span>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '6px', alignItems: 'center', flexWrap: 'wrap' }}>
          {onOpenLogs && (
            <button
              onClick={onOpenLogs}
              style={{
                padding: '6px 12px',
                background: '#1e293b',
                color: '#93c5fd',
                border: '1px solid #3b82f6',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              📜 Xem Log
            </button>
          )}

          {!isRunning && !isPaused && (
            <button
              onClick={onStart}
              disabled={loadingAction}
              style={{
                padding: '6px 14px',
                background: 'linear-gradient(90deg, #2563eb 0%, #4f46e5 100%)',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: loadingAction ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                fontSize: '12px',
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
                padding: '6px 14px',
                background: '#d97706',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: loadingAction ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                fontSize: '12px',
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
                padding: '6px 14px',
                background: '#059669',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: loadingAction ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                fontSize: '12px',
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
                padding: '6px 12px',
                background: '#dc2626',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: loadingAction ? 'not-allowed' : 'pointer',
                fontWeight: '600',
                fontSize: '12px',
                opacity: loadingAction ? 0.7 : 1,
              }}
            >
              {loadingAction === 'cancel' ? '⏳ Cancelling...' : '🛑 Cancel'}
            </button>
          )}

          {isFailed && onRetryJob && (
            <button
              onClick={onRetryJob}
              disabled={loadingAction === 'retry'}
              style={{
                padding: '6px 12px',
                background: loadingAction === 'retry' ? '#78350f' : '#d97706',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: loadingAction === 'retry' ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                fontSize: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              {loadingAction === 'retry' ? '⏳ Retrying...' : '🔄 Smart Retry'}
            </button>
          )}
        </div>
      </div>

      {/* Overall Progress Bar */}
      <div style={{ marginBottom: '14px' }}>
        <div style={{ background: '#1e293b', borderRadius: '6px', height: '10px', width: '100%', overflow: 'hidden', border: '1px solid #334155' }}>
          <div
            style={{
              width: `${overallProgress}%`,
              height: '100%',
              background: isFailed ? '#ef4444' : 'linear-gradient(90deg, #3b82f6, #8b5cf6)',
              transition: 'width 0.3s ease',
            }}
          />
        </div>
      </div>

      {/* 6 Stage Grid Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))', gap: '8px', marginBottom: '14px' }}>
        {STAGES.map((st, idx) => {
          const stIdx = idx + 1;
          const isSelected = activeStage === st.id;

          let stDataStatus = 'pending';
          if (currentStatus === 'completed') {
            stDataStatus = 'passed';
          } else if (stIdx < curStageIdx) {
            stDataStatus = 'passed';
          } else if (stIdx === curStageIdx) {
            if (currentStatus === 'failed') stDataStatus = 'failed';
            else if (currentStatus === 'segment_editing') stDataStatus = 'needs_review';
            else if (currentStatus === 'paused') stDataStatus = 'paused';
            else if (currentStatus === 'cancelled') stDataStatus = 'cancelled';
            else stDataStatus = isRunning ? 'running' : (stagesMap[st.id]?.status || 'running');
          } else {
            stDataStatus = 'pending';
          }

          const isStageRunning = stDataStatus === 'running';
          const isPassed = stDataStatus === 'passed';
          const isStageFailed = stDataStatus === 'failed';
          const isNeedsReview = stDataStatus === 'needs_review';

          let cardBorder = '1px solid #334155';
          let cardBg = isSelected ? '#1e293b' : '#0f172a';

          if (isStageRunning) {
            cardBorder = '2px solid #3b82f6';
            cardBg = isSelected ? '#1e3a8a' : '#1e293b';
          } else if (isPassed) {
            cardBorder = '1px solid #10b981';
            cardBg = isSelected ? '#064e3b' : '#062c22';
          } else if (isStageFailed) {
            cardBorder = '1px solid #ef4444';
            cardBg = isSelected ? '#7f1d1d' : '#450a0a';
          } else if (isNeedsReview) {
            cardBorder = '2px solid #f59e0b';
            cardBg = isSelected ? '#78350f' : '#451a03';
          }

          return (
            <div
              key={st.id}
              onClick={() => setSelectedStageOverride(st.id)}
              className={isStageRunning ? 'stage-card-running' : ''}
              style={{
                background: cardBg,
                border: cardBorder,
                borderRadius: '8px',
                padding: '8px 10px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ fontSize: '16px', marginBottom: '2px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>{st.icon}</span>
                {isStageRunning && <span className="spinner-icon" style={{ fontSize: '12px' }}>⏳</span>}
              </div>
              <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#f8fafc', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{st.label}</div>
              <div style={{ fontSize: '10px', color: '#94a3b8', marginBottom: '4px', height: '14px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{st.desc}</div>
              <div>{getStatusBadge(stDataStatus)}</div>
            </div>
          );
        })}
      </div>

      {/* Integrated Processing Telemetry Sub-Panel */}
      <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '12px 14px', fontSize: '12px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px' }}>
          <div>
            <span style={{ color: '#94a3b8' }}>Bước hiện tại:</span>
            <div style={{ fontWeight: 'bold', color: isFailed ? '#fca5a5' : '#e2e8f0', marginTop: '2px' }}>
              {currentJob.current_step || statusData?.current_step || 'Processing'}
            </div>
          </div>

          <div>
            <span style={{ color: '#94a3b8' }}>Worker Heartbeat:</span>
            <div style={{ marginTop: '2px' }}>
              {getHeartbeatBadge(currentJob)}
            </div>
          </div>

          <div>
            <span style={{ color: '#94a3b8' }}>FFmpeg Process:</span>
            <div style={{ fontWeight: 'bold', color: currentJob.process?.status === 'RUNNING' ? '#60a5fa' : (currentJob.process?.status === 'COMPLETED' ? '#4ade80' : (currentJob.process?.status === 'FAILED' ? '#ef4444' : '#94a3b8')), marginTop: '2px' }}>
              {currentJob.process?.status === 'RUNNING' ? `⚡ RUNNING (PID: ${currentJob.process.pid})` : (currentJob.process?.status === 'COMPLETED' ? '✅ COMPLETED' : (currentJob.process?.status || 'IDLE'))}
            </div>
          </div>

          <div>
            <span style={{ color: '#94a3b8' }}>Dữ liệu Phân đoạn:</span>
            <div style={{ fontWeight: 'bold', color: '#c084fc', marginTop: '2px' }}>
              {currentJob.completed_segments_count !== undefined
                ? `${currentJob.completed_segments_count} / ${currentJob.total_segments_count || 0} Phân đoạn`
                : `${segments.length} Phân đoạn`}
            </div>
          </div>
        </div>

        {/* FFmpeg stats inline display */}
        {currentJob.ffmpeg_stats && currentJob.status !== 'failed' && (
          <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #334155', display: 'flex', gap: '16px', color: '#cbd5e1', fontSize: '11px', flexWrap: 'wrap' }}>
            <span>⚡ FFmpeg Duration: <strong>{formatTime(currentJob.ffmpeg_stats.processed_seconds)} / {formatTime(currentJob.ffmpeg_stats.total_duration)}</strong></span>
            <span>Speed: <strong>{currentJob.ffmpeg_stats.speed}</strong></span>
            <span>FPS: <strong>{currentJob.ffmpeg_stats.fps}</strong></span>
          </div>
        )}

        {/* Debug Telemetry Details Toggle */}
        <div style={{ marginTop: '8px', paddingTop: '6px', borderTop: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '11px', color: '#64748b' }}>Single Source of Truth DB Sync</span>
          <button
            type="button"
            onClick={() => setShowDebug(!showDebug)}
            style={{ background: 'none', border: 'none', color: '#60a5fa', fontSize: '11px', cursor: 'pointer', padding: 0 }}
          >
            {showDebug ? '▲ Ẩn Telemetry DB' : '🐞 Debug State (DB Status)'}
          </button>
        </div>

        {showDebug && (
          <div style={{ marginTop: '8px', padding: '10px', background: '#0f172a', borderRadius: '6px', fontSize: '11px', fontFamily: 'monospace', color: '#38bdf8', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '6px' }}>
            <div>Job ID: <strong style={{ color: '#fff' }}>{currentJob.id || 'N/A'}</strong></div>
            <div>Status: <strong style={{ color: '#a7f3d0' }}>{currentJob.status || currentStatus}</strong></div>
            <div>Stage: <strong style={{ color: '#60a5fa' }}>{currentStageName} ({job?.stage || 'N/A'})</strong></div>
            <div>Detected Lang: <strong style={{ color: '#fbbf24' }}>{currentJob.detected_language || 'Auto'}</strong></div>
            <div>STT Status: <strong style={{ color: '#4ade80' }}>{currentJob.stt?.status || 'PENDING'}</strong></div>
            <div>Translation: <strong style={{ color: '#4ade80' }}>{currentJob.translation?.status || 'PENDING'}</strong></div>
            <div>Last Poll: <strong style={{ color: '#cbd5e1' }}>{lastPollTime || 'N/A'}</strong></div>
            <div>API Time: <strong style={{ color: '#cbd5e1' }}>{lastApiResponseTime || 'N/A'}</strong></div>
          </div>
        )}
      </div>

      {/* Compact Error Banner Integrated Inside Pipeline Footer */}
      {(pipelineError || currentJob.status === 'failed' || currentJob.error_message) && (
        <div style={{ marginTop: '12px', padding: '10px 14px', background: '#450a0a', border: '1px solid #ef4444', borderRadius: '8px', color: '#fee2e2', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
          <div style={{ flex: 1, minWidth: '220px' }}>
            <div style={{ fontWeight: 'bold', color: '#fca5a5', fontSize: '13px' }}>❌ Xử Lý Thất Bại</div>
            <div style={{ fontSize: '12px', fontFamily: 'monospace', color: '#fecaca', marginTop: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '500px' }}>
              {currentJob.error_message || pipelineError || 'Xảy ra lỗi trong quá trình thực thi pipeline.'}
            </div>
          </div>
          <div style={{ display: 'flex', gap: '6px' }}>
            {onOpenLogs && (
              <button
                onClick={onOpenLogs}
                style={{ padding: '4px 10px', borderRadius: '4px', background: '#78350f', color: '#fef3c7', border: '1px solid #d97706', cursor: 'pointer', fontSize: '11px', fontWeight: 'bold' }}
              >
                📜 Log
              </button>
            )}
            {onRetryJob && (
              <button
                onClick={onRetryJob}
                disabled={loadingAction === 'retry'}
                style={{ padding: '4px 10px', borderRadius: '4px', background: '#d97706', color: '#fff', border: 'none', cursor: 'pointer', fontSize: '11px', fontWeight: 'bold' }}
              >
                🔄 Thử lại
              </button>
            )}
          </div>
        </div>
      )}

      {/* Selected Stage Detail Drawer */}
      {activeStage && (
        <div style={{ marginTop: '12px', background: '#0f172a', padding: '12px', borderRadius: '8px', border: '1px solid #334155' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontSize: '13px', fontWeight: 'bold', color: '#cbd5e1' }}>Chi tiết Stage: {activeStage}</span>
            {onRetryStage && (
              <button
                onClick={() => onRetryStage(activeStage)}
                disabled={loadingAction}
                style={{ padding: '3px 8px', background: '#4338ca', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '11px', fontWeight: 'bold' }}
              >
                🔄 Retry Stage {activeStage}
              </button>
            )}
          </div>

          {selectedStageData.steps && selectedStageData.steps.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '6px', marginTop: '6px' }}>
              {selectedStageData.steps.map((stStep) => (
                <div
                  key={stStep.name}
                  style={{
                    background: stStep.status === 'success' || stStep.status === 'passed' ? '#062c22' : (stStep.status === 'failed' ? '#450a0a' : '#1e293b'),
                    padding: '6px 8px',
                    borderRadius: '4px',
                    fontSize: '11px',
                    border: '1px solid #334155',
                    display: 'flex',
                    justify: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <span style={{ fontFamily: 'monospace', color: '#e2e8f0' }}>{stStep.name}</span>
                  {getStatusBadge(stStep.status)}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ fontSize: '11px', color: '#94a3b8', fontStyle: 'italic', marginTop: '4px' }}>
              Trạng thái Stage: <strong>{getStatusBadge(STAGES.find(s => s.id === activeStage) ? (curStageIdx > (STAGES.findIndex(s => s.id === activeStage) + 1) ? 'passed' : (curStageIdx === (STAGES.findIndex(s => s.id === activeStage) + 1) ? (currentStatus === 'failed' ? 'failed' : (currentStatus === 'segment_editing' ? 'needs_review' : 'running')) : 'pending')) : 'pending')}</strong>
            </div>
          )}
        </div>
      )}

    </div>
  );
}
