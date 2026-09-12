import React, { useState, useEffect, useRef } from 'react';
import { videoMergerApi } from '../api';
import YouTubePublisherModal from '../components/YouTubePublisherModal';
import LoadingSpinner from '../components/LoadingSpinner';

export default function VideoMerger() {
  // State for video list & uploads
  const [selectedVideos, setSelectedVideos] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');

  // Asset picker modal state
  const [showAssetModal, setShowAssetModal] = useState(false);
  const [availableAssets, setAvailableAssets] = useState([]);
  const [isLoadingAssets, setIsLoadingAssets] = useState(false);

  // Merge Job State
  const [jobTitle, setJobTitle] = useState('');
  const [activeJob, setActiveJob] = useState(null);
  const [isMerging, setIsMerging] = useState(false);
  const [mergeError, setMergeError] = useState(null);

  // YouTube Publisher Modal State
  const [showPublishModal, setShowPublishModal] = useState(false);

  // Drag & drop state for reordering list items
  const [draggedIndex, setDraggedIndex] = useState(null);

  // Polling ref for job status
  const pollIntervalRef = useRef(null);

  // Load existing assets when opening asset modal
  const handleOpenAssetModal = async () => {
    setShowAssetModal(true);
    setIsLoadingAssets(true);
    try {
      const res = await videoMergerApi.listAssets();
      if (res.success && res.data) {
        setAvailableAssets(res.data);
      }
    } catch (err) {
      console.error('Failed to fetch available assets:', err);
    } finally {
      setIsLoadingAssets(false);
    }
  };

  // Upload video handler
  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    setIsUploading(true);
    setMergeError(null);

    const fileList = Array.from(files);
    const newItems = [];

    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      setUploadProgress(`Đang tải lên (${i + 1}/${fileList.length}): ${file.name}...`);
      try {
        const res = await videoMergerApi.upload(file);
        if (res.success && res.data) {
          newItems.push({
            id: res.data.id || `file_${Date.now()}_${i}`,
            original_filename: res.data.original_filename || file.name,
            file_path: res.data.file_path,
            file_size: res.data.file_size || file.size,
            duration: res.data.duration || 0,
            width: res.data.width || 0,
            height: res.data.height || 0,
            fps: res.data.fps || 30,
            has_audio: res.data.has_audio !== undefined ? res.data.has_audio : true,
            thumbnail_url: res.data.thumbnail_url || null,
          });
        }
      } catch (err) {
        const detail = err.response?.data?.detail || err.message || 'Lỗi upload';
        setMergeError(`❌ Tải file ${file.name} thất bại: ${detail}`);
      }
    }

    if (newItems.length > 0) {
      setSelectedVideos((prev) => [...prev, ...newItems]);
    }
    setIsUploading(false);
    setUploadProgress('');
  };

  // Select asset from system modal
  const handleSelectAsset = (asset) => {
    // Check if already in list
    if (selectedVideos.some((v) => v.file_path === asset.file_path)) {
      alert('⚠️ Video này đã có trong danh sách ghép.');
      return;
    }
    const newItem = {
      id: asset.id || `asset_${Date.now()}`,
      original_filename: asset.title || asset.original_filename || 'Video',
      file_path: asset.file_path,
      file_size: asset.file_size || 0,
      duration: asset.duration || 0,
      width: asset.width || 0,
      height: asset.height || 0,
      fps: asset.fps || 30,
      has_audio: asset.has_audio !== undefined ? asset.has_audio : true,
      thumbnail_url: asset.thumbnail_url || null,
    };
    setSelectedVideos((prev) => [...prev, newItem]);
    setShowAssetModal(false);
  };

  // Reordering handlers (Up / Down)
  const moveVideoItem = (fromIndex, toIndex) => {
    if (toIndex < 0 || toIndex >= selectedVideos.length) return;
    const updated = [...selectedVideos];
    const [moved] = updated.splice(fromIndex, 1);
    updated.splice(toIndex, 0, moved);
    setSelectedVideos(updated);
  };

  const removeVideoItem = (index) => {
    setSelectedVideos((prev) => prev.filter((_, idx) => idx !== index));
  };

  // Drag & Drop reordering logic
  const handleDragStart = (e, index) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e, index) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, targetIndex) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === targetIndex) return;
    moveVideoItem(draggedIndex, targetIndex);
    setDraggedIndex(null);
  };

  // Total duration calculation
  const totalDurationSeconds = selectedVideos.reduce((sum, v) => sum + (v.duration || 0), 0);
  const formatDuration = (sec) => {
    if (!sec || isNaN(sec)) return '00:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    const h = Math.floor(m / 60);
    const remM = m % 60;
    if (h > 0) {
      return `${String(h).padStart(2, '0')}:${String(remM).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 MB';
    const mb = bytes / (1024 * 1024);
    if (mb > 1024) {
      return `${(mb / 1024).toFixed(2)} GB`;
    }
    return `${mb.toFixed(1)} MB`;
  };

  // Start Merge Job
  const handleStartMerge = async () => {
    if (selectedVideos.length === 0) {
      setMergeError('❌ Vui lòng chọn ít nhất 1 video để ghép.');
      return;
    }

    setIsMerging(true);
    setMergeError(null);

    try {
      // 1. Create Job
      const formattedTitle = jobTitle.trim() || `Ghép ${selectedVideos.length} Video (${new Date().toLocaleTimeString('vi-VN')})`;
      const createRes = await videoMergerApi.createJob({
        title: formattedTitle,
        items: selectedVideos.map((v, idx) => ({ ...v, order_index: idx + 1 })),
      });

      if (!createRes.success || !createRes.data) {
        throw new Error('Khởi tạo job ghép video thất bại.');
      }

      const jobId = createRes.data.id;
      setActiveJob({ ...createRes.data, status: 'preparing', progress: 2.0 });

      // 2. Start Job Execution
      const startRes = await videoMergerApi.startJob(jobId);
      if (!startRes.success) {
        throw new Error(startRes.message || 'Không thể bắt đầu ghép video.');
      }

      // 3. Start Polling Status
      startPollingStatus(jobId);
    } catch (err) {
      console.error('Merge job start error:', err);
      const detail = err.response?.data?.detail || err.message || 'Thất bại khi bắt đầu ghép video';
      setMergeError(`❌ ${detail}`);
      setIsMerging(false);
    }
  };

  // Status Polling logic
  const startPollingStatus = (jobId) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

    pollIntervalRef.current = setInterval(async () => {
      try {
        const res = await videoMergerApi.getJobStatus(jobId);
        if (res.success && res.data) {
          const jobData = res.data;
          setActiveJob(jobData);

          if (jobData.status === 'completed') {
            clearInterval(pollIntervalRef.current);
            setIsMerging(false);
          } else if (jobData.status === 'failed') {
            clearInterval(pollIntervalRef.current);
            setIsMerging(false);
            setMergeError(jobData.error_message || '❌ Tiến trình ghép video thất bại.');
          }
        }
      } catch (err) {
        console.error('Polling merge status error:', err);
      }
    }, 1200);
  };

  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);

  // Retry failed job
  const handleRetryJob = async () => {
    if (!activeJob) return;
    setIsMerging(true);
    setMergeError(null);
    try {
      await videoMergerApi.retryJob(activeJob.id);
      startPollingStatus(activeJob.id);
    } catch (err) {
      setMergeError(`❌ Retry thất bại: ${err.message}`);
      setIsMerging(false);
    }
  };

  // Reset merger page for new job
  const handleResetNewMerge = () => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    setActiveJob(null);
    setSelectedVideos([]);
    setMergeError(null);
    setIsMerging(false);
    setJobTitle('');
  };

  const handleDownloadOutput = () => {
    if (!activeJob) return;
    const rawPath = activeJob.output_relative_url
      ? activeJob.output_relative_url.replace('/api/storage/files/', '')
      : activeJob.output_video_path || '';
    if (!rawPath) {
      alert('❌ Chưa tìm thấy đường dẫn file video kết quả.');
      return;
    }
    const filename = activeJob.output_filename || `merged_${activeJob.id}.mp4`;
    const downloadUrl = `/api/storage/download?path=${encodeURIComponent(rawPath)}&filename=${encodeURIComponent(filename)}`;
    window.open(downloadUrl, '_blank');
  };

  return (
    <div className="video-merger-page" style={{ maxWidth: '1280px', margin: '0 auto', padding: '1.5rem 1rem' }}>
      {/* Header Banner */}
      <div className="merger-header-card card" style={{ padding: '1.5rem', marginBottom: '1.5rem', borderRadius: '12px', background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)', border: '1px solid #334155' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.6rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              🎬 Video Merger — Ghép Video Độc Lập
            </h1>
            <p style={{ margin: '0.4rem 0 0 0', color: '#94a3b8', fontSize: '0.95rem' }}>
              Nối nhiều video thành một video duy nhất theo thứ tự mong muốn với công nghệ FFmpeg tự động normalize resolution, fps và âm thanh.
            </p>
          </div>
          {activeJob && activeJob.status === 'completed' && (
            <button className="btn btn-secondary" onClick={handleResetNewMerge} style={{ padding: '0.5rem 1rem' }}>
              🔄 Ghép Video Mới
            </button>
          )}
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="merger-grid" style={{ display: 'grid', gridTemplateColumns: activeJob && activeJob.status === 'completed' ? '1fr 1fr' : '1fr 1.2fr', gap: '1.5rem' }}>
        
        {/* Left Column: Source Selection & Reordering List */}
        <div className="merger-left-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
          
          {/* Upload & Select Section */}
          <div className="card" style={{ padding: '1.2rem', borderRadius: '12px', background: '#1e293b', border: '1px solid #334155' }}>
            <h3 style={{ margin: '0 0 0.8rem 0', fontSize: '1.1rem', color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              📥 Nguồn Video Input
            </h3>
            
            {/* Dropzone */}
            <div
              className="upload-dropzone"
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                handleFileUpload(e.dataTransfer.files);
              }}
              style={{
                border: '2px dashed #475569',
                borderRadius: '10px',
                padding: '1.5rem',
                textAlign: 'center',
                background: '#0f172a',
                cursor: 'pointer',
                transition: 'border-color 0.2s',
              }}
              onClick={() => document.getElementById('merger-file-input').click()}
            >
              <input
                id="merger-file-input"
                type="file"
                multiple
                accept="video/*,.mp4,.mov,.avi,.mkv,.webm"
                style={{ display: 'none' }}
                onChange={(e) => handleFileUpload(e.target.files)}
              />
              <div style={{ fontSize: '2.2rem', marginBottom: '0.5rem' }}>📁</div>
              <p style={{ margin: 0, fontWeight: 600, color: '#f1f5f9' }}>
                Kéo thả nhiều video vào đây hoặc <span style={{ color: '#38bdf8', textDecoration: 'underline' }}>Duyệt file từ máy</span>
              </p>
              <p style={{ margin: '0.4rem 0 0 0', fontSize: '0.8rem', color: '#64748b' }}>
                Hỗ trợ MP4, MOV, AVI, MKV, WEBM (Nối trực tiếp hoặc tự động normalize)
              </p>
            </div>

            {/* Existing Asset Selection Button */}
            <div style={{ marginTop: '0.8rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleOpenAssetModal}
                style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem', background: '#334155', border: 'none', color: '#f8fafc', padding: '0.6rem 1rem', borderRadius: '8px', cursor: 'pointer' }}
              >
                📂 Chọn từ Dự án / Asset có sẵn
              </button>
            </div>

            {isUploading && (
              <div style={{ marginTop: '0.8rem', padding: '0.6rem', borderRadius: '6px', background: '#0284c722', border: '1px solid #38bdf844', color: '#38bdf8', fontSize: '0.88rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <LoadingSpinner size="sm" />
                <span>{uploadProgress}</span>
              </div>
            )}
          </div>

          {/* Selected Video Sequence List */}
          <div className="card" style={{ padding: '1.2rem', borderRadius: '12px', background: '#1e293b', border: '1px solid #334155' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.8rem' }}>
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#f8fafc' }}>
                📋 Danh sách Ghép ({selectedVideos.length} video)
              </h3>
              {selectedVideos.length > 0 && (
                <button
                  type="button"
                  onClick={() => setSelectedVideos([])}
                  disabled={isMerging}
                  style={{ background: 'transparent', border: 'none', color: '#ef4444', fontSize: '0.82rem', cursor: 'pointer', textDecoration: 'underline' }}
                >
                  Xóa tất cả
                </button>
              )}
            </div>

            {selectedVideos.length === 0 ? (
              <div style={{ padding: '2rem 1rem', textAlign: 'center', color: '#64748b', background: '#0f172a', borderRadius: '8px' }}>
                <p style={{ margin: 0 }}>Chưa chọn video nào. Vui lòng upload hoặc chọn video để bắt đầu ghép.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', maxHeight: '420px', overflowY: 'auto', paddingRight: '0.2rem' }}>
                {selectedVideos.map((video, idx) => (
                  <div
                    key={video.id + '_' + idx}
                    draggable={!isMerging}
                    onDragStart={(e) => handleDragStart(e, idx)}
                    onDragOver={(e) => handleDragOver(e, idx)}
                    onDrop={(e) => handleDrop(e, idx)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.8rem',
                      padding: '0.6rem 0.8rem',
                      borderRadius: '8px',
                      background: draggedIndex === idx ? '#334155' : '#0f172a',
                      border: '1px solid #334155',
                      cursor: isMerging ? 'default' : 'grab',
                      transition: 'background 0.2s',
                    }}
                  >
                    {/* Order Badge */}
                    <div style={{ minWidth: '28px', height: '28px', borderRadius: '50%', background: '#0284c7', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>
                      {idx + 1}
                    </div>

                    {/* Thumbnail Preview */}
                    {video.thumbnail_url ? (
                      <img
                        src={video.thumbnail_url}
                        alt="thumb"
                        style={{ width: '48px', height: '32px', objectFit: 'cover', borderRadius: '4px', background: '#000' }}
                      />
                    ) : (
                      <div style={{ width: '48px', height: '32px', borderRadius: '4px', background: '#1e293b', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.9rem', color: '#94a3b8' }}>
                        🎥
                      </div>
                    )}

                    {/* Info */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#f1f5f9', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={video.original_filename}>
                        {video.original_filename}
                      </div>
                      <div style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'flex', gap: '0.6rem', marginTop: '0.2rem' }}>
                        <span>⏱️ {formatDuration(video.duration)}</span>
                        <span>💾 {formatFileSize(video.file_size)}</span>
                        {video.width > 0 && <span>📐 {video.width}x{video.height}</span>}
                        <span>{video.has_audio ? '🔊' : '🔇 Audio'}</span>
                      </div>
                    </div>

                    {/* Reorder & Action Buttons */}
                    {!isMerging && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                        <button
                          type="button"
                          disabled={idx === 0}
                          onClick={() => moveVideoItem(idx, idx - 1)}
                          title="Lên trên"
                          style={{ background: '#1e293b', border: '1px solid #475569', color: '#cbd5e1', borderRadius: '4px', padding: '2px 6px', cursor: idx === 0 ? 'not-allowed' : 'pointer' }}
                        >
                          ▲
                        </button>
                        <button
                          type="button"
                          disabled={idx === selectedVideos.length - 1}
                          onClick={() => moveVideoItem(idx, idx + 1)}
                          title="Xuống dưới"
                          style={{ background: '#1e293b', border: '1px solid #475569', color: '#cbd5e1', borderRadius: '4px', padding: '2px 6px', cursor: idx === selectedVideos.length - 1 ? 'not-allowed' : 'pointer' }}
                        >
                          ▼
                        </button>
                        <button
                          type="button"
                          onClick={() => removeVideoItem(idx)}
                          title="Xóa khỏi danh sách"
                          style={{ background: 'transparent', border: 'none', color: '#f87171', padding: '2px 6px', cursor: 'pointer', fontSize: '1rem', marginLeft: '0.2rem' }}
                        >
                          🗑️
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Total Summary Footer */}
            {selectedVideos.length > 0 && (
              <div style={{ marginTop: '1rem', paddingTop: '0.8rem', borderTop: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#cbd5e1', fontSize: '0.9rem' }}>
                <span>Tổng số: <strong>{selectedVideos.length} video</strong></span>
                <span>Tổng thời lượng: <strong style={{ color: '#38bdf8' }}>{formatDuration(totalDurationSeconds)}</strong></span>
              </div>
            )}
          </div>

        </div>

        {/* Right Column: Execution Controls, Progress & Result Studio */}
        <div className="merger-right-panel" style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
          
          {/* Controls & Action Card */}
          <div className="card" style={{ padding: '1.2rem', borderRadius: '12px', background: '#1e293b', border: '1px solid #334155' }}>
            <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', color: '#38bdf8' }}>
              ⚡ Cấu hình & Thực hiện Merge
            </h3>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.88rem', color: '#94a3b8', marginBottom: '0.4rem' }}>
                Tên file / Tiêu đề Video kết quả (tùy chọn):
              </label>
              <input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder={`Ví dụ: Video_Tong_Hop_${new Date().toISOString().slice(0, 10)}`}
                disabled={isMerging}
                style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', background: '#0f172a', border: '1px solid #475569', color: '#f8fafc', fontSize: '0.9rem' }}
              />
            </div>

            {/* Error Banner */}
            {mergeError && (
              <div style={{ padding: '0.8rem 1rem', borderRadius: '8px', background: '#450a0a', border: '1px solid #ef4444', color: '#fca5a5', fontSize: '0.88rem', marginBottom: '1rem' }}>
                <div style={{ fontWeight: 600, marginBottom: '0.3rem' }}>⚠️ Báo Lỗi ghép video:</div>
                <div style={{ wordBreak: 'break-word' }}>{mergeError}</div>
                {activeJob && activeJob.status === 'failed' && (
                  <button
                    type="button"
                    onClick={handleRetryJob}
                    className="btn btn-secondary"
                    style={{ marginTop: '0.6rem', padding: '0.3rem 0.8rem', fontSize: '0.82rem', background: '#ef4444', border: 'none', color: '#fff' }}
                  >
                    🔁 Thử lại tiến trình
                  </button>
                )}
              </div>
            )}

            {/* Merge Action Button */}
            <button
              type="button"
              className="btn btn-primary"
              disabled={isMerging || selectedVideos.length < 1}
              onClick={handleStartMerge}
              style={{
                width: '100%',
                padding: '0.86rem',
                fontSize: '1.05rem',
                fontWeight: 700,
                borderRadius: '8px',
                background: isMerging || selectedVideos.length < 1 ? '#475569' : 'linear-gradient(135deg, #0284c7 0%, #2563eb 100%)',
                color: '#ffffff',
                border: 'none',
                cursor: isMerging || selectedVideos.length < 1 ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.6rem',
                boxShadow: isMerging ? 'none' : '0 4px 14px rgba(2, 132, 199, 0.3)',
              }}
            >
              {isMerging ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Đang xử lý Ghép Video... ({activeJob?.progress ? `${activeJob.progress.toFixed(0)}%` : '0%'})</span>
                </>
              ) : (
                <>
                  <span>⚡ Ghép {selectedVideos.length} Video Ngay</span>
                </>
              )}
            </button>
          </div>

          {/* Processing / Progress Card */}
          {activeJob && (activeJob.status === 'preparing' || activeJob.status === 'processing') && (
            <div className="card" style={{ padding: '1.2rem', borderRadius: '12px', background: '#0f172a', border: '1px solid #0284c7' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
                <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#38bdf8' }}>
                  ⏳ Tiến trình FFmpeg Concat & Normalization
                </span>
                <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#38bdf8' }}>
                  {activeJob.progress ? `${activeJob.progress.toFixed(1)}%` : '0%'}
                </span>
              </div>

              {/* Progress Bar Container */}
              <div style={{ width: '100%', height: '10px', background: '#1e293b', borderRadius: '5px', overflow: 'hidden', marginBottom: '0.8rem' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${Math.min(100, Math.max(0, activeJob.progress || 0))}%`,
                    background: 'linear-gradient(90deg, #38bdf8 0%, #3b82f6 100%)',
                    transition: 'width 0.4s ease',
                  }}
                />
              </div>

              <div style={{ fontSize: '0.82rem', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
                <span>Trạng thái: <strong>{activeJob.status.toUpperCase()}</strong></span>
                <span>Đã xử lý: {activeJob.processed_duration ? `${activeJob.processed_duration}s` : '0s'} / {activeJob.total_duration}s</span>
              </div>
            </div>
          )}

          {/* Output Result Studio */}
          {activeJob && activeJob.status === 'completed' && activeJob.output_relative_url && (
            <div className="card" style={{ padding: '1.2rem', borderRadius: '12px', background: '#1e293b', border: '1px solid #10b981' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#10b981', fontWeight: 700, fontSize: '1.1rem', marginBottom: '1rem' }}>
                <span>✅ Ghép Video Thành Công!</span>
              </div>

              {/* HTML5 Video Player */}
              <div style={{ background: '#000', borderRadius: '8px', overflow: 'hidden', marginBottom: '1rem' }}>
                <video
                  controls
                  src={activeJob.output_relative_url}
                  style={{ width: '100%', maxHeight: '360px', display: 'block' }}
                />
              </div>

              {/* Download & Publish Actions */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.8rem' }}>
                <button
                  type="button"
                  onClick={handleDownloadOutput}
                  className="btn btn-primary"
                  style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', background: '#10b981', border: 'none', color: '#fff', padding: '0.65rem 1rem', borderRadius: '8px', fontWeight: 600, cursor: 'pointer' }}
                >
                  📥 Tải Video Kết Quả
                </button>

                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowPublishModal(true)}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#0284c7', border: 'none', color: '#fff', padding: '0.65rem 1rem', borderRadius: '8px', fontWeight: 600, cursor: 'pointer' }}
                >
                  🌐 Tải lên YouTube
                </button>
              </div>
            </div>
          )}

        </div>
      </div>

      {/* Asset Selection Modal */}
      {showAssetModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.75)', zIndex: 999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
          <div className="card" style={{ width: '100%', maxWidth: '640px', maxHeight: '80vh', display: 'flex', flexDirection: 'column', borderRadius: '12px', background: '#1e293b', border: '1px solid #475569', padding: '1.2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#f8fafc' }}>
                📂 Chọn Video có sẵn trong Hệ Thống
              </h3>
              <button
                type="button"
                onClick={() => setShowAssetModal(false)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', fontSize: '1.4rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            {isLoadingAssets ? (
              <div style={{ padding: '3rem', textAlign: 'center' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.8rem', color: '#94a3b8' }}>Đang tải danh sách asset...</p>
              </div>
            ) : availableAssets.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>
                Chưa có asset video nào trong hệ thống. Bạn có thể upload video trực tiếp ở trang chính.
              </div>
            ) : (
              <div style={{ overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem', paddingRight: '0.2rem' }}>
                {availableAssets.map((asset) => (
                  <div
                    key={asset.id}
                    onClick={() => handleSelectAsset(asset)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.8rem',
                      padding: '0.6rem 0.8rem',
                      borderRadius: '8px',
                      background: '#0f172a',
                      border: '1px solid #334155',
                      cursor: 'pointer',
                      transition: 'background 0.2s',
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#334155'}
                    onMouseLeave={(e) => e.currentTarget.style.background = '#0f172a'}
                  >
                    <div style={{ width: '40px', height: '30px', borderRadius: '4px', background: '#1e293b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      🎬
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.88rem', color: '#f1f5f9', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {asset.title || asset.original_filename}
                      </div>
                      <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                        ⏱️ {formatDuration(asset.duration)} | {formatFileSize(asset.file_size)}
                      </div>
                    </div>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      style={{ padding: '0.3rem 0.7rem', fontSize: '0.8rem', background: '#0284c7', color: '#fff', border: 'none', borderRadius: '6px' }}
                    >
                      + Chọn
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Optional YouTube Publisher Modal */}
      {showPublishModal && activeJob && (
        <YouTubePublisherModal
          jobId={activeJob.id}
          videoPath={activeJob.output_video_path}
          onClose={() => setShowPublishModal(false)}
        />
      )}
    </div>
  );
}
