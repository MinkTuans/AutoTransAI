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
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.75)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        background: '#1e293b',
        width: '600px',
        maxWidth: '90%',
        borderRadius: '12px',
        padding: '24px',
        color: '#e2e8f0',
        boxShadow: '0 20px 25px -5px rgba(0,0,0,0.5)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ margin: 0, fontSize: '20px', color: '#f43f5e', display: 'flex', alignItems: 'center', gap: '8px' }}>
            🔴 YouTube Auto-Publish & SEO Generator
          </h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '20px', cursor: 'pointer' }}>
            ✖
          </button>
        </div>

        {statusMsg && (
          <div style={{
            padding: '10px 14px',
            borderRadius: '8px',
            background: statusMsg.startsWith('✅') || statusMsg.startsWith('🎉') ? '#064e3b' : '#7f1d1d',
            color: '#fff',
            marginBottom: '16px',
            fontSize: '14px',
          }}>
            {statusMsg}
          </div>
        )}

        {publishedUrl ? (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#4ade80', marginBottom: '12px' }}>
              🚀 Video đã được xuất bản!
            </div>
            <a
              href={publishedUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: '#38bdf8', fontSize: '16px', textDecoration: 'underline' }}
            >
              {publishedUrl}
            </a>
            <div style={{ marginTop: '20px' }}>
              <button
                onClick={onClose}
                style={{ padding: '8px 20px', borderRadius: '6px', background: '#475569', color: '#fff', border: 'none', cursor: 'pointer' }}
              >
                Đóng
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <button
                onClick={handleGenerateSEO}
                disabled={loadingSeo}
                style={{
                  width: '100%',
                  padding: '10px',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  color: '#fff',
                  fontWeight: 'bold',
                  border: 'none',
                  cursor: 'pointer',
                  marginBottom: '16px',
                }}
              >
                {loadingSeo ? '⏳ Gemini đang sáng tạo SEO Metadata...' : '✨ Tự Động Sinh SEO Title & Description (Gemini AI)'}
              </button>

              <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: 'bold' }}>
                📌 Tiêu đề Video (Title):
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Nhập tiêu đề YouTube..."
                style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #334155', marginBottom: '12px' }}
              />

              <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: 'bold' }}>
                📝 Mô tả Video (Description):
              </label>
              <textarea
                rows="4"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Nhập nội dung mô tả & hashtag..."
                style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #334155', marginBottom: '12px' }}
              />

              <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: 'bold' }}>
                🏷️ Từ khóa Tags (phân cách bằng dấu phẩy):
              </label>
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="vd: AI, Dubbing, Shorts"
                style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #334155', marginBottom: '12px' }}
              />

              <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: 'bold' }}>
                🔒 Chế độ Chế bản (Privacy Status):
              </label>
              <select
                value={privacyStatus}
                onChange={(e) => setPrivacyStatus(e.target.value)}
                style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #334155' }}
              >
                <option value="private">Private (Riêng tư)</option>
                <option value="unlisted">Unlisted (Không công khai)</option>
                <option value="public">Public (Công khai)</option>
              </select>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' }}>
              <button
                onClick={onClose}
                style={{ padding: '10px 16px', borderRadius: '6px', background: '#475569', color: '#fff', border: 'none', cursor: 'pointer' }}
              >
                Hủy
              </button>
              <button
                onClick={handlePublish}
                disabled={publishing || !title}
                style={{
                  padding: '10px 24px',
                  borderRadius: '6px',
                  background: '#f43f5e',
                  color: '#fff',
                  fontWeight: 'bold',
                  border: 'none',
                  cursor: 'pointer',
                }}
              >
                {publishing ? '⏳ Đang đăng YouTube...' : '🔴 Upload Lên YouTube'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
