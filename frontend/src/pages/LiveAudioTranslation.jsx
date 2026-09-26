import React, { useEffect, useState } from 'react';
import { liveAudioApi } from '../api';

const ACTIVE = new Set(['queued', 'converting', 'connecting', 'streaming', 'muxing']);
const STORED_JOB_KEY = 'autotrans_live_audio_job_id';
const STATUS = {
  queued: 'Đang chờ', converting: 'Đang chuẩn bị âm thanh',
  connecting: 'Đang kết nối Gemini Live', streaming: 'Đang dịch âm thanh',
  muxing: 'Đang ghép âm thanh vào video',
  completed: 'Hoàn tất', failed: 'Thất bại', cancelled: 'Đã hủy',
};
const ERRORS = {
  feature_disabled: 'Tính năng Live Audio Translation đang tắt trong cấu hình.',
  missing_api_key: 'Chưa có key Gemini đang bật trong AI Provider Catalog hoặc GEMINI_LIVE_TRANSLATE_API_KEY.',
  credential_unavailable: 'Không đọc được key Gemini đã lưu. Hãy kiểm tra kho credential của ứng dụng.',
  model_unavailable: 'Model Gemini Live Translate hiện không khả dụng.',
  unsupported_audio_format: 'Định dạng audio không được hỗ trợ.',
  unsupported_video_format: 'Video MP4 không hợp lệ hoặc không có hình.',
  video_has_no_audio: 'Video không có track tiếng để dịch.',
  video_processing_failed: 'Không thể tách tiếng hoặc ghép video bằng FFmpeg.',
  audio_too_large: 'File audio vượt giới hạn 25 MB.',
  video_too_large: 'File video vượt giới hạn 250 MB.',
  session_limit: 'Đã đạt giới hạn phiên hoặc audio dài quá 5 phút.',
  quota_or_rate_limit: 'Gemini đã đạt hạn mức hoặc giới hạn tốc độ.',
  connection_failure: 'Không thể kết nối tới Gemini Live.',
  timeout: 'Phiên Gemini Live đã hết thời gian chờ.',
  malformed_response: 'Gemini Live trả về dữ liệu âm thanh không hợp lệ.',
  no_translated_audio: 'Gemini Live không trả về âm thanh đã dịch.',
  converter_unavailable: 'Cần FFmpeg và FFprobe để xử lý file audio.',
  conversion_timeout: 'Chuyển đổi file audio quá thời gian cho phép.',
};

function safeError(code) {
  return ERRORS[code] || 'Không thể hoàn tất phiên dịch audio. Vui lòng thử lại.';
}

export default function LiveAudioTranslation() {
  const [file, setFile] = useState(null);
  const [job, setJob] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const id = localStorage.getItem(STORED_JOB_KEY);
    if (!id) return undefined;
    let active = true;
    liveAudioApi.status(id).then(response => {
      if (!active) return;
      setJob(response.data);
      if (response.data.status === 'failed') setError(safeError(response.data.error_code));
    }).catch(() => {
      if (active) localStorage.removeItem(STORED_JOB_KEY);
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!job?.id || !ACTIVE.has(job.status)) return undefined;
    let active = true;
    const timer = setInterval(async () => {
      try {
        const response = await liveAudioApi.status(job.id);
        if (!active) return;
        setJob(response.data);
        if (response.data.status === 'failed') setError(safeError(response.data.error_code));
      } catch (failure) {
        if (!active) return;
        if (failure.response?.status === 404) {
          localStorage.removeItem(STORED_JOB_KEY);
          setJob(null);
          setError('Phiên dịch không còn trên máy chủ. Bạn có thể bắt đầu phiên mới.');
        } else {
          setError('Không thể cập nhật trạng thái phiên dịch.');
        }
      }
    }, 1000);
    return () => { active = false; clearInterval(timer); };
  }, [job?.id, job?.status]);

  const start = async (event) => {
    event.preventDefault();
    if (!file) {
      setError('Hãy chọn file audio trước khi bắt đầu.');
      return;
    }
    setBusy(true);
    setError('');
    setJob(null);
    try {
      const created = await liveAudioApi.start(file);
      setJob(created.data);
      localStorage.setItem(STORED_JOB_KEY, created.data.id);
      const response = await liveAudioApi.status(created.data.id);
      setJob(response.data);
      if (response.data.status === 'failed') setError(safeError(response.data.error_code));
    } catch (failure) {
      setError(safeError(failure.response?.data?.detail));
    } finally {
      setBusy(false);
    }
  };

  const cancel = async () => {
    if (!job?.id) return;
    try {
      const response = await liveAudioApi.cancel(job.id);
      setJob(response.data);
    } catch (_error) {
      setError('Không thể dừng phiên dịch audio.');
    }
  };

  const audioUrl = job?.status === 'completed' && job?.media_type !== 'video'
    ? liveAudioApi.audioUrl(job.id) : null;
  const videoUrl = job?.status === 'completed' && job?.media_type === 'video'
    ? liveAudioApi.videoUrl(job.id) : null;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Live Audio / Video Translation</h1>
        <p className="page-subtitle">Audio hoặc Video → Gemini Live Translate → âm thanh tiếng Việt</p>
      </div>
      <section className="card" style={{ maxWidth: 720 }}>
        <form onSubmit={start}>
          <label htmlFor="live-audio-file">Upload Audio or Video</label>
          <input id="live-audio-file" type="file"
            accept=".wav,.mp3,.m4a,.flac,.ogg,.webm,.mp4"
            onChange={event => setFile(event.target.files?.[0] || null)} />
          <p className="page-subtitle">Audio: WAV, MP3, M4A, FLAC, OGG, WebM (25 MB). Video: MP4 (250 MB). Tối đa 5 phút.</p>
          <p className="page-subtitle">Video giữ nguyên hình và thay tiếng gốc bằng tiếng Việt; lời dịch có thể lệch nhịp với cảnh.</p>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', margin: '20px 0' }}>
            <div>
              <label htmlFor="live-source">Source Language</label>
              <select id="live-source" aria-label="Source Language" value="auto" disabled>
                <option value="auto">Tự động nhận diện (Gemini)</option>
              </select>
            </div>
            <div>
              <label htmlFor="live-target">Target Language</label>
              <select id="live-target" aria-label="Target Language" value="vi" disabled>
                <option value="vi">Tiếng Việt</option>
              </select>
            </div>
          </div>
          <button className="btn btn-primary" type="submit" disabled={busy || ACTIVE.has(job?.status)}>
            Start Translation
          </button>
          {ACTIVE.has(job?.status) && <button className="btn btn-secondary" type="button"
            onClick={cancel} style={{ marginLeft: 12 }}>Kết thúc phiên</button>}
        </form>
        {job && <p role="status" style={{ marginTop: 20 }}>Trạng thái phiên: {STATUS[job.status] || job.status}</p>}
        {error && <p role="alert" style={{ color: 'var(--danger)' }}>{error}</p>}
        {audioUrl && <div style={{ marginTop: 24 }}>
          <h2>Âm thanh tiếng Việt</h2>
          <audio aria-label="Âm thanh tiếng Việt" controls src={audioUrl} style={{ width: '100%' }} />
          <p><a href={audioUrl} download={`live-translation-${job.id}.wav`}>
            Download translated audio
          </a></p>
        </div>}
        {videoUrl && <div style={{ marginTop: 24 }}>
          <h2>Video tiếng Việt</h2>
          <video aria-label="Video tiếng Việt" controls src={videoUrl} style={{ width: '100%' }} />
          <p><a href={videoUrl} download={`live-translation-${job.id}.mp4`}>
            Download translated video
          </a></p>
        </div>}
      </section>
    </div>
  );
}
