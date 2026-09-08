import React, { useState, useEffect, useRef } from 'react';
import { projectsApi, providersApi, videoTranslatorApi } from '../api';
import { LoadingSpinner, ButtonSpinner, SkeletonLoader } from '../components/LoadingSpinner';
import ProjectGlossaryManager from '../components/ProjectGlossaryManager';

const parseBool = (val, defaultVal = false) => {
  if (val === null || val === undefined) return defaultVal;
  if (typeof val === 'boolean') return val;
  if (typeof val === 'number') return val !== 0;
  if (typeof val === 'string') {
    const clean = val.trim().toLowerCase();
    if (clean === 'true' || clean === '1' || clean === 'yes' || clean === 'on') return true;
    if (clean === 'false' || clean === '0' || clean === 'no' || clean === 'off') return false;
  }
  return Boolean(val);
};

export default function ProjectDetail({ projectId, onBack, onEditInTranslator }) {
  const [project, setProject] = useState(null);
  const [providers, setProviders] = useState({ audio: [], video: [], llm: [] });
  const [voices, setVoices] = useState([]);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'settings', 'glossary'
  const [loading, setLoading] = useState(true);
  const [savingSettings, setSavingSettings] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState('');
  const [error, setError] = useState(null);

  // Editable settings form state
  const [editSettings, setEditSettings] = useState({});
  const [savedSnapshot, setSavedSnapshot] = useState({});
  const [isTabDirty, setIsTabDirty] = useState(false);
  const [isUploadingLogo, setIsUploadingLogo] = useState(false);
  const [deletingVideoId, setDeletingVideoId] = useState(null);

  const handleDeleteVideo = async (targetVideoId) => {
    if (!targetVideoId) return;
    const confirmDelete = window.confirm(`Bạn có chắc chắn muốn xóa video này (ID: ${targetVideoId}) khỏi dự án?\nHành động này sẽ xóa vĩnh viễn dữ liệu và các file liên quan.`);
    if (!confirmDelete) return;

    setDeletingVideoId(targetVideoId);
    try {
      const res = await projectsApi.delete(targetVideoId);
      if (res.success) {
        await loadProjectData();
      } else {
        alert('Không thể xóa video: ' + (res.message || 'Lỗi không xác định'));
      }
    } catch (err) {
      alert('Lỗi khi xóa video: ' + (err.response?.data?.detail || err.message));
    } finally {
      setDeletingVideoId(null);
    }
  };

  const pollIntervalRef = useRef(null);

  const loadProjectData = async () => {
    try {
      const [projRes, provRes] = await Promise.all([
        projectsApi.get(projectId),
        providersApi.list(),
      ]);

      if (projRes.success) {
        const p = projRes.data;
        setProject(p);
        const s = p.settings || {};
        setEditSettings(s);
        setSavedSnapshot(s);
        setIsTabDirty(false);
      } else {
        setError('Không tìm thấy dữ liệu dự án');
      }

      if (provRes.success) {
        setProviders(provRes.data);
      }
    } catch (err) {
      setError('Lỗi kết nối khi tải chi tiết dự án');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjectData();
  }, [projectId]);

  // Fetch voices for current audio provider
  useEffect(() => {
    const audioProv = editSettings.audio_provider_id || 'edge_tts';
    const lang = editSettings.target_language || 'vi';
    providersApi.listVoices(audioProv, lang)
      .then(res => {
        if (res.success && res.data) {
          setVoices(res.data);
        }
      })
      .catch(() => setVoices([]));
  }, [editSettings.audio_provider_id, editSettings.target_language]);

  // Check dirty state on settings tab
  useEffect(() => {
    if (!savedSnapshot || Object.keys(savedSnapshot).length === 0) {
      setIsTabDirty(false);
      return;
    }
    const isDiff = JSON.stringify(editSettings) !== JSON.stringify(savedSnapshot);
    setIsTabDirty(isDiff);
  }, [editSettings, savedSnapshot]);

  const handleSaveTabSettings = async () => {
    setSavingSettings(true);
    setSaveSuccessMsg('');
    setError(null);
    try {
      const res = await projectsApi.saveSettings(projectId, editSettings);
      if (res.success) {
        const savedData = res.data || res.settings;
        setSavedSnapshot(savedData);
        setEditSettings(savedData);
        setIsTabDirty(false);
        setSaveSuccessMsg('✅ Đã lưu thành công cấu hình mới vào Database MySQL!');
        await loadProjectData();
        setTimeout(() => setSaveSuccessMsg(''), 4000);
      }
    } catch (err) {
      setError('Không thể lưu cấu hình dự án: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSavingSettings(false);
    }
  };

  const handleTabLogoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploadingLogo(true);
    try {
      const res = await videoTranslatorApi.uploadWatermarkLogo(file, projectId);
      if (res.success && res.data) {
        const relativePath = res.data.relative_path || res.data.image_path;
        setEditSettings(prev => ({
          ...prev,
          watermark_image_path: relativePath,
          watermark_image_asset_id: res.data.asset_id || prev.watermark_image_asset_id,
        }));
      }
    } catch (err) {
      alert('Lỗi upload logo: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsUploadingLogo(false);
    }
  };

  // Polling for live status when workflow status is running
  useEffect(() => {
    const isRunning = project && ['running', 'generating_audio', 'generating_video', 'syncing', 'merging'].includes(project.workflow_status);

    if (!isRunning) {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      return;
    }

    pollIntervalRef.current = setInterval(async () => {
      try {
        const projRes = await projectsApi.get(projectId);
        if (projRes.success) setProject(projRes.data);
      } catch (e) {
        console.error('Polling status failed', e);
      }
    }, 2000);

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [project?.workflow_status, projectId]);

  if (loading) {
    return (
      <div className="card" style={{ padding: '2rem', background: '#0f172a', borderRadius: '12px' }}>
        <LoadingSpinner size="lg" label="Đang tải chi tiết dự án..." sublabel="Đang nạp thông tin cấu hình, video và glossary..." />
        <div style={{ marginTop: '1.5rem' }}>
          <SkeletonLoader type="card" rows={3} />
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="card" style={{ padding: '2rem', textAlign: 'center', background: '#0f172a', borderRadius: '12px' }}>
        <h3 style={{ color: '#f87171', marginBottom: '0.5rem' }}>⚠️ Không tìm thấy dự án</h3>
        <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>
          {error || 'Dự án với ID này không tồn tại hoặc đã bị xóa.'}
        </p>
        <button className="btn btn-secondary" onClick={onBack}>
          ← Quay lại Dashboard
        </button>
      </div>
    );
  }

  const pSettings = editSettings;
  const videos = project.videos || [];
  const totalVideos = videos.length;
  const completedVideos = videos.filter(v => v.status === 'completed').length;
  const runningVideos = videos.filter(v => v.status === 'running' || v.status === 'in_progress').length;
  const failedVideos = videos.filter(v => v.status === 'failed').length;

  const formatDate = (isoStr) => {
    if (!isoStr) return 'N/A';
    try {
      return new Date(isoStr).toLocaleString('vi-VN');
    } catch (e) {
      return isoStr;
    }
  };

  return (
    <div style={{ padding: '20px 0', maxWidth: '1100px', margin: '0 auto' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '24px' }}>
        <div>
          <button
            className="btn btn-secondary"
            onClick={onBack}
            style={{ marginBottom: '10px', padding: '6px 14px', fontSize: '13px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            ← Quay lại Dashboard
          </button>
          <h1 style={{ fontSize: '26px', fontWeight: 'bold', color: '#f8fafc', margin: '0 0 6px 0' }}>
            📁 {project.title}
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '13px', margin: 0 }}>
            ID: <code style={{ background: '#1e293b', padding: '2px 8px', borderRadius: '4px', color: '#818cf8' }}>{project.id}</code>
            {' | '} Tạo lúc: {formatDate(project.created_at)}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {onEditInTranslator && (
            <button
              onClick={() => onEditInTranslator(project.id, videos.length > 0 ? (videos[0].id || videos[0].job_id) : null)}
              style={{
                background: '#4f46e5',
                color: '#fff',
                border: 'none',
                padding: '10px 18px',
                borderRadius: '8px',
                fontWeight: 'bold',
                cursor: 'pointer',
                fontSize: '14px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                boxShadow: '0 4px 12px rgba(79, 70, 229, 0.3)',
              }}
            >
              ⚙️ Chỉnh sửa Studio & Dịch Video
            </button>
          )}
        </div>
      </div>

      {saveSuccessMsg && (
        <div style={{ background: '#064e3b', border: '1px solid #10b981', color: '#6ee7b7', padding: '12px 20px', borderRadius: '8px', marginBottom: '20px', fontWeight: 'bold' }}>
          {saveSuccessMsg}
        </div>
      )}

      {error && (
        <div style={{ background: '#7f1d1d', border: '1px solid #f87171', color: '#fca5a5', padding: '12px 20px', borderRadius: '8px', marginBottom: '20px' }}>
          ❌ {error}
        </div>
      )}

      {/* Tabs Navigation */}
      <div style={{ display: 'flex', borderBottom: '1px solid #334155', marginBottom: '24px' }}>
        <button
          onClick={() => setActiveTab('overview')}
          style={{
            padding: '12px 20px',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'overview' ? '3px solid #6366f1' : '3px solid transparent',
            color: activeTab === 'overview' ? '#818cf8' : '#94a3b8',
            fontWeight: 'bold',
            fontSize: '15px',
            cursor: 'pointer',
          }}
        >
          📊 Tổng quan & Videos ({totalVideos})
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          style={{
            padding: '12px 20px',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'settings' ? '3px solid #6366f1' : '3px solid transparent',
            color: activeTab === 'settings' ? '#818cf8' : '#94a3b8',
            fontWeight: 'bold',
            fontSize: '15px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          ⚙️ Cấu hình Dự án (Project Settings)
          {isTabDirty && <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b' }} />}
        </button>
        <button
          onClick={() => setActiveTab('glossary')}
          style={{
            padding: '12px 20px',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'glossary' ? '3px solid #6366f1' : '3px solid transparent',
            color: activeTab === 'glossary' ? '#818cf8' : '#94a3b8',
            fontWeight: 'bold',
            fontSize: '15px',
            cursor: 'pointer',
          }}
        >
          📖 Thuật ngữ & Glossary ({project.glossary_count || 0})
        </button>
      </div>

      {/* TAB 1: OVERVIEW & VIDEOS */}
      {activeTab === 'overview' && (
        <div>
          {/* Project Metrics Overview */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <div style={{ background: '#1e293b', padding: '16px', borderRadius: '10px', border: '1px solid #334155' }}>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>Tổng Video</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f8fafc', marginTop: '4px' }}>{totalVideos}</div>
            </div>
            <div style={{ background: '#1e293b', padding: '16px', borderRadius: '10px', border: '1px solid #334155' }}>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>Hoàn thành</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4ade80', marginTop: '4px' }}>{completedVideos}</div>
            </div>
            <div style={{ background: '#1e293b', padding: '16px', borderRadius: '10px', border: '1px solid #334155' }}>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>Đang chạy</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#60a5fa', marginTop: '4px' }}>{runningVideos}</div>
            </div>
            <div style={{ background: '#1e293b', padding: '16px', borderRadius: '10px', border: '1px solid #334155' }}>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>Thất bại</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f87171', marginTop: '4px' }}>{failedVideos}</div>
            </div>
          </div>

          {/* Description */}
          {project.description && (
            <div className="card" style={{ background: '#1e293b', padding: '16px 20px', borderRadius: '10px', marginBottom: '24px', border: '1px solid #334155' }}>
              <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#94a3b8' }}>Mô tả dự án:</h4>
              <p style={{ margin: 0, color: '#e2e8f0', fontSize: '14px' }}>{project.description}</p>
            </div>
          )}

          {/* Video List Table */}
          <div className="card" style={{ background: '#1e293b', borderRadius: '12px', padding: '20px', border: '1px solid #334155' }}>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 'bold', color: '#f8fafc' }}>
              🎬 Danh sách Video trong Dự án
            </h3>

            {videos.length === 0 ? (
              <div style={{ padding: '30px', textAlign: 'center', color: '#94a3b8' }}>
                Chưa có video nào được xử lý trong dự án này.
                {onEditInTranslator && (
                  <div style={{ marginTop: '12px' }}>
                    <button
                      onClick={() => onEditInTranslator(project.id)}
                      className="btn btn-primary"
                    >
                      ▶️ Khởi chạy Video đầu tiên
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #334155', textTransform: 'uppercase', fontSize: '12px', color: '#94a3b8', textAlign: 'left' }}>
                      <th style={{ padding: '10px' }}>Video / Job ID</th>
                      <th style={{ padding: '10px' }}>Trạng thái</th>
                      <th style={{ padding: '10px' }}>Tiến trình</th>
                      <th style={{ padding: '10px' }}>Thời gian tạo</th>
                      <th style={{ padding: '10px' }}>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {videos.map(v => (
                      <tr key={v.id} style={{ borderBottom: '1px solid #1e293b' }}>
                        <td style={{ padding: '12px 10px', fontWeight: 'bold', color: '#e2e8f0' }}>
                          {v.title || v.id}
                        </td>
                        <td style={{ padding: '12px 10px' }}>
                          <span className={`badge ${v.status === 'completed' ? 'badge-success' : (v.status === 'failed' ? 'badge-danger' : 'badge-info')}`}>
                            {v.status}
                          </span>
                        </td>
                        <td style={{ padding: '12px 10px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div style={{ flex: 1, height: '6px', background: '#0f172a', borderRadius: '3px', overflow: 'hidden' }}>
                              <div style={{ width: `${v.overall_progress_pct || 0}%`, height: '100%', background: v.status === 'completed' ? '#10b981' : '#3b82f6' }} />
                            </div>
                            <span style={{ fontSize: '12px', color: '#94a3b8' }}>{v.overall_progress_pct || 0}%</span>
                          </div>
                        </td>
                        <td style={{ padding: '12px 10px', fontSize: '13px', color: '#94a3b8' }}>
                          {formatDate(v.created_at)}
                        </td>
                        <td style={{ padding: '12px 10px' }}>
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                            {v.output_url && (
                              <a
                                href={v.output_url}
                                target="_blank"
                                rel="noreferrer"
                                className="btn btn-secondary"
                                style={{ padding: '4px 10px', fontSize: '12px' }}
                              >
                                📥 Xem Output
                              </a>
                            )}
                            <button
                              onClick={() => onEditInTranslator && onEditInTranslator(project.id, v.id || v.job_id)}
                              className="btn btn-primary"
                              style={{ padding: '4px 10px', fontSize: '12px' }}
                            >
                              ⚙️ Mở Studio
                            </button>

                            <button
                              onClick={() => handleDeleteVideo(v.id || v.job_id)}
                              disabled={deletingVideoId === (v.id || v.job_id)}
                              title="Xóa Video này khỏi dự án"
                              style={{
                                padding: '4px 10px',
                                fontSize: '12px',
                                background: '#ef4444',
                                color: '#ffffff',
                                border: 'none',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontWeight: 'bold',
                                opacity: deletingVideoId === (v.id || v.job_id) ? 0.6 : 1,
                              }}
                            >
                              {deletingVideoId === (v.id || v.job_id) ? '...' : '🗑️ Xóa'}
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: EDITABLE PROJECT SETTINGS */}
      {activeTab === 'settings' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Header Action Bar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#1e1b4b', padding: '16px 20px', borderRadius: '10px', border: '1px solid #4338ca', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '16px', color: '#fff', fontWeight: 'bold' }}>⚙️ Cấu hình Chi Tiết Dự Án (Chỉnh sửa & Lưu DB)</h3>
              <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#93c5fd' }}>Thay đổi các tùy chọn dưới đây và nhấn "Lưu cấu hình" để cập nhật chính xác vào dự án.</p>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              {isTabDirty && (
                <button
                  onClick={() => setEditSettings(savedSnapshot)}
                  style={{ background: '#475569', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' }}
                >
                  ↩️ Khôi phục
                </button>
              )}
              <button
                onClick={handleSaveTabSettings}
                disabled={savingSettings}
                style={{ background: '#2563eb', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', fontSize: '14px', boxShadow: '0 4px 12px rgba(37, 99, 235, 0.4)' }}
              >
                {savingSettings ? 'Đang lưu Database...' : '💾 Lưu Cấu hình Dự án'}
              </button>
            </div>
          </div>

          {isTabDirty && (
            <div style={{ background: '#1e3a8a', border: '1px solid #3b82f6', color: '#93c5fd', padding: '12px 18px', borderRadius: '8px', fontSize: '13px', fontWeight: 'bold' }}>
              ⚠️ Bạn có thay đổi chưa lưu trên trang này. Hãy nhấn "Lưu Cấu hình Dự án" để lưu lại.
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
            {/* 1. Language & Input */}
            <div className="card" style={{ background: '#1e293b', borderRadius: '10px', padding: '18px', border: '1px solid #334155' }}>
              <h4 style={{ margin: '0 0 14px 0', fontSize: '15px', color: '#818cf8', fontWeight: 'bold', borderBottom: '1px solid #334155', paddingBottom: '8px' }}>
                🌐 Ngôn ngữ & Video Input
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Ngôn ngữ đích (Target Language):</label>
                  <select
                    value={pSettings.target_language || 'vi'}
                    onChange={(e) => setEditSettings(prev => ({ ...prev, target_language: e.target.value }))}
                    style={{ width: '100%', padding: '8px 12px', background: '#0f172a', border: '1px solid #475569', color: '#fff', borderRadius: '6px', fontSize: '13px' }}
                  >
                    <option value="vi">🇻🇳 Tiếng Việt (Vietnamese)</option>
                    <option value="en">🇬🇧 Tiếng Anh (English)</option>
                    <option value="ja">🇯🇵 Tiếng Nhật (Japanese)</option>
                    <option value="ko">🇰🇷 Tiếng Hàn (Korean)</option>
                    <option value="zh">🇨🇳 Tiếng Trung (Chinese)</option>
                    <option value="fr">🇫🇷 Tiếng Pháp (French)</option>
                    <option value="de">🇩🇪 Tiếng Đức (German)</option>
                    <option value="es">🇪🇸 Tiếng Tây Ban Nha (Spanish)</option>
                    <option value="ru">🇷🇺 Tiếng Nga (Russian)</option>
                    <option value="th">🇹🇭 Tiếng Thái (Thai)</option>
                    <option value="id">🇮🇩 Tiếng Indonesia (Indonesian)</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Ngôn ngữ nguồn (Source Language):</label>
                  <select
                    value={pSettings.source_language || 'auto'}
                    onChange={(e) => setEditSettings(prev => ({ ...prev, source_language: e.target.value }))}
                    style={{ width: '100%', padding: '8px 12px', background: '#0f172a', border: '1px solid #475569', color: '#fff', borderRadius: '6px', fontSize: '13px' }}
                  >
                    <option value="auto">✨ Tự động nhận diện (Auto Detect)</option>
                    <option value="en">🇬🇧 Tiếng Anh (English)</option>
                    <option value="zh">🇨🇳 Tiếng Trung (Chinese)</option>
                    <option value="ja">🇯🇵 Tiếng Nhật (Japanese)</option>
                    <option value="ko">🇰🇷 Tiếng Hàn (Korean)</option>
                    <option value="fr">🇫🇷 Tiếng Pháp (French)</option>
                    <option value="de">🇩🇪 Tiếng Đức (German)</option>
                    <option value="es">🇪🇸 Tiếng Tây Ban Nha (Spanish)</option>
                    <option value="ru">🇷🇺 Tiếng Nga (Russian)</option>
                    <option value="vi">🇻🇳 Tiếng Việt (Vietnamese)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 2. AI Providers & Models */}
            <div className="card" style={{ background: '#1e293b', borderRadius: '10px', padding: '18px', border: '1px solid #334155' }}>
              <h4 style={{ margin: '0 0 14px 0', fontSize: '15px', color: '#818cf8', fontWeight: 'bold', borderBottom: '1px solid #334155', paddingBottom: '8px' }}>
                🤖 AI Providers & Models
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>LLM / Script Provider:</label>
                  <select
                    value={pSettings.llm_provider_id || 'gemini'}
                    onChange={(e) => setEditSettings(prev => ({ ...prev, llm_provider_id: e.target.value, stt_provider_id: e.target.value, translation_provider_id: e.target.value }))}
                    style={{ width: '100%', padding: '8px 12px', background: '#0f172a', border: '1px solid #475569', color: '#fff', borderRadius: '6px', fontSize: '13px' }}
                  >
                    <option value="gemini">✨ Google Gemini AI Studio (Mặc định)</option>
                    <option value="openai">🤖 OpenAI ChatGPT</option>
                    <option value="claude">🧠 Anthropic Claude AI</option>
                    <option value="deepseek">🐳 DeepSeek AI</option>
                    <option value="ollama">🦙 Local Ollama (Offline)</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>STT / Translation Model:</label>
                  <select
                    value={pSettings.stt_model || 'gemini-2.0-flash'}
                    onChange={(e) => setEditSettings(prev => ({ ...prev, stt_model: e.target.value, translation_model: e.target.value }))}
                    style={{ width: '100%', padding: '8px 12px', background: '#0f172a', border: '1px solid #475569', color: '#fff', borderRadius: '6px', fontSize: '13px' }}
                  >
                    <option value="gemini-2.0-flash">✨ Gemini 2.0 Flash (Nhanh & Tối Ưu)</option>
                    <option value="gemini-1.5-pro">💎 Gemini 1.5 Pro (Chính Xác Cao)</option>
                    <option value="gpt-4o-mini">🤖 GPT-4o Mini (OpenAI)</option>
                    <option value="gpt-4o">🚀 GPT-4o (OpenAI High Accuracy)</option>
                    <option value="claude-3-5-sonnet">🧠 Claude 3.5 Sonnet</option>
                    <option value="deepseek-chat">🐳 DeepSeek V3 / R1</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 3. Voice & Dubbing */}
            <div className="card" style={{ background: '#1e293b', borderRadius: '10px', padding: '18px', border: '1px solid #334155' }}>
              <h4 style={{ margin: '0 0 14px 0', fontSize: '15px', color: '#818cf8', fontWeight: 'bold', borderBottom: '1px solid #334155', paddingBottom: '8px' }}>
                🎙️ Voice & Dubbing
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>TTS Provider:</label>
                  <select
                    value={pSettings.audio_provider_id || 'edge_tts'}
                    onChange={(e) => setEditSettings(prev => ({ ...prev, audio_provider_id: e.target.value }))}
                    style={{ width: '100%', padding: '8px 12px', background: '#0f172a', border: '1px solid #475569', color: '#fff', borderRadius: '6px', fontSize: '13px' }}
                  >
                    <option value="edge_tts">⚡ Edge TTS (Miễn phí / Tốc độ cao)</option>
                    <option value="elevenlabs">🎙️ ElevenLabs (Chất lượng cao)</option>
                    <option value="google_tts">🔊 Google Cloud TTS</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Giọng đọc (Voice ID):</label>
                  <select
                    value={pSettings.voice_id || 'vi-VN-HoaiMyNeural'}
                    onChange={(e) => setEditSettings(prev => ({ ...prev, voice_id: e.target.value }))}
                    style={{ width: '100%', padding: '8px 12px', background: '#0f172a', border: '1px solid #475569', color: '#fff', borderRadius: '6px', fontSize: '13px' }}
                  >
                    {voices.map(v => (
                      <option key={v.id} value={v.id}>{v.name} ({v.gender})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Âm thanh gốc (Original Audio):</label>
                  <select
                    value={pSettings.original_audio_mode || 'mute'}
                    onChange={(e) => setEditSettings(prev => ({ ...prev, original_audio_mode: e.target.value }))}
                    style={{ width: '100%', padding: '8px 12px', background: '#0f172a', border: '1px solid #475569', color: '#fff', borderRadius: '6px', fontSize: '13px' }}
                  >
                    <option value="mute">🔇 Tắt hoàn toàn tiếng gốc (Mute)</option>
                    <option value="duck">🔉 Giảm âm lượng gốc (Background Ducking 20%)</option>
                    <option value="keep">🔊 Giữ âm thanh gốc trộn cùng tiếng đọc (Full Keep)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 4. Watermark Configuration */}
            <div className="card" style={{ background: '#1e293b', borderRadius: '10px', padding: '18px', border: '1px solid #334155' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', borderBottom: '1px solid #334155', paddingBottom: '8px' }}>
                <h4 style={{ margin: 0, fontSize: '15px', color: '#818cf8', fontWeight: 'bold' }}>
                  🏷️ Watermark / Logo Configuration
                </h4>
                <button
                  type="button"
                  role="switch"
                  aria-checked={parseBool(pSettings.watermark_enabled)}
                  title={parseBool(pSettings.watermark_enabled) ? "BẬT Watermark" : "TẮT Watermark"}
                  onClick={() => setEditSettings(prev => ({ ...prev, watermark_enabled: !parseBool(prev.watermark_enabled) }))}
                  style={{
                    width: '46px',
                    height: '24px',
                    borderRadius: '12px',
                    background: parseBool(pSettings.watermark_enabled) ? '#6366f1' : '#475569',
                    border: 'none',
                    position: 'relative',
                    cursor: 'pointer',
                    transition: 'background 0.2s ease',
                    padding: 0,
                    outline: 'none',
                    boxShadow: parseBool(pSettings.watermark_enabled) ? '0 0 10px rgba(99, 102, 241, 0.6)' : 'none',
                  }}
                >
                  <span
                    style={{
                      display: 'block',
                      width: '18px',
                      height: '18px',
                      borderRadius: '50%',
                      background: '#ffffff',
                      position: 'absolute',
                      top: '3px',
                      left: parseBool(pSettings.watermark_enabled) ? '25px' : '3px',
                      transition: 'left 0.2s ease',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
                    }}
                  />
                </button>
              </div>

              {parseBool(pSettings.watermark_enabled) ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div style={{ display: 'flex', gap: '16px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', color: '#cbd5e1', fontSize: '13px' }}>
                      <input
                        type="radio"
                        name="tab_wm_type"
                        value="image"
                        checked={(pSettings.watermark_type === 'text' ? 'text' : 'image') === 'image'}
                        onChange={() => setEditSettings(prev => ({ ...prev, watermark_type: 'image' }))}
                        style={{ accentColor: '#6366f1' }}
                      />
                      🖼️ Logo Ảnh
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', color: '#cbd5e1', fontSize: '13px' }}>
                      <input
                        type="radio"
                        name="tab_wm_type"
                        value="text"
                        checked={pSettings.watermark_type === 'text'}
                        onChange={() => setEditSettings(prev => ({ ...prev, watermark_type: 'text' }))}
                        style={{ accentColor: '#6366f1' }}
                      />
                      🔤 Watermark Text
                    </label>
                  </div>

                  {pSettings.watermark_type === 'text' ? (
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Nội dung Text Watermark:</label>
                      <input
                        type="text"
                        value={pSettings.watermark_text || ''}
                        onChange={(e) => setEditSettings(prev => ({ ...prev, watermark_text: e.target.value }))}
                        placeholder="© AutoTransAI Studio"
                        style={{ width: '100%', padding: '8px 12px', background: '#0f172a', border: '1px solid #475569', color: '#fff', borderRadius: '6px', fontSize: '13px' }}
                      />
                    </div>
                  ) : (
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Upload Logo (PNG / WEBP / JPG):</label>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleTabLogoUpload}
                        disabled={isUploadingLogo}
                        style={{ background: '#0f172a', padding: '6px', borderRadius: '6px', color: '#fff', border: '1px solid #475569', fontSize: '12px', width: '100%' }}
                      />
                      {pSettings.watermark_image_path && (
                        <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <img
                            src={`/api/storage/files/${pSettings.watermark_image_path.replace(/\\/g, '/')}`}
                            alt="Logo Preview"
                            style={{ maxHeight: '40px', maxWidth: '120px', objectFit: 'contain', background: '#0f172a', padding: '4px', borderRadius: '4px', border: '1px solid #475569' }}
                          />
                          <span style={{ color: '#4ade80', fontSize: '12px' }}>✓ Đã chọn logo</span>
                        </div>
                      )}
                    </div>
                  )}

                  <div>
                    <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Vị trí Watermark:</label>
                    <select
                      value={pSettings.watermark_position || 'bottom_right'}
                      onChange={(e) => setEditSettings(prev => ({ ...prev, watermark_position: e.target.value }))}
                      style={{ width: '100%', padding: '8px 12px', background: '#0f172a', border: '1px solid #475569', color: '#fff', borderRadius: '6px', fontSize: '13px' }}
                    >
                      <option value="bottom_right">↘️ Góc Dưới Phải (Bottom Right)</option>
                      <option value="bottom_left">↙️ Góc Dưới Trái (Bottom Left)</option>
                      <option value="top_right">↗️ Góc Trên Phải (Top Right)</option>
                      <option value="top_left">↖️ Góc Trên Trái (Top Left)</option>
                      <option value="center">⏹️ Chính Giữa (Center)</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>
                      Kích thước ({Math.round((pSettings.watermark_scale || 0.20) * 100)}% rộng video):
                    </label>
                    <input
                      type="range"
                      min="0.10"
                      max="0.50"
                      step="0.05"
                      value={pSettings.watermark_scale || 0.20}
                      onChange={(e) => setEditSettings(prev => ({ ...prev, watermark_scale: parseFloat(e.target.value) }))}
                      style={{ width: '100%', accentColor: '#818cf8' }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>
                      Độ Trong Suốt ({Math.round((pSettings.watermark_opacity || 0.80) * 100)}%):
                    </label>
                    <input
                      type="range"
                      min="0.10"
                      max="1.00"
                      step="0.05"
                      value={pSettings.watermark_opacity || 0.80}
                      onChange={(e) => setEditSettings(prev => ({ ...prev, watermark_opacity: parseFloat(e.target.value) }))}
                      style={{ width: '100%', accentColor: '#818cf8' }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>
                      Khoảng cách mép ({pSettings.watermark_margin || 20}px):
                    </label>
                    <input
                      type="range"
                      min="10"
                      max="50"
                      step="5"
                      value={pSettings.watermark_margin || 20}
                      onChange={(e) => setEditSettings(prev => ({ ...prev, watermark_margin: parseInt(e.target.value, 10) }))}
                      style={{ width: '100%', accentColor: '#818cf8' }}
                    />
                  </div>
                </div>
              ) : (
                <div style={{ fontSize: '13px', color: '#94a3b8', fontStyle: 'italic', padding: '12px', background: '#0f172a', borderRadius: '6px', border: '1px solid #334155' }}>
                  🚫 Watermark hiện đang TẮT cho dự án này. Gạt thanh trượt đóng mở ở trên để kích hoạt tùy chỉnh logo hoặc văn bản watermark.
                </div>
              )}
            </div>

            {/* 5. AI Thumbnail Settings */}
            <div className="card" style={{ background: '#1e293b', borderRadius: '10px', padding: '18px', border: '1px solid #334155' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', borderBottom: '1px solid #334155', paddingBottom: '8px' }}>
                <h4 style={{ margin: 0, fontSize: '15px', color: '#818cf8', fontWeight: 'bold' }}>
                  🎨 AI Thumbnail Configuration
                </h4>
                <button
                  type="button"
                  role="switch"
                  aria-checked={parseBool(pSettings.thumbnail_enabled)}
                  title={parseBool(pSettings.thumbnail_enabled) ? "BẬT AI Thumbnail" : "TẮT AI Thumbnail"}
                  onClick={() => setEditSettings(prev => ({ ...prev, thumbnail_enabled: !parseBool(prev.thumbnail_enabled) }))}
                  style={{
                    width: '46px',
                    height: '24px',
                    borderRadius: '12px',
                    background: parseBool(pSettings.thumbnail_enabled) ? '#6366f1' : '#475569',
                    border: 'none',
                    position: 'relative',
                    cursor: 'pointer',
                    transition: 'background 0.2s ease',
                    padding: 0,
                    outline: 'none',
                    boxShadow: parseBool(pSettings.thumbnail_enabled) ? '0 0 10px rgba(99, 102, 241, 0.6)' : 'none',
                  }}
                >
                  <span
                    style={{
                      display: 'block',
                      width: '18px',
                      height: '18px',
                      borderRadius: '50%',
                      background: '#ffffff',
                      position: 'absolute',
                      top: '3px',
                      left: parseBool(pSettings.thumbnail_enabled) ? '25px' : '3px',
                      transition: 'left 0.2s ease',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
                    }}
                  />
                </button>
              </div>

              {parseBool(pSettings.thumbnail_enabled) ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div>
                    <label className="form-label text-light small fw-bold" style={{ display: 'block', marginBottom: '6px' }}>
                      🎭 Phong Cách Thumbnail (Style):
                    </label>
                    <select
                      className="form-select form-select-sm bg-dark text-light border-secondary"
                      value={pSettings.thumbnail_style || 'auto'}
                      onChange={(e) => setEditSettings(prev => ({ ...prev, thumbnail_style: e.target.value }))}
                    >
                      <option value="auto">🤖 Tự động (Phân tích cảm xúc kịch bản)</option>
                      <option value="cinematic">🎬 Cinematic (Điện ảnh kịch tính)</option>
                      <option value="youtube_viral">🚀 YouTube Viral (Bắt mắt, biểu cảm mạnh)</option>
                      <option value="horror">👻 Horror (U tối, bí ẩn, kinh dị)</option>
                      <option value="anime">🌸 Anime Nhật Bản (Nhiều màu sắc)</option>
                      <option value="realistic">📸 Realistic (Ảnh chụp 8K chân thực)</option>
                      <option value="cartoon">🎨 Cartoon 3D (Hoạt hình 3D)</option>
                      <option value="documentary">📜 Documentary (Phim tài liệu)</option>
                      <option value="minimal">📐 Minimal (Tối giản, tương phản)</option>
                      <option value="movie_poster">🍿 Poster Phim Hollywood</option>
                    </select>
                  </div>

                  <div>
                    <label className="form-label text-light small fw-bold" style={{ display: 'block', marginBottom: '6px' }}>
                      ⚙️ AI Image Provider:
                    </label>
                    <select
                      className="form-select form-select-sm bg-dark text-light border-secondary"
                      value={pSettings.thumbnail_provider || 'pollinations'}
                      onChange={(e) => setEditSettings(prev => ({ ...prev, thumbnail_provider: e.target.value }))}
                    >
                      <option value="pollinations">⚡ Pollinations AI (Miễn phí & Nhanh)</option>
                      <option value="fal">🎨 fal.ai FLUX (Chất lượng cao)</option>
                      <option value="openai">🤖 OpenAI DALL-E 3</option>
                      <option value="local_image">🖼️ Local Scenery (Offline)</option>
                    </select>
                  </div>

                  <div>
                    <label className="form-label text-light small fw-bold" style={{ display: 'block', marginBottom: '6px' }}>
                      💬 Yêu Cầu Bổ Sung (Custom Instruction):
                    </label>
                    <textarea
                      className="form-textarea form-control form-control-sm bg-dark text-light border-secondary"
                      rows="3"
                      placeholder="Ví dụ: Tập trung vào nhân vật chính, tông màu xanh u tối, tương phản cao, góc quay rộng..."
                      value={pSettings.thumbnail_custom_instruction || ''}
                      onChange={(e) => setEditSettings(prev => ({ ...prev, thumbnail_custom_instruction: e.target.value }))}
                      style={{ resize: 'vertical' }}
                    />
                  </div>
                </div>
              ) : (
                <div style={{ fontSize: '13px', color: '#94a3b8', fontStyle: 'italic', padding: '12px', background: '#0f172a', borderRadius: '6px', border: '1px solid #334155' }}>
                  🖼️ tự động hiện đang TẮT. Gạt thanh trượt đóng mở ở trên để kích hoạt.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: GLOSSARY */}
      {activeTab === 'glossary' && (
        <ProjectGlossaryManager projectId={projectId} />
      )}
    </div>
  );
}
