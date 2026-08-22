import React, { useState, useEffect } from 'react';
import './AppSelector.css';

export default function AppSelector({ onSelectApp, currentApp }) {
  const [appsStatus, setAppsStatus] = useState({
    workflow_vd_ai: { running: true, port: 8000, name: 'WorkflowVdAi (Original)' },
    krillin_ai: { running: false, port: 8888, name: 'KrillinAI' },
    py_video_trans: { running: false, port: 9999, name: 'pyVideoTrans' },
    soni_translate: { running: false, port: 7860, name: 'SoniTranslate' },
  });
  const [loadingApp, setLoadingApp] = useState(null);

  const checkStatus = async () => {
    try {
      const res = await fetch('/api/apps/status');
      if (res.ok) {
        const data = await res.json();
        setAppsStatus((prev) => ({ ...prev, ...data }));
      }
    } catch (e) {
      // Backend status endpoint quiet fallback
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleLaunchOrOpen = async (appKey) => {
    if (appKey === 'workflow_vd_ai') {
      onSelectApp('workflow_vd_ai');
      return;
    }

    setLoadingApp(appKey);
    try {
      // Direct navigate to viewer frame
      onSelectApp(appKey);
      
      const res = await fetch(`/api/apps/launch/${appKey}`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setAppsStatus((prev) => ({
          ...prev,
          [appKey]: { ...prev[appKey], running: true, url: data.url },
        }));
      }
    } catch (err) {
      console.error("Failed to launch app:", err);
    } finally {
      setLoadingApp(null);
    }
  };

  return (
    <div className="app-selector-container">
      <div className="app-selector-header">
        <h1 className="selector-title">AI VIDEO TOOLS</h1>
        <p className="selector-subtitle">Chọn ứng dụng muốn sử dụng</p>
      </div>

      <div className="app-grid">
        {/* WorkflowVdAi (Original) */}
        <div className={`app-card ${currentApp === 'workflow_vd_ai' ? 'active-app' : ''}`}>
          <div className="app-card-badge status-online">Sẵn sàng</div>
          <div className="app-icon">⚡</div>
          <h2 className="app-name">WorkflowVdAi</h2>
          <p className="app-desc">Quy trình sản xuất video từ kịch bản hiện tại.</p>
          <button
            className="app-launch-btn primary-btn"
            onClick={() => handleLaunchOrOpen('workflow_vd_ai')}
          >
            {currentApp === 'workflow_vd_ai' ? 'Đang mở' : 'Mở ứng dụng'}
          </button>
        </div>

        {/* KrillinAI */}
        <div className={`app-card ${currentApp === 'krillin_ai' ? 'active-app' : ''}`}>
          <div className={`app-card-badge ${appsStatus.krillin_ai?.running ? 'status-online' : 'status-offline'}`}>
            {appsStatus.krillin_ai?.running ? 'Đang chạy' : 'Chưa chạy'}
          </div>
          <div className="app-icon">🎬</div>
          <h2 className="app-name">KrillinAI</h2>
          <p className="app-desc">Dịch video, nhân bản giọng nói, tạo phụ đề và các công cụ AI.</p>
          <button
            className="app-launch-btn"
            disabled={loadingApp === 'krillin_ai'}
            onClick={() => handleLaunchOrOpen('krillin_ai')}
          >
            {loadingApp === 'krillin_ai' ? 'Đang khởi chạy...' : 'Mở ứng dụng'}
          </button>
        </div>

        {/* pyVideoTrans */}
        <div className={`app-card ${currentApp === 'py_video_trans' ? 'active-app' : ''}`}>
          <div className={`app-card-badge ${appsStatus.py_video_trans?.running ? 'status-online' : 'status-offline'}`}>
            {appsStatus.py_video_trans?.running ? 'Đang chạy' : 'Chưa chạy'}
          </div>
          <div className="app-icon">🎥</div>
          <h2 className="app-name">pyVideoTrans</h2>
          <p className="app-desc">Tự động dịch video, lồng tiếng và tạo phụ đề SRT bằng Whisper.</p>
          <button
            className="app-launch-btn"
            disabled={loadingApp === 'py_video_trans'}
            onClick={() => handleLaunchOrOpen('py_video_trans')}
          >
            {loadingApp === 'py_video_trans' ? 'Đang khởi chạy...' : 'Mở ứng dụng'}
          </button>
        </div>

        {/* SoniTranslate */}
        <div className={`app-card ${currentApp === 'soni_translate' ? 'active-app' : ''}`}>
          <div className={`app-card-badge ${appsStatus.soni_translate?.running ? 'status-online' : 'status-offline'}`}>
            {appsStatus.soni_translate?.running ? 'Đang chạy' : 'Chưa chạy'}
          </div>
          <div className="app-icon">🌐</div>
          <h2 className="app-name">SoniTranslate</h2>
          <p className="app-desc">Ứng dụng web dịch video và phân tách người nói.</p>
          <button
            className="app-launch-btn"
            disabled={loadingApp === 'soni_translate'}
            onClick={() => handleLaunchOrOpen('soni_translate')}
          >
            {loadingApp === 'soni_translate' ? 'Đang khởi chạy...' : 'Mở ứng dụng'}
          </button>
        </div>
      </div>
    </div>
  );
}
