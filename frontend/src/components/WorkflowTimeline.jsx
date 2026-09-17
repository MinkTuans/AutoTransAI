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
  transferProgress = null,
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

  const formatBytes = (n) => {
    const num = Number(n) || 0;
    if (num < 1024) return `${num} B`;
    if (num < 1024 * 1024) return `${(num / 1024).toFixed(1)} KB`;
    return `${(num / (1024 * 1024)).toFixed(1)} MB`;
  };

  const transferPct = Math.min(100, Math.max(0, Number(transferProgress?.percent) || 0));
  const transferKind = transferProgress?.kind === 'upload' ? 'Tải lên' : 'Tải xuống';

  const getStatusBadge = (status) => {
    switch (status) {
      case 'passed':
      case 'completed':
      case 'success':
        return <span className="wf-chip ok">Passed</span>;
      case 'running':
      case 'processing':
        return (
          <span className="wf-chip run">
            <span className="spinner-icon">⚙</span> Running
          </span>
        );
      case 'paused':
        return <span className="wf-chip warn">Paused</span>;
      case 'needs_review':
      case 'segment_editing':
        return <span className="wf-chip warn">Chờ xác nhận</span>;
      case 'failed':
        return <span className="wf-chip err">Failed</span>;
      case 'cancelled':
        return <span className="wf-chip idle">Cancelled</span>;
      default:
        return <span className="wf-chip idle">Waiting</span>;
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
    <div className={`wf-panel ${isFailed ? 'is-failed' : ''}`}>
      <div className="wf-panel-head">
        <div>
          <h3 className="compact-card-title" style={{ color: isFailed ? '#fca5a5' : undefined }}>
            Pipeline 6 bước
            {job?.id && <span className="collapse-chip">Job {job.id}</span>}
          </h3>
          <div className="page-subtitle" style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginTop: 4 }}>
            <span>{getStatusBadge(currentStatus)}</span>
            <span>Tiến độ <strong>{overallProgress}%</strong></span>
            <span>Stage <strong>{currentStageName}</strong></span>
          </div>
        </div>

        <div className="wf-actions">
          {onOpenLogs && (
            <button type="button" className="btn btn-secondary btn-sm" onClick={onOpenLogs}>
              Log
            </button>
          )}
          {!isRunning && !isPaused && (
            <button type="button" className="btn btn-primary btn-sm" onClick={onStart} disabled={loadingAction}>
              {loadingAction === 'start' ? 'Starting...' : 'Start'}
            </button>
          )}
          {isRunning && (
            <button type="button" className="btn btn-secondary btn-sm" onClick={onPause} disabled={loadingAction}>
              {loadingAction === 'pause' ? 'Pausing...' : 'Pause'}
            </button>
          )}
          {isPaused && (
            <button type="button" className="btn btn-primary btn-sm" onClick={onResume} disabled={loadingAction}>
              {loadingAction === 'resume' ? 'Resuming...' : 'Resume'}
            </button>
          )}
          {(isRunning || isPaused) && onCancel && (
            <button type="button" className="btn btn-danger btn-sm" onClick={onCancel} disabled={loadingAction}>
              {loadingAction === 'cancel' ? 'Cancelling...' : 'Cancel'}
            </button>
          )}
          {isFailed && onRetryJob && (
            <button type="button" className="btn btn-secondary btn-sm" onClick={onRetryJob} disabled={loadingAction === 'retry'}>
              {loadingAction === 'retry' ? 'Retrying...' : 'Retry'}
            </button>
          )}
        </div>
      </div>

      <div className="progress-container">
        <div className="progress-bar-bg">
          <div
            className={`progress-bar-fill ${isFailed ? 'warning' : ''}`}
            style={{
              width: `${overallProgress}%`,
              background: isFailed ? '#ef4444' : undefined,
            }}
          />
        </div>
        {transferProgress && (
          <div style={{ marginTop: 8 }}>
            <div className="progress-label" style={{ fontSize: 11 }}>
              <span>{transferKind}: <strong>{transferProgress.message || `${transferPct.toFixed(0)}%`}</strong></span>
              <span>
                {formatBytes(transferProgress.downloaded_bytes)} / {formatBytes(transferProgress.total_bytes)}
                {transferProgress.speed ? ` · ${transferProgress.speed}` : ''}
                {transferProgress.eta ? ` · ETA ${transferProgress.eta}` : ''}
              </span>
            </div>
            <div className="progress-bar-bg">
              <div
                className="progress-bar-fill success"
                style={{
                  width: `${transferPct}%`,
                  background: transferProgress.status === 'failed' ? '#ef4444' : undefined,
                }}
              />
            </div>
          </div>
        )}
      </div>

      <div className="wf-stages">
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
            else if (['segment_editing', 'needs_review'].includes(currentStatus)) stDataStatus = 'needs_review';
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

          const stageClass = [
            'wf-stage',
            isSelected ? 'is-selected' : '',
            isStageRunning ? 'is-running stage-card-running' : '',
            isPassed ? 'is-passed' : '',
            isStageFailed ? 'is-failed' : '',
            isNeedsReview ? 'is-review' : '',
          ].filter(Boolean).join(' ');

          return (
            <button
              type="button"
              key={st.id}
              onClick={() => setSelectedStageOverride(st.id)}
              className={stageClass}
            >
              <div className="inline-row" style={{ justifyContent: 'space-between', marginBottom: 2 }}>
                <span>{st.icon}</span>
                {isStageRunning && <span className="spinner-icon">⏳</span>}
              </div>
              <div className="wf-stage-label">{st.label}</div>
              <div className="wf-stage-desc">{st.desc}</div>
              <div>{getStatusBadge(stDataStatus)}</div>
            </button>
          );
        })}
      </div>

      <div className="wf-telemetry">
        <div className="wf-telemetry-grid">
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
            <div style={{ fontSize: '12px', fontFamily: 'monospace', color: '#fecaca', marginTop: '2px', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', maxWidth: '100%' }}>
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
              Trạng thái Stage: <strong>{getStatusBadge(STAGES.find(s => s.id === activeStage) ? (curStageIdx > (STAGES.findIndex(s => s.id === activeStage) + 1) ? 'passed' : (curStageIdx === (STAGES.findIndex(s => s.id === activeStage) + 1) ? (currentStatus === 'failed' ? 'failed' : (['segment_editing', 'needs_review'].includes(currentStatus) ? 'needs_review' : (isRunning ? 'running' : (isPaused ? 'paused' : 'pending')))) : 'pending')) : 'pending')}</strong>
            </div>
          )}
        </div>
      )}

    </div>
  );
}
