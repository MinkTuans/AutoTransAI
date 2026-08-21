import React, { useState, useEffect } from 'react';
import { videoTranslatorApi, providersApi } from '../api';

export default function VideoTranslator() {
  const [inputMode, setInputMode] = useState('url'); // 'url' or 'upload'
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

  // Polling for job updates
  useEffect(() => {
    let timer;
    if (job && (job.status !== 'completed' && job.status !== 'failed' && job.status !== 'segment_editing')) {
      timer = setInterval(() => {
        videoTranslatorApi.getJob(job.id)
          .then(res => {
            if (res.success) {
              setJob(res.data);
              if (res.data.segments) {
                setSegments(res.data.segments);
              }
            }
          })
          .catch(console.error);
      }, 2000);
    }
    return () => clearInterval(timer);
  }, [job]);

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

      // Create translation job
      const jobRes = await videoTranslatorApi.createJob({
        asset_id: importedAsset.asset_id,
        source_language: 'auto',
        target_language: targetLanguage,
        audio_provider_id: audioProviderId,
        voice_id: voiceId,
        original_audio_mode: originalAudioMode,
      });

      const newJobId = jobRes.data.job_id;

      // Start phase 1
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
      // Save edited segments first
      await videoTranslatorApi.updateSegments(
        job.id,
        segments.map(s => ({ id: s.id, translated_text: s.translated_text }))
      );

      // Trigger render
      await videoTranslatorApi.renderJob(job.id);
      const updated = await videoTranslatorApi.getJob(job.id);
      setJob(updated.data);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Lỗi render video';
      setPipelineError(detail);
    }
  };

  const formatTime = (seconds) => {
    if (!seconds) return '00:00';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="video-translator-container" style={{ padding: '24px', maxWidth: '1100px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px', background: 'linear-[#4f46e5,#7c3aed]', WebkitBackgroundClip: 'text' }}>
        🎬 Video Translator – Dịch & Lồng tiếng Video
      </h1>
      <p style={{ color: '#6b7280', marginBottom: '24px' }}>
        Tự động dịch giọng nói trong video từ URL Internet hoặc file Upload, chuyển ngữ bằng AI và lồng tiếng chuẩn khớp thời lượng.
      </p>

      {/* Input Selection Box */}
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

      {pipelineError && (
        <div style={{ marginBottom: '24px', padding: '16px', background: '#7f1d1d', border: '1px solid #ef4444', borderRadius: '8px', color: '#fee2e2' }}>
          <strong>Lỗi Xử Lý:</strong> {pipelineError}
        </div>
      )}

      {/* Live Pipeline Steps Progress */}
      {job && (
        <div className="card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '24px', color: '#fff', marginBottom: '24px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>📊 Tiến Trình Xử Lý Pipeline</h3>
          <div style={{ background: '#1e293b', borderRadius: '8px', height: '12px', width: '100%', overflow: 'hidden', marginBottom: '16px' }}>
            <div
              style={{
                width: `${job.progress_pct}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #3b82f6, #8b5cf6)',
                transition: 'width 0.5s ease',
              }}
            />
          </div>
          <div style={{ fontSize: '14px', color: '#a7f3d0', fontWeight: '600' }}>
            {job.current_step} ({job.progress_pct}%)
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
              disabled={isProcessing && job.status === 'rendering'}
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
    </div>
  );
}
