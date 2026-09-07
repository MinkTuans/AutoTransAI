import React, { useState, useEffect } from 'react';
import { thumbnailApi } from '../api';
import { LoadingSpinner, ButtonSpinner } from './LoadingSpinner';

const STYLE_OPTIONS = [
  { value: 'auto', label: '🤖 Tự động (Phân tích cảm xúc kịch bản)' },
  { value: 'cinematic', label: '🎬 Cinematic (Điện ảnh kịch tính)' },
  { value: 'youtube_viral', label: '🚀 YouTube Viral (Bắt mắt, biểu cảm mạnh)' },
  { value: 'horror', label: '👻 Horror (U tối, bí ẩn, kinh dị)' },
  { value: 'anime', label: '🌸 Anime Nhật Bản (Nhiều màu sắc)' },
  { value: 'realistic', label: '📸 Realistic (Ảnh chụp 8K chân thực)' },
  { value: 'cartoon', label: '🎨 Cartoon 3D (Hoạt hình 3D)' },
  { value: 'documentary', label: '📜 Documentary (Phim tài liệu)' },
  { value: 'minimal', label: '📐 Minimal (Tối giản, tương phản)' },
  { value: 'movie_poster', label: '🍿 Poster Phim Hollywood' },
];

const PROVIDER_OPTIONS = [
  { value: 'pollinations', label: '⚡ Pollinations AI (Miễn phí & Nhanh)' },
  { value: 'fal', label: '🎨 fal.ai FLUX (Chất lượng cao)' },
  { value: 'openai', label: '🤖 OpenAI DALL-E 3' },
  { value: 'local_image', label: '🖼️ Local Scenery (Offline)' },
];

export default function AIThumbnailPanel({
  projectId,
  jobId,
  assetId,
  initialThumbnailUrl,
  onThumbnailUpdated,
}) {
  const [activeThumbnail, setActiveThumbnail] = useState(null);
  const [historyList, setHistoryList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [selectedStyle, setSelectedStyle] = useState('auto');
  const [customInstruction, setCustomInstruction] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('pollinations');
  const [errorMsg, setErrorMsg] = useState(null);

  const [showPromptModal, setShowPromptModal] = useState(false);
  const [showZoomModal, setShowZoomModal] = useState(false);

  useEffect(() => {
    loadThumbnails();
  }, [projectId, jobId, assetId]);

  const loadThumbnails = async () => {
    if (!projectId && !jobId && !assetId) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      let res = null;
      if (jobId) {
        res = await thumbnailApi.getByJob(jobId);
      } else if (projectId) {
        res = await thumbnailApi.getByProject(projectId);
      }

      if (res && res.success && res.thumbnails) {
        setHistoryList(res.thumbnails);
        const active = res.thumbnails.find((t) => t.is_active) || res.thumbnails[0] || null;
        setActiveThumbnail(active);
        if (active && onThumbnailUpdated) {
          onThumbnailUpdated(active.thumbnail_url);
        }
      }
    } catch (err) {
      console.warn('Failed loading thumbnails:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (isRegenerate = false) => {
    if (generating) return;
    setGenerating(true);
    setErrorMsg(null);
    setProgressStep(1);

    // Simulated progress steps for smooth UX feedback
    const timer1 = setTimeout(() => setProgressStep(2), 1200);
    const timer2 = setTimeout(() => setProgressStep(3), 2800);
    const timer3 = setTimeout(() => setProgressStep(4), 5500);

    try {
      let res = null;
      if (isRegenerate && activeThumbnail) {
        res = await thumbnailApi.regenerate(activeThumbnail.id, {
          selected_style: selectedStyle,
          custom_instruction: customInstruction,
          provider_id: selectedProvider,
        });
      } else {
        res = await thumbnailApi.generate({
          project_id: projectId,
          job_id: jobId,
          asset_id: assetId,
          selected_style: selectedStyle,
          custom_instruction: customInstruction,
          provider_id: selectedProvider,
        });
      }

      setProgressStep(5);

      if (res && res.success && res.thumbnail) {
        setActiveThumbnail(res.thumbnail);
        await loadThumbnails();
        if (onThumbnailUpdated && res.thumbnail.thumbnail_url) {
          onThumbnailUpdated(res.thumbnail.thumbnail_url);
        }
      } else {
        setErrorMsg(res?.thumbnail?.error_message || 'Tạo thumbnail thất bại.');
      }
    } catch (err) {
      console.error('Thumbnail generation error:', err);
      setErrorMsg(err.response?.data?.detail || err.message || 'Lỗi hệ thống khi sinh thumbnail.');
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      setGenerating(false);
      setTimeout(() => setProgressStep(0), 1000);
    }
  };

  const handleSetActive = async (thumb) => {
    try {
      const res = await thumbnailApi.setActive(thumb.id);
      if (res && res.success) {
        setActiveThumbnail(res.thumbnail);
        await loadThumbnails();
        if (onThumbnailUpdated) onThumbnailUpdated(res.thumbnail.thumbnail_url);
      }
    } catch (err) {
      alert('Không thể kích hoạt thumbnail này: ' + err.message);
    }
  };

  const handleDelete = async (thumbId) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa thumbnail này?')) return;
    try {
      await thumbnailApi.delete(thumbId);
      await loadThumbnails();
    } catch (err) {
      alert('Lỗi xóa thumbnail: ' + err.message);
    }
  };

  const currentPreviewUrl = activeThumbnail?.thumbnail_url || initialThumbnailUrl;

  return (
    <div className="card shadow-sm border-0 mb-4" style={{ background: 'rgba(15, 23, 42, 0.65)', backdropFilter: 'blur(12px)', border: '1px solid rgba(255,255,255,0.1)' }}>
      <div className="card-header bg-transparent border-bottom border-secondary d-flex justify-content-between align-items-center py-3">
        <h5 className="card-title m-0 text-light d-flex align-items-center gap-2">
          <span>🎨</span>
          <span>Tự Động Sinh Thumbnail AI (Video Hook)</span>
        </h5>
        {activeThumbnail && (
          <span className={`badge ${activeThumbnail.status === 'completed' ? 'bg-success' : 'bg-warning'}`}>
            {activeThumbnail.status.toUpperCase()}
          </span>
        )}
      </div>

      <div className="card-body p-4">
        {errorMsg && (
          <div className="alert alert-danger d-flex align-items-center justify-content-between mb-4">
            <div>
              <strong>⚠️ Lỗi: </strong> {errorMsg}
            </div>
            <button className="btn btn-sm btn-outline-danger" onClick={() => handleGenerate(false)}>
              Thử lại
            </button>
          </div>
        )}

        {/* Thumbnail Preview Window */}
        <div className="row g-4 mb-4">
          <div className="col-md-7">
            <div
              className="thumbnail-preview-box position-relative rounded overflow-hidden shadow-lg border border-secondary"
              style={{
                width: '100%',
                paddingTop: '56.25%', // 16:9 ratio
                backgroundColor: '#020617',
                backgroundImage: currentPreviewUrl ? `url(${currentPreviewUrl})` : 'none',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
              }}
            >
              {!currentPreviewUrl && !generating && (
                <div className="position-absolute top-50 start-50 translate-middle text-center text-muted px-3">
                  <div style={{ fontSize: '2.5rem' }}>🖼️</div>
                  <p className="small mb-1 text-light fw-bold">Chưa có Thumbnail AI</p>
                  <p className="extra-small text-secondary m-0">
                    Nhấn nút 'Tạo Thumbnail AI' để phân tích kịch bản & sinh ảnh 16:9 tự động.
                  </p>
                </div>
              )}

              {generating && (
                <div
                  className="position-absolute top-0 start-0 w-100 h-100 d-flex flex-column align-items-center justify-content-center"
                  style={{ backgroundColor: 'rgba(2, 6, 23, 0.85)', backdropFilter: 'blur(6px)' }}
                >
                  <LoadingSpinner size="lg" />
                  <p className="text-info fw-bold mt-3 mb-1">
                    {progressStep === 1 && '🔍 Đang phân tích nội dung kịch bản & visual hook...'}
                    {progressStep === 2 && '✍️ Đang tạo prompt minh họa visual storytelling...'}
                    {progressStep === 3 && '🎨 AI đang vẽ hình ảnh thumbnail...'}
                    {progressStep === 4 && '☁️ Đang tải ảnh lên Cloudflare R2 / Supabase Storage...'}
                    {progressStep === 5 && '✅ Đã tạo thumbnail thành công!'}
                  </p>
                  <div className="progress w-50 mt-2" style={{ height: '6px' }}>
                    <div
                      className="progress-bar progress-bar-striped progress-bar-animated bg-info"
                      style={{ width: `${(progressStep / 5) * 100}%` }}
                    />
                  </div>
                </div>
              )}

              {currentPreviewUrl && !generating && (
                <div className="position-absolute bottom-0 start-0 w-100 p-2 d-flex justify-content-between align-items-center bg-dark bg-opacity-75">
                  <span className="badge bg-primary">16:9 (1280x720)</span>
                  <div className="btn-group btn-group-sm">
                    <button className="btn btn-outline-light btn-sm" title="Phóng to" onClick={() => setShowZoomModal(true)}>
                      🔍
                    </button>
                    <a
                      href={currentPreviewUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-outline-light btn-sm"
                      title="Tải xuống ảnh gốc"
                      download
                    >
                      ⬇️
                    </a>
                    {activeThumbnail?.generated_prompt && (
                      <button className="btn btn-outline-info btn-sm" title="Xem AI Prompt" onClick={() => setShowPromptModal(true)}>
                        👁️ AI Prompt
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Controls & Configuration Panel */}
          <div className="col-md-5 d-flex flex-column justify-content-between">
            <div>
              <div className="mb-3">
                <label className="form-label text-light small fw-bold">🎭 Phong Cách Thumbnail (Style):</label>
                <select
                  className="form-select form-select-sm bg-dark text-light border-secondary"
                  value={selectedStyle}
                  onChange={(e) => setSelectedStyle(e.target.value)}
                  disabled={generating}
                >
                  {STYLE_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mb-3">
                <label className="form-label text-light small fw-bold">⚙️ AI Image Provider:</label>
                <select
                  className="form-select form-select-sm bg-dark text-light border-secondary"
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  disabled={generating}
                >
                  {PROVIDER_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mb-3">
                <label className="form-label text-light small fw-bold">💬 Yêu Cầu Bổ Sung (Custom Instruction):</label>
                <textarea
                  className="form-textarea form-control form-control-sm bg-dark text-light border-secondary"
                  rows="3"
                  placeholder="Ví dụ: Tập trung vào nhân vật chính, tông màu xanh u tối, tương phản cao, góc quay rộng..."
                  value={customInstruction}
                  onChange={(e) => setCustomInstruction(e.target.value)}
                  disabled={generating}
                />
              </div>
            </div>

            <div className="d-grid gap-2">
              <button
                className="btn btn-primary fw-bold py-2 d-flex align-items-center justify-content-center gap-2"
                onClick={() => handleGenerate(false)}
                disabled={generating || loading}
              >
                {generating ? <ButtonSpinner text="Đang tạo thumbnail AI..." /> : '✨ Tạo Thumbnail AI Tự Động'}
              </button>

              {activeThumbnail && (
                <div className="d-flex gap-2">
                  <button
                    className="btn btn-outline-warning w-50 btn-sm"
                    onClick={() => handleGenerate(true)}
                    disabled={generating}
                  >
                    🔄 Thử lại / Sinh lại
                  </button>
                  <button
                    className="btn btn-outline-danger w-50 btn-sm"
                    onClick={() => handleDelete(activeThumbnail.id)}
                    disabled={generating}
                  >
                    🗑️ Xóa Thumbnail
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* History Gallery */}
        {historyList.length > 1 && (
          <div className="mt-4 border-top border-secondary pt-3">
            <h6 className="text-secondary small fw-bold mb-2">📜 Lịch Sử Sinh Thumbnail ({historyList.length})</h6>
            <div className="d-flex gap-3 overflow-auto pb-2" style={{ scrollbarWidth: 'thin' }}>
              {historyList.map((item) => (
                <div
                  key={item.id}
                  className={`rounded overflow-hidden border position-relative ${
                    item.is_active ? 'border-success border-2 shadow' : 'border-secondary'
                  }`}
                  style={{ width: '130px', flexShrink: 0, cursor: 'pointer', backgroundColor: '#0f172a' }}
                  onClick={() => handleSetActive(item)}
                >
                  <img
                    src={item.thumbnail_url}
                    alt="Thumbnail history"
                    style={{ width: '100%', height: '73px', objectFit: 'cover' }}
                  />
                  <div className="p-1 small text-truncate text-center text-light extra-small bg-dark">
                    {item.selected_style}
                  </div>
                  {item.is_active && (
                    <span className="badge bg-success position-absolute top-0 start-0 m-1" style={{ fontSize: '0.65rem' }}>
                      ✓ Đang dùng
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* AI Prompt Modal */}
      {showPromptModal && activeThumbnail && (
        <div className="modal-backdrop d-flex justify-content-center align-items-center" style={{ backgroundColor: 'rgba(0,0,0,0.75)', zIndex: 1050 }}>
          <div className="modal-dialog modal-lg bg-dark text-light border border-secondary rounded shadow-lg" style={{ maxWidth: '700px', width: '90%' }}>
            <div className="modal-header border-bottom border-secondary py-3 px-4">
              <h5 className="modal-title">👁️ Chi Tiết AI Analysis & Generated Prompt</h5>
              <button className="btn-close btn-close-white" onClick={() => setShowPromptModal(false)}></button>
            </div>
            <div className="modal-body p-4" style={{ maxHeight: '70vh', overflowY: 'auto' }}>
              <div className="mb-3">
                <h6 className="text-info fw-bold">🎯 Final Image Generation Prompt:</h6>
                <div className="p-3 bg-black rounded text-success font-monospace small border border-secondary">
                  {activeThumbnail.generated_prompt}
                </div>
              </div>

              {activeThumbnail.ai_analysis && (
                <div>
                  <h6 className="text-info fw-bold">🧠 Structured Content Analysis (JSON):</h6>
                  <pre className="p-3 bg-black rounded text-light font-monospace small border border-secondary">
                    {JSON.stringify(activeThumbnail.ai_analysis, null, 2)}
                  </pre>
                </div>
              )}
            </div>
            <div className="modal-footer border-top border-secondary py-2 px-4">
              <button className="btn btn-secondary btn-sm" onClick={() => setShowPromptModal(false)}>
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Fullscreen Zoom Modal */}
      {showZoomModal && currentPreviewUrl && (
        <div
          className="modal-backdrop d-flex justify-content-center align-items-center"
          style={{ backgroundColor: 'rgba(0,0,0,0.9)', zIndex: 1060, cursor: 'pointer' }}
          onClick={() => setShowZoomModal(false)}
        >
          <div className="position-relative p-2" style={{ maxWidth: '95vw', maxHeight: '95vh' }}>
            <img
              src={currentPreviewUrl}
              alt="Zoomed thumbnail"
              className="rounded shadow-lg border border-secondary"
              style={{ maxWidth: '100%', maxHeight: '90vh', objectFit: 'contain' }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
