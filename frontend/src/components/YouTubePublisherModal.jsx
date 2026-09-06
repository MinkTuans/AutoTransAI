import React, { useState } from 'react';
import { videoEditorApi } from '../api';

export default function YouTubePublisherModal({ jobId, onClose }) {
  const [loadingSeo, setLoadingSeo] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const [privacyStatus, setPrivacyStatus] = useState('private');
  const [statusMsg, setStatusMsg] = useState(null);
  const [publishedUrl, setPublishedUrl] = useState(null);

  const handleGenerateSEO = async () => {
    setLoadingSeo(true);
    setStatusMsg(null);
    try {
      const res = await videoEditorApi.generateSEO(jobId);
      if (res.success) {
        setTitle(res.data.title || '');
        setDescription(res.data.description || '');
        setTags(Array.isArray(res.data.tags) ? res.data.tags.join(', ') : '');
        setStatusMsg('✅ Đã tự động tạo SEO Title & Description bằng AI Gemini!');
      }
    } catch (err) {
      setStatusMsg(`❌ Lỗi tạo SEO: ${err.message}`);
    } finally {
      setLoadingSeo(false);
    }
  };

  const handlePublish = async () => {
    setPublishing(true);
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
      if (res.success) {
        setPublishedUrl(res.data.youtube_url);
        setStatusMsg('🎉 Đã xuất bản video lên YouTube thành công!');
      }
    } catch (err) {
      setStatusMsg(`❌ Lỗi đăng YouTube: ${err.message}`);
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="modal-dialog" style={{ maxWidth: '640px' }}>
        <div className="modal-header">
          <h3 style={{ color: '#f43f5e', display: 'flex', alignItems: 'center', gap: '8px' }}>
            🔴 YouTube Auto-Publish & SEO Generator
          </h3>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            &times;
          </button>
        </div>

        <div className="modal-body">
          {statusMsg && (
            <div className={`banner ${statusMsg.startsWith('✅') || statusMsg.startsWith('🎉') ? 'banner-success' : 'banner-danger'}`} style={{ marginBottom: '1rem' }}>
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

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={onClose}>
                  Hủy
                </button>
                <button
                  type="button"
                  className="btn btn-danger"
                  onClick={handlePublish}
                  disabled={publishing || !title}
                  style={{ backgroundColor: '#f43f5e' }}
                >
                  {publishing ? '⏳ Đang đăng YouTube...' : '🔴 Upload Lên YouTube'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
