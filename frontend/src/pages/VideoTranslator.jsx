import React, { useState, useEffect, useRef } from 'react';
import { videoTranslatorApi, providersApi } from '../api';
import VideoEditorStudio from '../components/VideoEditorStudio';
import AIQCScorecard from '../components/AIQCScorecard';
import YouTubePublisherModal from '../components/YouTubePublisherModal';
import WorkflowTimeline from '../components/WorkflowTimeline';
import ProjectGlossaryManager from '../components/ProjectGlossaryManager';


export default function VideoTranslator({ initialJobId }) {
  const [showYouTubeModal, setShowYouTubeModal] = useState(false);
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
  const [llmProviderId, setLlmProviderId] = useState('gemini');
  const [voices, setVoices] = useState([]);
  const [voiceId, setVoiceId] = useState('vi-VN-HoaiMyNeural');
  const [originalAudioMode, setOriginalAudioMode] = useState('mute');

  // Job execution state
  const [asset, setAsset] = useState(null);
  const [job, setJob] = useState(null);
  const [segments, setSegments] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [pipelineError, setPipelineError] = useState(null);

  // Workflow engine state
  const [workflowStatusData, setWorkflowStatusData] = useState(null);

  const activeProjectId = job?.project_id || asset?.project_id || 'default_project';

  const fetchWorkflowStatus = async (projectId) => {
    try {
      const res = await fetch(`/api/video-translator/projects/${projectId || activeProjectId}/workflow-status`);
      const data = await res.json();
      if (data.success) {
        setWorkflowStatusData(data.data);
      }
    } catch (err) {
      console.error('Failed fetching workflow status', err);
    }
  };

  const handleStartWorkflow = async () => {
    try {
      await fetch(`/api/video-translator/projects/${activeProjectId}/workflow/start`, { method: 'POST' });
      fetchWorkflowStatus(activeProjectId);
    } catch (err) {
      console.error('Failed starting workflow', err);
    }
  };

  const handlePauseWorkflow = async () => {
    try {
      await fetch(`/api/video-translator/projects/${activeProjectId}/workflow/pause`, { method: 'POST' });
      fetchWorkflowStatus(activeProjectId);
    } catch (err) {
      console.error('Failed pausing workflow', err);
    }
  };

  const handleResumeWorkflow = async () => {
    try {
      await fetch(`/api/video-translator/projects/${activeProjectId}/workflow/resume`, { method: 'POST' });
      fetchWorkflowStatus(activeProjectId);
    } catch (err) {
      console.error('Failed resuming workflow', err);
    }
  };

  // Initial Job ID effect
  useEffect(() => {
    if (initialJobId) {
      videoTranslatorApi.getJob(initialJobId).then(res => {
        if (res.success && res.data) {
          setJob(res.data);
          if (res.data.segments) setSegments(res.data.segments);
          fetchWorkflowStatus(res.data.project_id || res.data.id);
        }
      }).catch(err => console.error('Failed to load initial job:', err));
    }
  }, [initialJobId]);


  // Log Modal state
  const [showLogModal, setShowLogModal] = useState(false);
  const [logsContent, setLogsContent] = useState('');
  const [isFetchingLogs, setIsFetchingLogs] = useState(false);
  const [copySuccess, setCopySuccess] = useState('');

  // Polling ref & Timestamps
  const pollingRef = useRef(null);
  const [lastPollTime, setLastPollTime] = useState(null);
  const [lastApiResponseTime, setLastApiResponseTime] = useState(null);

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

  const activeJobId = job?.id || job?.job_id;
  const lastPollTimestampRef = useRef(0);

  // Single Source of Truth Polling Effect
  useEffect(() => {
    if (!activeJobId) return;

    if (['completed', 'failed', 'cancelled', 'segment_editing'].includes(job?.status)) {
      if (isProcessing) setIsProcessing(false);
    }

    const isFinalTerminal = ['completed', 'failed', 'cancelled'].includes(job?.status);
    if (isFinalTerminal) return;

    const fetchJobStatus = () => {
      const reqTimestamp = Date.now();
      const nowStr = new Date().toLocaleTimeString('vi-VN');
      setLastPollTime(nowStr);
      console.log(`[JOB POLL] Job ID: ${activeJobId} | Request time: ${nowStr}`);

      videoTranslatorApi.getJob(activeJobId)
        .then(res => {
          const respTimeStr = new Date().toLocaleTimeString('vi-VN');
          setLastApiResponseTime(respTimeStr);

          if (res.success && res.data) {
            const rawData = res.data;
            const newJob = {
              ...rawData,
              id: rawData.id || rawData.job_id,
            };

            console.log(`[JOB POLL RESPONSE] Job: ${newJob.id} | Status: ${newJob.status} | Stage: ${newJob.stage} | Overall: ${newJob.overall_progress_pct}% | StagePct: ${newJob.stage_progress_pct}% | Heartbeat: ${newJob.heartbeat?.active} | FFmpeg: ${newJob.process?.status} | Segments: ${newJob.segments?.length || 0}`);

            // Stale response check: reject if request is older than latest received
            if (reqTimestamp < lastPollTimestampRef.current) {
              console.warn('[JOB POLL] Ignoring stale response');
              return;
            }
            lastPollTimestampRef.current = reqTimestamp;

            setJob(prev => {
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
            }

            if (['completed', 'failed', 'cancelled'].includes(newJob.status)) {
              if (pollingRef.current) clearInterval(pollingRef.current);
            }
          }
        })
        .catch(err => {
          console.error('[JOB POLL ERROR]', err);
        });
    };

    fetchJobStatus();
    pollingRef.current = setInterval(fetchJobStatus, 1500);

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [activeJobId, job?.status]);

  const formatApiError = (err, defaultMsg) => {
    const status = err.response?.status ? `[HTTP ${err.response.status}] ` : '';
    const method = err.config?.method ? err.config.method.toUpperCase() + ' ' : '';
    const url = err.config?.url ? err.config.url + '\n' : '';
    const serverDetail = err.response?.data?.detail;
    const errorMsg = err.response?.data?.error || err.message;

    let detailStr = '';
    if (serverDetail) {
      detailStr = typeof serverDetail === 'object' ? JSON.stringify(serverDetail, null, 2) : serverDetail;
    } else if (errorMsg) {
      detailStr = errorMsg;
    } else {
      detailStr = defaultMsg;
    }
    return `${status}${method}${url}Lỗi: ${detailStr}`;
  };

  const fetchLogs = async (jobId) => {
    const targetId = jobId || activeJobId;
    if (!targetId) {
      setLogsContent(
        pipelineError
          ? `⚠️ Chưa có Job ID được gán (Khởi tạo Job thất bại).\n\n[Chi Tiết Lỗi Request/Pipeline]:\n${pipelineError}`
          : 'Chưa có thông tin Job ID hoặc log execution.'
      );
      return;
    }
    setIsFetchingLogs(true);
    try {
      const res = await videoTranslatorApi.getLogs(targetId);
      if (res.success) {
        setLogsContent(res.data.logs || 'Chưa có dữ liệu log.');
      }
    } catch (err) {
      const errFormatted = formatApiError(err, 'Lỗi không thể lấy log từ server');
      setLogsContent(
        `Không thể tải log từ server cho Job ID (${targetId}):\n${errFormatted}\n\n[Chi Tiết Lỗi Pipeline Hiển Thị]:\n${pipelineError || job?.error_message || 'N/A'}`
      );
    } finally {
      setIsFetchingLogs(false);
    }
  };

  const handleOpenLogs = () => {
    setShowLogModal(true);
    fetchLogs(activeJobId);
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
      setCheckError(formatApiError(err, 'Lỗi kiểm tra URL'));
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
        llm_provider_id: llmProviderId,
        voice_id: voiceId,
        original_audio_mode: originalAudioMode,
      });

      const newJobId = jobRes.data.job_id || jobRes.data.id;
      // Immediately set job state so activeJobId is populated before startJob completes
      const initialPendingJob = {
        id: newJobId,
        job_id: newJobId,
        status: 'created',
        stage: 'QUEUED',
        overall_progress_pct: 0,
        stage_progress_pct: 0,
        current_step: 'Đang bắt đầu pipeline...',
      };
      setJob(initialPendingJob);

      await videoTranslatorApi.startJob(newJobId);
      const initialJob = await videoTranslatorApi.getJob(newJobId);
      const normalizedInitial = {
        ...initialJob.data,
        id: initialJob.data.id || initialJob.data.job_id,
      };
      setJob(normalizedInitial);
      if (normalizedInitial.segments && normalizedInitial.segments.length > 0) {
        setSegments(normalizedInitial.segments);
      }
    } catch (err) {
      const detail = formatApiError(err, 'Không thể bắt đầu dịch video');
      setPipelineError(detail);
      setIsProcessing(false);
    }
  };

  const handleSegmentTextChange = (segmentId, text) => {
    setSegments(prev => prev.map(s => s.id === segmentId ? { ...s, translated_text: text } : s));
  };

  const handleRenderFinalVideo = async () => {
    if (!activeJobId) return;
    setIsProcessing(true);
    setPipelineError(null);

    try {
      const updateItems = segments.map(s => ({ id: s.id, translated_text: s.translated_text }));
      await videoTranslatorApi.updateSegments(activeJobId, updateItems);
      await videoTranslatorApi.renderFinalVideo(activeJobId);
      const updatedJob = await videoTranslatorApi.getJob(activeJobId);
      const normalizedUpdated = {
        ...updatedJob.data,
        id: updatedJob.data.id || updatedJob.data.job_id,
      };
      setJob(normalizedUpdated);
    } catch (err) {
      const detail = formatApiError(err, 'Lỗi render video');
      setPipelineError(detail);
      setIsProcessing(false);
    }
  };

  const handleCancelJob = async () => {
    if (!activeJobId) return;
    try {
      await videoTranslatorApi.cancelJob(activeJobId);
      const res = await videoTranslatorApi.getJob(activeJobId);
      if (res.success) {
        const normalized = {
          ...res.data,
          id: res.data.id || res.data.job_id,
        };
        setJob(normalized);
      }
    } catch (err) {
      alert('Không thể hủy job: ' + formatApiError(err, 'Lỗi hệ thống'));
    }
  };

  const handleRetryJob = async () => {
    if (!activeJobId) return;
    setIsProcessing(true);
    setPipelineError(null);
    try {
      await videoTranslatorApi.retryJob(activeJobId);
      const res = await videoTranslatorApi.getJob(activeJobId);
      if (res.success) {
        const normalized = {
          ...res.data,
          id: res.data.id || res.data.job_id,
        };
        setJob(normalized);
      }
    } catch (err) {
      setPipelineError('Không thể thử lại job: ' + formatApiError(err, 'Lỗi hệ thống'));
      setIsProcessing(false);
    }
  };

  const formatTime = (sec) => {
    if (!sec || isNaN(sec)) return '00:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const getHeartbeatBadge = (currentJob) => {
    if (!currentJob) return null;
    const status = currentJob.status;
    const heartbeat = currentJob.heartbeat || {};
    const ageSec = heartbeat.age_seconds ?? 999;

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
    if (status === 'segment_editing') {
      return (
        <span style={{ color: '#6ee7b7', fontSize: '13px', fontWeight: 'bold' }}>
          🟢 Phase 1 Hoàn Thành (Đang chờ bạn xác nhận phân đoạn)
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

    if (heartbeat.active && ageSec <= 15) {
      return (
        <span style={{ color: '#4ade80', fontSize: '13px', fontWeight: 'bold' }}>
          🟢 Worker đang hoạt động (Cập nhật {Math.round(ageSec)}s trước)
        </span>
      );
    }
    if (ageSec <= 45) {
      return (
        <span style={{ color: '#facc15', fontSize: '13px', fontWeight: 'bold' }}>
          🟡 Đang xử lý / Chờ server... (Cập nhật {Math.round(ageSec)}s trước)
        </span>
      );
    }
    return (
      <span style={{ color: '#94a3b8', fontSize: '13px', fontWeight: 'bold' }}>
        ⚪ Worker đã dừng (Dừng heartbeat)
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

      {/* Visual 6-Stage Workflow Timeline */}
      <WorkflowTimeline
        projectId={activeProjectId}
        statusData={workflowStatusData || {
          current_stage: job?.stage || 'INGEST',
          current_step: job?.current_step || 'Ready',
          stages: [
            { name: 'INGEST', status: job ? 'passed' : 'pending' },
            { name: 'ANALYZE', status: job?.stage === 'TRANSLATING' || job?.status === 'completed' ? 'passed' : job?.stage === 'TRANSCRIBING' ? 'running' : 'pending' },
            { name: 'TRANSLATE', status: job?.stage === 'SYNTHESIZING' || job?.status === 'completed' ? 'passed' : job?.stage === 'TRANSLATING' ? 'running' : 'pending' },
            { name: 'DUB', status: job?.stage === 'RENDERING' || job?.status === 'completed' ? 'passed' : job?.stage === 'SYNTHESIZING' ? 'running' : 'pending' },
            { name: 'PRODUCE', status: job?.status === 'completed' ? 'passed' : job?.stage === 'RENDERING' ? 'running' : 'pending' },
            { name: 'PUBLISH', status: 'pending' },
          ]
        }}
        onStart={handleStartWorkflow}
        onPause={handlePauseWorkflow}
        onResume={handleResumeWorkflow}
      />

      {/* Input Selection Card */}
      <div className="card" style={{ background: '#1e1b4b', border: '1px solid #3730a3', borderRadius: '12px', padding: '24px', color: '#fff', marginBottom: '24px' }}>

        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
          <button
            onClick={() => setInputMode('url')}
            style={{
              flex: 1,
              padding: '12px',
              borderRadius: '8px',
              border: inputMode === 'url' ? '2px solid #818cf8' : '1px solid #4338ca',
              background: inputMode === 'url' ? '#312e81' : '#1e1b4b',
              color: '#fff',
              fontWeight: 'bold',
              cursor: 'pointer',
            }}
          >
            🔗 Dán Link/URL Video
          </button>
          <button
            onClick={() => setInputMode('upload')}
            style={{
              flex: 1,
              padding: '12px',
              borderRadius: '8px',
              border: inputMode === 'upload' ? '2px solid #818cf8' : '1px solid #4338ca',
              background: inputMode === 'upload' ? '#312e81' : '#1e1b4b',
              color: '#fff',
              fontWeight: 'bold',
              cursor: 'pointer',
            }}
          >
            📁 Upload File từ Máy
          </button>
        </div>

        {inputMode === 'url' ? (
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: '#cbd5e1' }}>
              Nhập Đường Dẫn Video (Direct MP4, YouTube, Bilibili, TikTok...):
            </label>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                placeholder="https://example.com/video.mp4"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                style={{
                  flex: 1,
                  padding: '12px',
                  borderRadius: '6px',
                  border: '1px solid #475569',
                  background: '#0f172a',
                  color: '#fff',
                }}
              />
              <button
                onClick={handleCheckUrl}
                disabled={isCheckingUrl || !videoUrl}
                style={{
                  padding: '12px 20px',
                  borderRadius: '6px',
                  background: '#4f46e5',
                  color: '#fff',
                  border: 'none',
                  fontWeight: 'bold',
                  cursor: isCheckingUrl ? 'not-allowed' : 'pointer',
                }}
              >
                {isCheckingUrl ? 'Đang kiểm tra...' : '🔍 Kiểm tra URL'}
              </button>
            </div>
            {checkError && (
              <div style={{ color: '#ef4444', fontSize: '13px', marginTop: '8px' }}>
                {checkError}
              </div>
            )}
            {urlMetadata && (
              <div style={{ marginTop: '12px', padding: '12px', background: '#0f172a', borderRadius: '6px', fontSize: '13px', border: '1px solid #334155' }}>
                <div style={{ color: '#4ade80', fontWeight: 'bold', marginBottom: '4px' }}>✓ Metadata Hợp Lệ</div>
                <div><strong>Tiêu đề:</strong> {urlMetadata.title}</div>
                <div><strong>Thời lượng:</strong> {formatTime(urlMetadata.duration)} ({urlMetadata.duration}s)</div>
              </div>
            )}
          </div>
        ) : (
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: '#cbd5e1' }}>
              Chọn File Video (MP4, MOV, MKV, AVI):
            </label>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => setUploadFile(e.target.files[0] || null)}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '6px',
                border: '1px solid #475569',
                background: '#0f172a',
                color: '#fff',
              }}
            />
          </div>
        )}
      </div>

      {/* Configuration Options */}
      <div className="card" style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '24px', color: '#fff', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>⚙️ Cấu hình Dịch & Lồng tiếng</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '13px', marginBottom: '6px', color: '#94a3b8' }}>LLM / Script Provider:</label>
            <select
              value={llmProviderId}
              onChange={(e) => setLlmProviderId(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569' }}
            >
              <option value="gemini">✨ Google Gemini AI Studio (Mặc định)</option>
              <option value="openai">🤖 OpenAI ChatGPT</option>
            </select>
          </div>

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

      {/* Project Glossary Manager */}
      <ProjectGlossaryManager projectId={activeProjectId} />

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
              📊 Tiến Trình Xử Lý Pipeline (Job: {job.id || job.job_id})
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
              Stage: <strong>{job.stage || 'QUEUED'}</strong> | Status: <strong>{(job.status || '').toUpperCase()}</strong>
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
              <div style={{ fontWeight: 'bold', color: job.process?.status === 'RUNNING' ? '#60a5fa' : (job.process?.status === 'COMPLETED' ? '#4ade80' : (job.process?.status === 'FAILED' ? '#ef4444' : '#94a3b8')), marginTop: '2px' }}>
                {job.process?.status === 'RUNNING' ? `⚡ RUNNING (PID: ${job.process.pid})` : (job.process?.status === 'COMPLETED' ? '✅ COMPLETED' : (job.process?.status || 'IDLE'))}
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

          {/* DEBUG JOB STATE PANEL (Dev Mode Single Source of Truth) */}
          <details open style={{ marginTop: '20px', padding: '14px 18px', background: '#020617', border: '1px solid #1e293b', borderRadius: '10px', fontSize: '12px', fontFamily: 'monospace', color: '#38bdf8' }}>
            <summary style={{ cursor: 'pointer', fontWeight: 'bold', color: '#facc15', fontSize: '14px' }}>🐞 DEBUG JOB STATE (Single Source of Truth)</summary>
            <div style={{ marginTop: '12px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '10px' }}>
              <div>Job ID: <strong style={{ color: '#fff' }}>{job.id || job.job_id}</strong></div>
              <div>Backend Status: <strong style={{ color: '#a7f3d0' }}>{job.status}</strong></div>
              <div>Backend Stage: <strong style={{ color: '#60a5fa' }}>{job.stage}</strong></div>
              <div>Overall Progress: <strong style={{ color: '#facc15' }}>{job.overall_progress_pct}%</strong></div>
              <div>Stage Progress: <strong style={{ color: '#facc15' }}>{job.stage_progress_pct}%</strong></div>
              <div>Heartbeat Active: <strong style={{ color: job.heartbeat?.active ? '#4ade80' : '#f87171' }}>{job.heartbeat?.active ? 'ACTIVE (TRUE)' : 'INACTIVE (FALSE)'}</strong> ({job.heartbeat?.age_seconds ?? 'N/A'}s)</div>
              <div>FFmpeg Status: <strong style={{ color: job.process?.status === 'COMPLETED' ? '#4ade80' : '#60a5fa' }}>{job.process?.status || 'IDLE'}</strong> (PID: {job.process?.pid || 'N/A'})</div>
              <div>STT Status: <strong style={{ color: job.stt?.status === 'COMPLETED' ? '#4ade80' : '#60a5fa' }}>{job.stt?.status || 'PENDING'}</strong> ({job.stt?.provider || 'gemini'})</div>
              <div>Detected Language: <strong style={{ color: '#fbbf24' }}>{job.detected_language || 'Auto'}</strong></div>
              <div>Translation Status: <strong style={{ color: job.translation?.status === 'COMPLETED' ? '#4ade80' : '#60a5fa' }}>{job.translation?.status || 'PENDING'}</strong></div>
              <div>Segments Loaded: <strong style={{ color: '#c084fc' }}>{segments.length} / {job.total_segments_count || segments.length}</strong></div>
              <div>Last Backend Update: <strong style={{ color: '#cbd5e1' }}>{job.updated_at ? new Date(job.updated_at).toLocaleTimeString('vi-VN') : 'N/A'}</strong></div>
              <div>Last Frontend Poll: <strong style={{ color: '#cbd5e1' }}>{lastPollTime || 'N/A'}</strong></div>
              <div>API Response Time: <strong style={{ color: '#cbd5e1' }}>{lastApiResponseTime || 'N/A'}</strong></div>
            </div>
          </details>
        </div>
      )}

      {/* Segment Editor when phase 1 completes */}
      {job && (job.status === 'segment_editing' || job.status === 'completed' || segments.length > 0) && (
        <div className="card" style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '24px', color: '#fff', marginBottom: '24px' }}>
          <div style={{ marginBottom: '20px', padding: '16px 20px', background: '#064e3b', border: '1px solid #10b981', borderRadius: '10px', color: '#a7f3d0' }}>
            <h4 style={{ margin: '0 0 6px 0', fontSize: '16px', fontWeight: 'bold', color: '#6ee7b7' }}>
              🟢 Phase 1 Hoàn Thành – Đã Trích Xuất & Dịch Phân Đoạn!
            </h4>
            <p style={{ margin: 0, fontSize: '13px' }}>
              Hệ thống đã nhận diện giọng nói và dịch thành công <strong>{segments.length}</strong> phân đoạn. Vui lòng xem lại và chỉnh sửa bản dịch dưới đây trước khi xác nhận render video lồng tiếng.
            </p>
          </div>

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
      {job && job.status === 'completed' && (job.output_url || job.output_video_path) && (
        <div className="card" style={{ background: '#064e3b', border: '1px solid #10b981', borderRadius: '12px', padding: '24px', color: '#fff' }}>
          <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#6ee7b7', marginBottom: '16px' }}>🎉 Video Lồng Tiếng Đã Hoàn Thành!</h3>
          <div style={{ width: '100%', borderRadius: '8px', overflow: 'hidden', marginBottom: '16px', background: '#000' }}>
            <video
              controls
              style={{ width: '100%', maxHeight: '500px' }}
              src={job.output_url || `/media/${job.output_video_path.replace(/^.*[\\\/]data[\\\/]/, '')}`}
            />
          </div>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <a
              href={job.output_url || `/media/${job.output_video_path.replace(/^.*[\\\/]data[\\\/]/, '')}`}
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
              📥 Tải Video Lồng Tiếng (MP4)
            </a>
            <button
              onClick={() => setShowYouTubeModal(true)}
              style={{
                padding: '12px 24px',
                borderRadius: '8px',
                background: '#f43f5e',
                color: '#fff',
                fontWeight: 'bold',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              🔴 Tự Động SEO & Đăng Bài YouTube
            </button>
          </div>

          {/* AI QC Scorecard */}
          <AIQCScorecard jobId={job.id} />

          {/* Video Editing & Branding Automation Studio */}
          <VideoEditorStudio jobId={job.id} />
        </div>
      )}

      {/* YouTube Publisher Modal */}
      {showYouTubeModal && job && (
        <YouTubePublisherModal
          jobId={job.id}
          onClose={() => setShowYouTubeModal(false)}
        />
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
                📜 Job Execution Logs ({job?.id || job?.job_id})
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
                  onClick={() => fetchLogs(job?.id || job?.job_id)}
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
