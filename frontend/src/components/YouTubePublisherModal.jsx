import React, { useState, useEffect, useRef } from 'react';
import { videoEditorApi, youtubeApi } from '../api';

export default function YouTubePublisherModal({ jobId, onClose }) {
  const [loadingSeo, setLoadingSeo] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const [privacyStatus, setPrivacyStatus] = useState('private');
  const [statusMsg, setStatusMsg] = useState(null);
  const [publishedUrl, setPublishedUrl] = useState(null);
  const pollingRef = useRef(null);

  useEffect(() => {
    // Fetch initial YouTube metadata populated from Project Defaults + Title Template + Episode calculation
    if (jobId) {
      videoEditorApi.getInitialSEO(jobId)
        .then((res) => {
          if (res.success && res.data) {
            if (res.data.title) setTitle(res.data.title);
            if (res.data.description) setDescription(res.data.description);
            if (res.data.tags) setTags(Array.isArray(res.data.tags) ? res.data.tags.join(', ') : res.data.tags);
          }
        })
        .catch((err) => console.warn('Failed to load initial YouTube defaults:', err));
    }

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [jobId]);

  const handleGenerateSEO = async () => {
    setLoadingSeo(true);
    setStatusMsg(null);
    try {
      const res = await videoEditorApi.generateSEO(jobId);
      if (res.success && res.data) {
        setTitle(res.data.title || '');
        setDescription(res.data.description || '');
        setTags(Array.isArray(res.data.tags) ? res.data.tags.join(', ') : (res.data.tags || ''));
        setStatusMsg('✨ Đã tự động sinh và bổ sung SEO bằng AI Gemini (giữ nguyên cấu hình mặc định)!');
      }
    } catch (err) {
      setStatusMsg(`❌ Lỗi tạo SEO: ${err.message}`);
    } finally {
      setLoadingSeo(false);
    }
  };

  const handlePublish = async () => {
    setPublishing(true);
    setUploadProgress(0);
    setStatusMsg(null);
    try {
      const tagList = tags.split(',').map((t) => t.trim()).filter(Boolean);
      const res = await videoEditorApi.publishYouTube({
        job_id: jobId,
        title,
        description,
        tags: tagList,
        privacy_status: privacyStatus,
      });

      if (res.success && res.data) {
        const uploadId = res.data.publication_id || res.data.id;
        if (uploadId) {
          // Poll real-time upload progress from backend DB
          pollingRef.current = setInterval(async () => {
            try {
              const statusRes = await youtubeApi.getUploadStatus(uploadId);
              if (statusRes) {
                const currentStatus = (statusRes.status || '').toUpperCase();
                setUploadProgress(statusRes.progress || 0);

                if (statusRes.error_message) {
                  clearInterval(pollingRef.current);
                  setStatusMsg(`❌ ${statusRes.error_message}`);
                  setPublishing(false);
                  return;
                }

                if (currentStatus === 'PUBLISHED') {
                  clearInterval(pollingRef.current);
                  setUploadProgress(100);
                  setPublishedUrl(statusRes.youtube_url);
                  setStatusMsg('🎉 Đã xuất bản video lên YouTube thành công!');
                  setPublishing(false);
                } else if (currentStatus === 'FAILED') {
                  clearInterval(pollingRef.current);
                  setStatusMsg(`❌ Lỗi đăng YouTube: ${statusRes.error_message || 'Thất bại'}`);
                  setPublishing(false);
                }
              }
            } catch (pollErr) {
              console.error('Upload status poll error:', pollErr);
            }
          }, 800);
        } else if (res.data.youtube_url) {
          setUploadProgress(100);
          setPublishedUrl(res.data.youtube_url);
          setStatusMsg('🎉 Đã xuất bản video lên YouTube thành công!');
          setPublishing(false);
        }
      }
    } catch (err) {
      setStatusMsg(`❌ Lỗi đăng YouTube: ${err.response?.data?.detail || err.message}`);
      setPublishing(false);
    }
  };

  const isDirty = title.trim() !== '' || description.trim() !== '' || tags.trim() !== '';

  const handleSafeClose = () => {
    if (isDirty && !publishedUrl) {
      if (window.confirm('⚠️ Bạn có dữ liệu đang nhập chưa lưu! Bạn có chắc chắn muốn đóng và xóa nội dung đã nhập không?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  return (
    <div className="modal-backdrop" onClick={(e) => { if (e.target === e.currentTarget) handleSafeClose(); }}>
      <div className="modal-dialog" style={{ maxWidth: '640px' }}>
        <div className="modal-header">
          <h3 style={{ color: '#f43f5e', display: 'flex', alignItems: 'center', gap: '8px' }}>
            🔴 YouTube Auto-Publish & SEO Generator
          </h3>
          <button type="button" className="modal-close-btn" onClick={handleSafeClose}>
            &times;
          </button>
        </div>

        <div className="modal-body">
          {statusMsg && (
            <div
              className={`banner ${statusMsg.startsWith('✅') || statusMsg.startsWith('🎉') || statusMsg.startsWith('✨') ? 'banner-success' : 'banner-danger'}`}
              style={{
                marginBottom: '1rem',
                padding: '0.8rem 1rem',
                borderRadius: '8px',
                background: statusMsg.startsWith('✅') || statusMsg.startsWith('🎉') || statusMsg.startsWith('✨') ? '#064e3b' : '#450a0a',
                border: `1px solid ${statusMsg.startsWith('✅') || statusMsg.startsWith('🎉') || statusMsg.startsWith('✨') ? '#10b981' : '#ef4444'}`,
                color: statusMsg.startsWith('✅') || statusMsg.startsWith('🎉') || statusMsg.startsWith('✨') ? '#6ee7b7' : '#fca5a5',
                fontWeight: 600,
                fontSize: '0.9rem',
                wordBreak: 'break-word',
              }}
            >
              <span>{statusMsg}</span>
            </div>
          )}

          {publishedUrl ? (
            <div style={{ textAlign: 'center', padding: '1rem 0' }}>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#4ade80', marginBottom: '0.75rem' }}>
                🚀 Video đã được xuất bản!
              </div>
              <a
                href={publishedUrl}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#38bdf8', fontSize: '1rem', textDecoration: 'underline' }}
              >
                {publishedUrl}
              </a>
              <div className="modal-footer" style={{ justifyContent: 'center', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={onClose}>
                  Đóng
                </button>
              </div>
            </div>
          ) : (
            <div>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleGenerateSEO}
                disabled={loadingSeo}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  marginBottom: '1.25rem',
                }}
              >
                {loadingSeo ? '⏳ Gemini đang sáng tạo SEO Metadata...' : '✨ Tự Động Sinh SEO Title & Description (Gemini AI)'}
              </button>

              <div className="form-group">
                <label className="form-label">📌 Tiêu đề Video (Title):</label>
                <input
                  type="text"
                  className="form-control"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Nhập tiêu đề YouTube..."
                />
              </div>

              <div className="form-group">
                <label className="form-label">📝 Mô tả Video (Description):</label>
                <textarea
                  className="form-textarea"
                  rows="4"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Nhập nội dung mô tả & hashtag..."
                />
              </div>

              <div className="form-group">
                <label className="form-label">🏷️ Từ khóa Tags (phân cách bằng dấu phẩy):</label>
                <input
                  type="text"
                  className="form-control"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  placeholder="vd: AI, Dubbing, Shorts"
                />
              </div>

              <div className="form-group">
                <label className="form-label">🔒 Chế độ Chế bản (Privacy Status):</label>
                <select
                  className="form-control"
                  value={privacyStatus}
                  onChange={(e) => setPrivacyStatus(e.target.value)}
                >
                  <option value="private">Private (Riêng tư)</option>
                  <option value="unlisted">Unlisted (Không công khai)</option>
                  <option value="public">Public (Công khai)</option>
                </select>
              </div>

              {publishing && (
                <div style={{ margin: '1.25rem 0', padding: '1rem', background: '#0f172a', border: '1px solid #3b82f6', borderRadius: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.3)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.85rem', fontWeight: 'bold' }}>
                    <span style={{ color: '#38bdf8', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                      ⏳ {uploadProgress < 100 ? `Đang tải video lên YouTube... (${uploadProgress}%)` : '🎉 Đang hoàn tất xuất bản...'}
                    </span>
                    <span style={{ color: '#ef4444', fontFamily: 'monospace', fontSize: '1rem', fontWeight: 'bold' }}>{uploadProgress}%</span>
                  </div>
                  <div style={{ width: '100%', height: '12px', background: '#1e293b', borderRadius: '6px', overflow: 'hidden', border: '1px solid #475569' }}>
                    <div
                      style={{
                        width: `${uploadProgress}%`,
                        height: '100%',
                        background: 'linear-gradient(90deg, #ef4444, #f43f5e, #dc2626)',
                        boxShadow: '0 0 10px rgba(239, 68, 68, 0.6)',
                        transition: 'width 0.4s ease-in-out',
                      }}
                    />
                  </div>
                </div>
              )}

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={handleSafeClose} disabled={publishing}>
                  Hủy
                </button>
                <button
                  type="button"
                  className="btn btn-danger"
                  onClick={handlePublish}
                  disabled={publishing || !title}
                  style={{ backgroundColor: '#f43f5e' }}
                >
                  {publishing ? `⏳ Đang Upload (${uploadProgress}%)...` : '🔴 Upload Lên YouTube'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
