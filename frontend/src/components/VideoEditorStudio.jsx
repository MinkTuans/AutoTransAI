import React, { useState } from 'react';
import { videoEditorApi } from '../api';

export default function VideoEditorStudio({ jobId, onConfigSaved }) {
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [logoPosition, setLogoPosition] = useState('top_right');
  const [logoScale, setLogoScale] = useState(0.15);
  const [logoOpacity, setLogoOpacity] = useState(0.85);
  const [bgmVolumeDb, setBgmVolumeDb] = useState(-18.0);
  const [enableBgmDucking, setEnableBgmDucking] = useState(true);
  const [enableBurnedSubtitles, setEnableBurnedSubtitles] = useState(true);

  const [saving, setSaving] = useState(false);
  const [uploadingLogo, setUploadingLogo] = useState(false);
  const [msg, setMsg] = useState(null);

  const handleLogoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploadingLogo(true);
    try {
      const res = await videoEditorApi.uploadLogo(jobId, file);
      if (res.success) {
        setMsg(`✅ Đã upload logo: ${res.data.filename}`);
      }
    } catch (err) {
      setMsg(`❌ Lỗi upload logo: ${err.message}`);
    } finally {
      setUploadingLogo(false);
    }
  };

  const handleSaveConfig = async () => {
    setSaving(true);
    setMsg(null);
    try {
      const res = await videoEditorApi.saveConfig({
        job_id: jobId,
        target_aspect_ratio: aspectRatio,
        logo_position: logoPosition,
        logo_scale: parseFloat(logoScale),
        logo_opacity: parseFloat(logoOpacity),
        bgm_volume_db: parseFloat(bgmVolumeDb),
        enable_bgm_ducking: enableBgmDucking,
        enable_burned_subtitles: enableBurnedSubtitles,
      });
      if (res.success) {
        setMsg('✅ Đã lưu cấu hình dựng video thành công!');
        if (onConfigSaved) onConfigSaved();
      }
    } catch (err) {
      setMsg(`❌ Lỗi lưu cấu hình: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{
      background: '#1a1f2c',
      borderRadius: '12px',
      padding: '20px',
      border: '1px solid #2d3748',
      color: '#e2e8f0',
      marginTop: '20px',
    }}>
      <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#6366f1' }}>
        🎬 Video Editing & Branding Automation Studio
      </h3>

      {msg && (
        <div style={{
          padding: '10px 14px',
          borderRadius: '8px',
          background: msg.startsWith('✅') ? '#064e3b' : '#7f1d1d',
          color: '#fff',
          marginBottom: '16px',
          fontSize: '14px',
        }}>
          {msg}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {/* Aspect Ratio */}
        <div>
          <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: 'bold' }}>
            📐 Khung hình (Aspect Ratio):
          </label>
          <select
            value={aspectRatio}
            onChange={(e) => setAspectRatio(e.target.value)}
            style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #334155' }}
          >
            <option value="16:9">16:9 Landscape (Ngang - YouTube / TV)</option>
            <option value="9:16">9:16 Portrait (Dọc - TikTok / Shorts / Reels)</option>
            <option value="1:1">1:1 Square (Vuông - Facebook / Instagram)</option>
          </select>
        </div>

        {/* Logo Position */}
        <div>
          <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: 'bold' }}>
            🏷️ Vị trí Logo Watermark:
          </label>
          <select
            value={logoPosition}
            onChange={(e) => setLogoPosition(e.target.value)}
            style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #334155' }}
          >
            <option value="top_right">Góc trên bên phải (Top Right)</option>
            <option value="top_left">Góc trên bên trái (Top Left)</option>
            <option value="bottom_right">Góc dưới bên phải (Bottom Right)</option>
            <option value="bottom_left">Góc dưới bên trái (Bottom Left)</option>
            <option value="center">Chính giữa (Center)</option>
          </select>
        </div>

        {/* Upload Logo PNG */}
        <div>
          <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: 'bold' }}>
            🖼️ Upload Logo File (PNG):
          </label>
          <input
            type="file"
            accept="image/png,image/jpeg"
            onChange={handleLogoUpload}
            disabled={uploadingLogo}
            style={{ width: '100%', fontSize: '13px' }}
          />
        </div>

        {/* Logo Opacity */}
        <div>
          <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px', fontWeight: 'bold' }}>
            ✨ Độ mờ Logo (Opacity): {Math.round(logoOpacity * 100)}%
          </label>
          <input
            type="range"
            min="0.1"
            max="1.0"
            step="0.05"
            value={logoOpacity}
            onChange={(e) => setLogoOpacity(e.target.value)}
            style={{ width: '100%' }}
          />
        </div>

        {/* Subtitles Option */}
        <div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', marginTop: '12px' }}>
            <input
              type="checkbox"
              checked={enableBurnedSubtitles}
              onChange={(e) => setEnableBurnedSubtitles(e.target.checked)}
            />
            🔥 Ghi đè Phụ đề động CapCut/TikTok Style (.ass)
          </label>
        </div>

        {/* BGM Ducking Option */}
        <div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', marginTop: '12px' }}>
            <input
              type="checkbox"
              checked={enableBgmDucking}
              onChange={(e) => setEnableBgmDucking(e.target.checked)}
            />
            🎵 Tự động hạ âm lượng Nhạc nền (Auto-Ducking)
          </label>
        </div>
      </div>

      <button
        onClick={handleSaveConfig}
        disabled={saving}
        style={{
          marginTop: '20px',
          padding: '10px 20px',
          borderRadius: '8px',
          background: '#6366f1',
          color: '#fff',
          fontWeight: 'bold',
          border: 'none',
          cursor: 'pointer',
        }}
      >
        {saving ? '⏳ Đang lưu...' : '💾 Lưu Cấu Hình Dựng Video'}
      </button>
    </div>
  );
}
