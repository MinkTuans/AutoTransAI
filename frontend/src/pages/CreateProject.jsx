import React, { useState, useMemo } from 'react';
import { projectsApi } from '../api';

const SAMPLE_SCRIPT = `Phân đoạn 1: Hello everyone! Welcome to our video production workflow demonstration.
Phân đoạn 2: In this project, we process your script locally, segment by segment.
Phân đoạn 3: Audio and video generated per segment are perfectly synchronized using FFmpeg.
Phân đoạn 4: Enjoy smooth, error-resilient video production right on your computer.`;

export default function CreateProject({ onProjectCreated }) {
  const [title, setTitle] = useState('My Video Project');
  const [script, setScript] = useState(SAMPLE_SCRIPT);
  const [workflowMode, setWorkflowMode] = useState('audio_video');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  // Live parsing stats calculation
  const stats = useMemo(() => {
    if (!script.trim()) return { segments: 0, chars: 0, estDuration: 0 };
    
    // Quick regex segment match
    const phanDoanMatches = script.match(/Phân\s+đoạn\s+\d+/gi);
    const segmentMatches = script.match(/Segment\s+\d+/gi);
    const numberedMatches = script.match(/^\d+[\:\.]/gm);
    
    let count = 0;
    if (phanDoanMatches) count = phanDoanMatches.length;
    else if (segmentMatches) count = segmentMatches.length;
    else if (numberedMatches) count = numberedMatches.length;
    else count = script.split(/\n\s*\n/).filter(p => p.trim()).length;

    const chars = script.length;
    const estDurationSec = Math.round(chars / 13); // ~13 chars/sec estimate

    return {
      segments: count,
      chars,
      estDurationSec,
    };
  }, [script]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!script.trim()) {
      setError('Script cannot be empty');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const res = await projectsApi.create({
        title,
        script,
        workflow_mode: workflowMode,
      });

      if (res.success) {
        onProjectCreated(res.data.project_id);
      } else {
        setError(res.error?.message || 'Failed to create project');
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map(d => d.msg || JSON.stringify(d)).join('; '));
      } else if (typeof detail === 'object' && detail !== null) {
        setError(JSON.stringify(detail));
      } else {
        setError(detail || err.message || 'Failed to create project');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `~${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Create New Project</h1>
          <p className="page-subtitle">Paste your structured script below</p>
        </div>
      </div>

      {error && (
        <div className="banner banner-danger">
          <span>❌ {error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="card">
          <div className="form-group">
            <label className="form-label">Project Title</label>
            <input
              type="text"
              className="form-control"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. AI Video Demo"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Workflow Mode</label>
            <div className="radio-cards">
              <div
                className={`radio-card ${workflowMode === 'audio_only' ? 'selected' : ''}`}
                onClick={() => setWorkflowMode('audio_only')}
              >
                <input
                  type="radio"
                  name="mode"
                  checked={workflowMode === 'audio_only'}
                  onChange={() => setWorkflowMode('audio_only')}
                />
                <div>
                  <strong>🎙️ Mode 1: Audio Only</strong>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Generates WAV audio files for each segment using Text-to-Speech.
                  </p>
                </div>
              </div>

              <div
                className={`radio-card ${workflowMode === 'audio_video' ? 'selected' : ''}`}
                onClick={() => setWorkflowMode('audio_video')}
              >
                <input
                  type="radio"
                  name="mode"
                  checked={workflowMode === 'audio_video'}
                  onChange={() => setWorkflowMode('audio_video')}
                />
                <div>
                  <strong>🎥 Mode 2: Audio + Video</strong>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Generates Audio + Video clips per segment, syncs timing, and merges into final MP4.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Script Input</label>
            <textarea
              className="form-textarea"
              value={script}
              onChange={(e) => setScript(e.target.value)}
              placeholder="Phân đoạn 1: Hello everyone..."
            />
          </div>

          {/* Live Parse Stats Preview */}
          <div className="card" style={{ backgroundColor: 'var(--bg-primary)', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-around', textAlign: 'center' }}>
              <div>
                <span style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--accent-primary)' }}>
                  {stats.segments}
                </span>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Segments</p>
              </div>
              <div>
                <span style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--accent-primary)' }}>
                  {stats.chars.toLocaleString()}
                </span>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Characters</p>
              </div>
              <div>
                <span style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--accent-primary)' }}>
                  {formatTime(stats.estDurationSec)}
                </span>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Est. Audio Duration</p>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting || stats.segments === 0}
            >
              {submitting ? 'Parsing & Creating...' : 'Continue to Configuration →'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
