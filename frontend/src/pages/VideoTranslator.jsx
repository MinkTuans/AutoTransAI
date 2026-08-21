import React, { useState, useEffect, useRef } from 'react';
import { videoTranslatorApi, providersApi } from '../api';

export default function VideoTranslator() {
  const [inputMode, setInputMode] = useState('url');
  const [videoUrl, setVideoUrl] = useState('');
  const [uploadFile, setUploadFile] = useState(null);

  // Status & Metadata
  const [isCheckingUrl, setIsCheckingUrl] = useState(false);
  const [urlMetadata, setUrlMetadata] = useState(null);
  const [checkError, setCheckError] = useState(null);

  // Config options
  const [targetLanguage, setTargetLanguage] = useState('vi');
  const [audioProviderId, setAudioProviderId] = useState('edge_tts');
  const [voices, setVoices] = useState([]);
  const [voiceId, setVoiceId] = useState('vi-VN-HoaiMyNeural');
  const [originalAudioMode, setOriginalAudioMode] = useState('mute');

  // Job execution state
  const [asset, setAsset] = useState(null);
  const [job, setJob] = useState(null);
  const [segments, setSegments] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [pipelineError, setPipelineError] = useState(null);

  // Log Modal state
  const [showLogModal, setShowLogModal] = useState(false);
  const [logsContent, setLogsContent] = useState('');
  const [isFetchingLogs, setIsFetchingLogs] = useState(false);
  const [copySuccess, setCopySuccess] = useState('');

  // Polling ref
  const pollingRef = useRef(null);

  // Fetch voices when provider or language changes
  useEffect(() => {
    providersApi.listVoices(audioProviderId, targetLanguage)
      .then(res => {
        if (res.success && res.data) {
          setVoices(res.data);
          if (res.data.length > 0) {
            setVoiceId(res.data[0].id);
          }
        }
      })
      .catch(() => setVoices([]));
  }, [audioProviderId, targetLanguage]);

  // Robust Polling for job updates with terminal state guard
  useEffect(() => {
    if (!job?.id) return;

    const isTerminal = ['completed', 'failed', 'cancelled', 'segment_editing'].includes(job.status);
    if (isTerminal) {
      if (isProcessing) setIsProcessing(false);
      return;
    }

    pollingRef.current = setInterval(() => {
      videoTranslatorApi.getJob(job.id)
        .then(res => {
          if (res.success && res.data) {
            const newJob = res.data;
            setJob(prev => {
              // Terminal state guard: Never overwrite terminal status with older response
              if (prev && ['completed', 'failed', 'cancelled'].includes(prev.status)) {
                return prev;
              }
              return newJob;
            });

            if (newJob.segments && newJob.segments.length > 0) {
              setSegments(newJob.segments);
            }

            if (['completed', 'failed', 'cancelled', 'segment_editing'].includes(newJob.status)) {
              setIsProcessing(false);
              clearInterval(pollingRef.current);
            }
          }
        })
        .catch(console.error);
    }, 1500);

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [job?.id, job?.status]);

  const fetchLogs = async (jobId) => {
    if (!jobId) return;
    setIsFetchingLogs(true);
    try {
      const res = await videoTranslatorApi.getLogs(jobId);
      if (res.success) {
        setLogsContent(res.data.logs || 'Chưa có dữ liệu log.');
      }
    } catch (err) {
      setLogsContent('Không thể tải log: ' + (err.message || 'Lỗi server'));
    } finally {
      setIsFetchingLogs(false);
    }
  };

  const handleOpenLogs = () => {
    if (job) {
      fetchLogs(job.id);
      setShowLogModal(true);
    }
  };

  const handleCheckUrl = async () => {
    if (!videoUrl) return;
    setIsCheckingUrl(true);
    setCheckError(null);
    setUrlMetadata(null);
    try {
      const res = await videoTranslatorApi.checkUrl(videoUrl);
      if (res.success) {
        setUrlMetadata(res.data);
      }
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Lỗi kiểm tra URL';
      setCheckError(detail);
    } finally {
      setIsCheckingUrl(false);
    }
  };

  const handleStartImportAndTranslation = async () => {
    setIsProcessing(true);
    setPipelineError(null);
    setJob(null);
    setSegments([]);

    try {
      let importedAsset;
      if (inputMode === 'upload') {
        if (!uploadFile) throw new Error('Vui lòng chọn file video.');
        const res = await videoTranslatorApi.importUpload(uploadFile);
        importedAsset = res.data;
      } else {
        if (!videoUrl) throw new Error('Vui lòng nhập URL video.');
        const res = await videoTranslatorApi.importUrl(videoUrl);
        importedAsset = res.data;
      }
      setAsset(importedAsset);

      const jobRes = await videoTranslatorApi.createJob({
        asset_id: importedAsset.asset_id,
        source_language: 'auto',
        target_language: targetLanguage,
        audio_provider_id: audioProviderId,
        voice_id: voiceId,
        original_audio_mode: originalAudioMode,
      });

      const newJobId = jobRes.data.job_id;
      await videoTranslatorApi.startJob(newJobId);
      const initialJob = await videoTranslatorApi.getJob(newJobId);
      setJob(initialJob.data);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Không thể bắt đầu dịch video';
      setPipelineError(detail);
      setIsProcessing(false);
    }
  };

  const handleSegmentTextChange = (segId, newText) => {
    setSegments(prev =>
      prev.map(s => (s.id === segId ? { ...s, translated_text: newText } : s))
    );
  };

  const handleRenderFinalVideo = async () => {
    if (!job) return;
    setIsProcessing(true);
    try {
      await videoTranslatorApi.updateSegments(
        job.id,
        segments.map(s => ({ id: s.id, translated_text: s.translated_text }))
      );

      await videoTranslatorApi.renderJob(job.id);
      const updated = await videoTranslatorApi.getJob(job.id);
      setJob(updated.data);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Lỗi render video';
      setPipelineError(detail);
      setIsProcessing(false);
    }
  };

  const handleCancelJob = async () => {
    if (!job) return;
    if (!window.confirm('Bạn có chắc chắn muốn hủy tiến trình dịch video này không?')) return;
    try {
      await videoTranslatorApi.cancelJob(job.id);
      const updated = await videoTranslatorApi.getJob(job.id);
      setJob(updated.data);
      setIsProcessing(false);
    } catch (err) {
      alert('Không thể hủy job: ' + (err.message || 'Lỗi'));
    }
  };

  const handleRetryJob = async () => {
    if (!job) return;
    setIsProcessing(true);
    setPipelineError(null);
    try {
      await videoTranslatorApi.retryJob(job.id);
      const updated = await videoTranslatorApi.getJob(job.id);
      setJob(updated.data);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Lỗi retry job';
      setPipelineError(detail);
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds) => {
    if (!seconds) return '00:00';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // Single Source of Truth Heartbeat & Status Badge
  const getHeartbeatBadge = (currentJob) => {
    if (!currentJob) return null;

    const status = currentJob.status;
    const ageSec = currentJob.last_heartbeat_age_sec ?? 999;

    if (status === 'failed') {
      return (
        <span style={{ color: '#f87171', fontSize: '13px', fontWeight: 'bold' }}>
          🔴 Job thất bại (FAILED)
        </span>
      );
    }
    if (status === 'completed') {
      return (
        <span style={{ color: '#4ade80', fontSize: '13px', fontWeight: 'bold' }}>
          🟢 Hoàn thành (COMPLETED)
        </span>
      );
    }
    if (status === 'cancelled') {
      return (
        <span style={{ color: '#94a3b8', fontSize: '13px', fontWeight: 'bold' }}>
          ⚪ Đã hủy bởi người dùng (CANCELLED)
        </span>
      );
    }
    if (status === 'stalled') {
      return (
        <span style={{ color: '#fb923c', fontSize: '13px', fontWeight: 'bold' }}>
          🟠 Process có thể đã bị treo (STALLED)
        </span>
      );
    }

    if (ageSec <= 15) {
      return (
        <span style={{ color: '#4ade80', fontSize: '13px', fontWeight: 'bold' }}>
          🟢 Worker đang hoạt động (Cập nhật {Math.round(ageSec)}s trước)
        </span>
      );
    }
    if (ageSec <= 45) {
      return (
        <span style={{ color: '#facc15', fontSize: '13px', fontWeight: 'bold' }}>
          🟡 Đang chờ cập nhật từ server... (Cập nhật {Math.round(ageSec)}s trước)
        </span>
      );
    }
    return (
      <span style={{ color: '#f87171', fontSize: '13px', fontWeight: 'bold' }}>
        🔴 Mất kết nối heartbeat (Không nhận phản hồi &gt; {Math.round(ageSec)}s)
      </span>
    );

  };

  return (
    <div className="video-translator-container" style={{ padding: '24px', maxWidth: '1100px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px', color: '#818cf8' }}>
        🎬 Video Translator – Dịch & Lồng tiếng Video
      </h1>
      <p style={{ color: '#94a3b8', marginBottom: '24px' }}>
        Tự động dịch giọng nói trong video từ URL Internet hoặc file Upload với cơ chế real-time tracking, heartbeat và FFmpeg process log.
      </p>

      {/* Input Selection Card */}
      <div className="card" style={{ background: '#1e1b4b', border: '1px solid #3730a3', borderRadius: '12px', padding: '24px', color: '#fff', marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
          <button
            className={`tab-btn ${inputMode === 'upload' ? 'active' : ''}`}
            onClick={() => setInputMode('upload')}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: '600',
              backgroundColor: inputMode === 'upload' ? '#6366f1' : '#312e81',
              color: '#fff',
            }}
          >
            📁 Upload Video từ Máy tính
          </button>
          <button
            className={`tab-btn ${inputMode === 'url' ? 'active' : ''}`}
            onClick={() => setInputMode('url')}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: '600',
              backgroundColor: inputMode === 'url' ? '#6366f1' : '#312e81',
              color: '#fff',
            }}
          >
            🌐 Dán Video URL
          </button>
        </div>

        {inputMode === 'upload' ? (
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Chọn file Video (MP4, WEBM, MOV, MKV):</label>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => setUploadFile(e.target.files[0])}
              style={{
                width: '100%',
                padding: '12px',
                background: '#0f172a',
                border: '1px dashed #6366f1',
                borderRadius: '8px',
                color: '#fff',
              }}
            />
          </div>
        ) : (
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Dán link/URL của video từ Internet:</label>
            <div style={{ display: 'flex', gap: '12px' }}>
              <input
                type="text"
                placeholder="https://example.com/video.mp4 hoặc https://www.youtube.com/watch?v=..."
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: '1px solid #4338ca',
                  background: '#0f172a',
                  color: '#fff',
                  fontSize: '14px',
                }}
              />
              <button
                onClick={handleCheckUrl}
                disabled={isCheckingUrl || !videoUrl}
                style={{
                  padding: '12px 20px',
                  borderRadius: '8px',
                  background: '#4f46e5',
                  color: '#fff',
                  border: 'none',
                  fontWeight: '600',
                  cursor: isCheckingUrl ? 'not-allowed' : 'pointer',
                }}
              >
                {isCheckingUrl ? 'Đang kiểm tra...' : '🔍 Kiểm tra Video'}
              </button>
            </div>

            {checkError && (
              <div style={{ marginTop: '12px', padding: '12px', background: '#7f1d1d', border: '1px solid #f87171', borderRadius: '8px', color: '#fca5a5' }}>
                {checkError}
              </div>
            )}

            {urlMetadata && (
              <div style={{ marginTop: '16px', padding: '16px', background: '#0f172a', borderRadius: '8px', border: '1px solid #22c55e' }}>
                <div style={{ color: '#4ade80', fontWeight: 'bold', marginBottom: '8px' }}>✓ Video Found</div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px', fontSize: '13px' }}>
                  <div><strong>Nguồn:</strong> {urlMetadata.source} ({urlMetadata.domain})</div>
                  <div><strong>Tiêu đề:</strong> {urlMetadata.title}</div>
                  <div><strong>Thời lượng:</strong> {formatTime(urlMetadata.duration)}</div>
                  <div><strong>Độ phân giải:</strong> {urlMetadata.width ? `${urlMetadata.width} × ${urlMetadata.height}` : 'Chưa rõ'}</div>
                  <div><strong>Định dạng:</strong> {urlMetadata.format?.toUpperCase()}</div>
                  <div><strong>Audio Track:</strong> {urlMetadata.audio_available ? 'Có audio ✓' : 'Không audio ❌'}</div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Configuration Options */}
      <div className="card" style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '24px', color: '#fff', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>⚙️ Cấu hình Dịch & Lồng tiếng</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '13px', marginBottom: '6px', color: '#94a3b8' }}>Ngôn ngữ đích (Target):</label>
            <select
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569' }}
            >
              <option value="vi">🇻🇳 Tiếng Việt (Vietnamese)</option>
              <option value="en">🇬🇧 Tiếng Anh (English)</option>
              <option value="ja">🇯🇵 Tiếng Nhật (Japanese)</option>
              <option value="ko">🇰🇷 Tiếng Hàn (Korean)</option>
              <option value="zh">🇨🇳 Tiếng Trung (Chinese)</option>
              <option value="fr">🇫🇷 Tiếng Pháp (French)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', marginBottom: '6px', color: '#94a3b8' }}>TTS Provider:</label>
            <select
              value={audioProviderId}
              onChange={(e) => setAudioProviderId(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569' }}
            >
              <option value="edge_tts">Edge TTS (Miễn phí / Tốc độ cao)</option>
              <option value="elevenlabs">ElevenLabs (Chất lượng cao)</option>
              <option value="google_tts">Google Cloud TTS</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', marginBottom: '6px', color: '#94a3b8' }}>Giọng đọc (Voice):</label>
            <select
              value={voiceId}
              onChange={(e) => setVoiceId(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569' }}
            >
              {voices.map(v => (
                <option key={v.id} value={v.id}>{v.name} ({v.gender})</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', marginBottom: '6px', color: '#94a3b8' }}>Âm thanh gốc (Original Audio):</label>
            <select
              value={originalAudioMode}
              onChange={(e) => setOriginalAudioMode(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569' }}
            >
              <option value="mute">Tắt hoàn toàn tiếng gốc (Mute)</option>
              <option value="duck">Giảm âm lượng gốc (Background Ducking 20%)</option>
              <option value="keep">Giữ âm thanh gốc trộn cùng tiếng đọc</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleStartImportAndTranslation}
          disabled={isProcessing}
          style={{
            marginTop: '20px',
            width: '100%',
            padding: '14px',
            borderRadius: '8px',
            background: 'linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%)',
            color: '#fff',
            fontWeight: 'bold',
            fontSize: '16px',
            border: 'none',
            cursor: isProcessing ? 'not-allowed' : 'pointer',
          }}
        >
          {isProcessing ? '⚡ Đang xử lý Pipeline...' : '🚀 Bắt đầu Nhập & Dịch Video'}
        </button>
      </div>

      {/* Error Message Card */}
      {(pipelineError || (job && job.status === 'failed')) && (
        <div style={{ marginBottom: '24px', padding: '20px', background: '#7f1d1d', border: '1px solid #ef4444', borderRadius: '12px', color: '#fee2e2' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', color: '#fca5a5' }}>
              ❌ Xử Lý Thất Bại (Job Failed)
            </h4>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={handleOpenLogs}
                style={{ padding: '6px 12px', borderRadius: '6px', background: '#451a03', color: '#fde68a', border: '1px solid #d97706', cursor: 'pointer', fontWeight: '600', fontSize: '12px' }}
              >
                📜 Xem Log Chi Tiết
              </button>
              <button
                onClick={handleRetryJob}
                style={{ padding: '6px 12px', borderRadius: '6px', background: '#d97706', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '12px' }}
              >
                🔄 Smart Retry
              </button>
            </div>
          </div>
          <div style={{ fontSize: '14px', fontFamily: 'monospace', background: '#450a0a', padding: '12px', borderRadius: '6px', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {job?.error_message || pipelineError || 'Xảy ra lỗi không xác định trong pipeline.'}
          </div>
        </div>
      )}

      {/* Real-time Tracking & Progress Panel */}
      {job && (
        <div className="card" style={{ background: '#0f172a', border: `1px solid ${job.status === 'failed' ? '#ef4444' : '#3b82f6'}`, borderRadius: '12px', padding: '24px', color: '#fff', marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: job.status === 'failed' ? '#fca5a5' : '#60a5fa', margin: 0 }}>
              📊 Tiến Trình Xử Lý Pipeline (Job: {job.job_id})
            </h3>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={handleOpenLogs}
                style={{
                  padding: '6px 14px',
                  borderRadius: '6px',
                  background: '#334155',
                  color: '#fff',
                  border: 'none',
                  cursor: 'pointer',
                  fontWeight: '600',
                  fontSize: '13px',
                }}
              >
                📜 Xem Log Chi Tiết
              </button>

              {['extracting_audio', 'stt', 'translating', 'generating_tts', 'syncing_audio', 'rendering'].includes(job.status) && (
                <button
                  onClick={handleCancelJob}
                  style={{
                    padding: '6px 14px',
                    borderRadius: '6px',
                    background: '#991b1b',
                    color: '#fff',
                    border: 'none',
                    cursor: 'pointer',
                    fontWeight: '600',
                    fontSize: '13px',
                  }}
                >
                  ❌ Hủy Xử Lý
                </button>
              )}

              {(job.status === 'failed' || job.status === 'stalled') && (
                <button
                  onClick={handleRetryJob}
                  style={{
                    padding: '6px 14px',
                    borderRadius: '6px',
                    background: '#d97706',
                    color: '#fff',
                    border: 'none',
                    cursor: 'pointer',
                    fontWeight: '600',
                    fontSize: '13px',
                  }}
                >
                  🔄 Smart Retry
                </button>
              )}
            </div>
          </div>

          {/* Heartbeat Status Badge */}
          <div style={{ marginBottom: '16px', padding: '10px 14px', background: '#1e293b', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>{getHeartbeatBadge(job)}</div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>
              Stage: <strong>{job.stage || 'QUEUED'}</strong> | Status: <strong>{job.status.toUpperCase()}</strong>
            </div>
          </div>

          {/* Overall Progress Bar */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
              <span>Tiến trình Tổng thể:</span>
              <span style={{ fontWeight: 'bold', color: job.status === 'failed' ? '#fca5a5' : '#60a5fa' }}>
                {job.overall_progress_pct}%
              </span>
            </div>
            <div style={{ background: '#1e293b', borderRadius: '8px', height: '14px', width: '100%', overflow: 'hidden' }}>
              <div
                style={{
                  width: `${job.overall_progress_pct}%`,
                  height: '100%',
                  background: job.status === 'failed' ? '#ef4444' : 'linear-gradient(90deg, #3b82f6, #8b5cf6)',
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
          </div>

          {/* Stage Detail Stats */}
          <div style={{ background: '#1e293b', borderRadius: '8px', padding: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', fontSize: '13px' }}>
            <div>
              <span style={{ color: '#94a3b8' }}>Bước hiện tại:</span>
              <div style={{ fontWeight: 'bold', color: job.status === 'failed' ? '#fca5a5' : '#e2e8f0', marginTop: '2px' }}>
                {job.current_step}
              </div>
            </div>

            <div>
              <span style={{ color: '#94a3b8' }}>Tiến trình Stage ({job.stage}):</span>
              <div style={{ fontWeight: 'bold', color: job.status === 'failed' ? '#ef4444' : '#a7f3d0', marginTop: '2px' }}>
                {job.stage_progress_pct}%
              </div>
            </div>

            <div>
              <span style={{ color: '#94a3b8' }}>FFmpeg Process Status:</span>
              <div style={{ fontWeight: 'bold', color: job.process?.status === 'RUNNING' ? '#60a5fa' : (job.process?.status === 'FAILED' ? '#ef4444' : '#94a3b8'), marginTop: '2px' }}>
                {job.process?.status === 'RUNNING' ? `RUNNING (PID: ${job.process.pid})` : (job.process?.status || 'IDLE')}
              </div>
            </div>

            {job.ffmpeg_stats && job.status !== 'failed' && (
              <>
                <div>
                  <span style={{ color: '#94a3b8' }}>Đã xử lý (FFmpeg):</span>
                  <div style={{ fontWeight: 'bold', color: '#facc15', marginTop: '2px' }}>
                    {formatTime(job.ffmpeg_stats.processed_seconds)} / {formatTime(job.ffmpeg_stats.total_duration)}
                  </div>
                </div>
                <div>
                  <span style={{ color: '#94a3b8' }}>Tốc độ & FPS:</span>
                  <div style={{ fontWeight: 'bold', color: '#e2e8f0', marginTop: '2px' }}>
                    Speed: {job.ffmpeg_stats.speed} | FPS: {job.ffmpeg_stats.fps}
                  </div>
                </div>
              </>
            )}

            {job.stage === 'GENERATING_TTS' && (
              <div>
                <span style={{ color: '#94a3b8' }}>Phân đoạn TTS:</span>
                <div style={{ fontWeight: 'bold', color: '#c084fc', marginTop: '2px' }}>
                  {job.completed_segments_count} / {job.total_segments_count} Phân đoạn
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Segment Editor when phase 1 completes */}
      {job && (job.status === 'segment_editing' || job.status === 'completed' || segments.length > 0) && (
        <div className="card" style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '24px', color: '#fff', marginBottom: '24px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '12px' }}>📝 Xem lại & Chỉnh sửa Văn Bản Dịch</h3>
          <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '20px' }}>
            Bạn có thể chỉnh sửa câu từ dịch của từng mốc thời gian trước khi tiến hành tạo giọng đọc TTS và Render video.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {segments.map((seg) => (
              <div key={seg.id} style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: '#818cf8', fontWeight: 'bold', fontSize: '13px' }}>
                  <span>Phân đoạn #{seg.number}</span>
                  <span>⏱ {formatTime(seg.start_time)} → {formatTime(seg.end_time)}</span>
                </div>
                <div style={{ fontSize: '13px', color: '#cbd5e1', marginBottom: '8px', fontStyle: 'italic' }}>
                  Gốc ({job.detected_language || 'Auto'}): "{seg.original_text}"
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Bản dịch ({targetLanguage.toUpperCase()}):</label>
                  <textarea
                    rows={2}
                    value={seg.translated_text}
                    onChange={(e) => handleSegmentTextChange(seg.id, e.target.value)}
                    style={{
                      width: '100%',
                      padding: '10px',
                      borderRadius: '6px',
                      background: '#1e293b',
                      color: '#fff',
                      border: '1px solid #475569',
                      fontSize: '14px',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          {job.status === 'segment_editing' && (
            <button
              onClick={handleRenderFinalVideo}
              disabled={isProcessing}
              style={{
                marginTop: '20px',
                width: '100%',
                padding: '14px',
                borderRadius: '8px',
                background: 'linear-gradient(90deg, #10b981 0%, #059669 100%)',
                color: '#fff',
                fontWeight: 'bold',
                fontSize: '16px',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              🎙️ Xác Nhận Bản Dịch & Render Video Lồng Tiếng
            </button>
          )}
        </div>
      )}

      {/* Final Dubbed Video Player */}
      {job && job.status === 'completed' && job.output_video_path && (
        <div className="card" style={{ background: '#064e3b', border: '1px solid #10b981', borderRadius: '12px', padding: '24px', color: '#fff' }}>
          <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#6ee7b7', marginBottom: '16px' }}>🎉 Video Lồng Tiếng Đã Hoàn Thành!</h3>
          <div style={{ width: '100%', borderRadius: '8px', overflow: 'hidden', marginBottom: '16px', background: '#000' }}>
            <video
              controls
              style={{ width: '100%', maxHeight: '500px' }}
              src={`/media/${job.output_video_path.replace(/^.*[\\\/]data[\\\/]/, '')}`}
            />
          </div>
          <a
            href={`/media/${job.output_video_path.replace(/^.*[\\\/]data[\\\/]/, '')}`}
            download="final_translated_video.mp4"
            style={{
              display: 'inline-block',
              padding: '12px 24px',
              borderRadius: '8px',
              background: '#10b981',
              color: '#fff',
              fontWeight: 'bold',
              textDecoration: 'none',
            }}
          >
            📥 Tải Xung Video Lồng Tiếng (MP4)
          </a>
        </div>
      )}

      {/* Log Terminal Modal */}
      {showLogModal && (
        <div
          style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '20px',
          }}
        >
          <div
            style={{
              background: '#090d16',
              border: '1px solid #3b82f6',
              borderRadius: '12px',
              width: '100%',
              maxWidth: '850px',
              maxHeight: '80vh',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
            }}
          >
            <div style={{ padding: '16px 20px', borderBottom: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', color: '#60a5fa' }}>
                📜 Job Execution Logs ({job?.job_id})
              </h3>
              <button
                onClick={() => setShowLogModal(false)}
                style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '20px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: '16px', flex: 1, overflowY: 'auto', background: '#020617', fontFamily: 'monospace', fontSize: '12px', color: '#38bdf8', whiteSpace: 'pre-wrap' }}>
              {isFetchingLogs ? 'Đang tải log...' : logsContent}
            </div>

            <div style={{ padding: '12px 20px', borderTop: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                {copySuccess && <span style={{ color: '#4ade80', fontSize: '13px' }}>✓ {copySuccess}</span>}
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                {job?.error_message && (
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(job.error_message);
                      setCopySuccess('Đã sao chép câu thông báo lỗi');
                      setTimeout(() => setCopySuccess(''), 2000);
                    }}
                    style={{ padding: '8px 16px', borderRadius: '6px', background: '#7f1d1d', color: '#fca5a5', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '13px' }}
                  >
                    ⚠️ Sao Chép Lỗi
                  </button>
                )}
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(logsContent);
                    setCopySuccess('Đã sao chép toàn bộ log');
                    setTimeout(() => setCopySuccess(''), 2000);
                  }}
                  style={{ padding: '8px 16px', borderRadius: '6px', background: '#334155', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '13px' }}
                >
                  📋 Sao Chép Full Log
                </button>
                <button
                  onClick={() => fetchLogs(job?.job_id)}
                  style={{ padding: '8px 16px', borderRadius: '6px', background: '#2563eb', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '13px' }}
                >
                  🔄 Làm Mới
                </button>
                <button
                  onClick={() => setShowLogModal(false)}
                  style={{ padding: '8px 16px', borderRadius: '6px', background: '#475569', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '13px' }}
                >
                  Đóng
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
