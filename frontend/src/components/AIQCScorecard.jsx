import React, { useState } from 'react';
import { videoEditorApi } from '../api';

export default function AIQCScorecard({ jobId }) {
  const [running, setRunning] = useState(false);
  const [qcResult, setQcResult] = useState(null);
  const [error, setError] = useState(null);

  const handleRunQC = async () => {
    setRunning(true);
    setError(null);
    try {
      const res = await videoEditorApi.runQC(jobId);
      if (res.success) {
        setQcResult(res.data);
      }
    } catch (err) {
      setError(err.message || 'Lỗi chạy kiểm định AI QC');
    } finally {
      setRunning(false);
    }
  };

  const getBadgeColor = (status) => {
    if (status === 'PASSED') return '#059669';
    if (status === 'WARNING') return '#d97706';
    return '#dc2626';
  };

  return (
    <div style={{
      background: '#0f172a',
      borderRadius: '12px',
      padding: '20px',
      border: '1px solid #1e293b',
      color: '#e2e8f0',
      marginTop: '20px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ margin: 0, fontSize: '18px', color: '#10b981', display: 'flex', alignItems: 'center', gap: '8px' }}>
          🛡️ AI Quality Control (AI QC Auditor)
        </h3>
        <button
          onClick={handleRunQC}
          disabled={running}
          style={{
            padding: '8px 16px',
            borderRadius: '6px',
            background: '#10b981',
            color: '#fff',
            fontWeight: 'bold',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          {running ? '⏳ Đang kiểm định QC...' : '⚡ Chạy Kiểm Định AI QC'}
        </button>
      </div>

      {error && (
        <div style={{ padding: '10px', borderRadius: '6px', background: '#7f1d1d', color: '#fff', fontSize: '14px', marginBottom: '16px' }}>
          ❌ {error}
        </div>
      )}

      {qcResult && (
        <div>
          {/* Header Score Badge */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            padding: '14px',
            borderRadius: '8px',
            background: '#1e293b',
            marginBottom: '16px',
          }}>
            <div style={{
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              background: getBadgeColor(qcResult.qc_status),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '22px',
              fontWeight: 'bold',
              color: '#fff',
            }}>
              {qcResult.overall_score}
            </div>
            <div>
              <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                Trạng thái QC: <span style={{ color: getBadgeColor(qcResult.qc_status) }}>{qcResult.qc_status}</span>
              </div>
              <div style={{ fontSize: '13px', color: '#94a3b8' }}>
                Điểm đánh giá tổng quan dựa trên Audio LUFS, Sync Drift & Gemini Audit.
              </div>
            </div>
          </div>

          {/* Grid Metrics */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px' }}>
            <div style={{ padding: '12px', background: '#1e293b', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>Audio Loudness</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#38bdf8' }}>{qcResult.audio_lufs} LUFS</div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>Target: -14.0 LUFS</div>
            </div>

            <div style={{ padding: '12px', background: '#1e293b', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>Sync Drift</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#38bdf8' }}>{qcResult.sync_drift_ms} ms</div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>Tối đa: 1500ms</div>
            </div>

            <div style={{ padding: '12px', background: '#1e293b', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>Safety Score</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#34d399' }}>{qcResult.content_safety_score}%</div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>An toàn nội dung</div>
            </div>

            <div style={{ padding: '12px', background: '#1e293b', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>Translation Quality</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#a78bfa' }}>{qcResult.translation_quality_score}%</div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>Chất lượng bản dịch</div>
            </div>
          </div>

          {/* Issues Checklist */}
          {qcResult.issues && qcResult.issues.length > 0 ? (
            <div style={{ background: '#331818', padding: '12px', borderRadius: '8px', border: '1px solid #7f1d1d' }}>
              <div style={{ fontWeight: 'bold', color: '#f87171', marginBottom: '8px', fontSize: '14px' }}>
                ⚠️ Vấn đề phát hiện ({qcResult.issues.length}):
              </div>
              <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: '#fca5a5' }}>
                {qcResult.issues.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
          ) : (
            <div style={{ background: '#064e3b', padding: '10px 14px', borderRadius: '8px', color: '#6ee7b7', fontSize: '14px' }}>
              🎉 Không phát hiện lỗi chất lượng nào. Video đạt chuẩn phát hành!
            </div>
          )}
        </div>
      )}
    </div>
  );
}
