import React, { useState, useEffect, useRef } from 'react';
import { projectsApi, providersApi } from '../api';

export default function ProjectDetail({ projectId, onBack }) {
  const [project, setProject] = useState(null);
  const [providers, setProviders] = useState({ audio: [], video: [], llm: [] });
  const [voices, setVoices] = useState([]);
  const [estimate, setEstimate] = useState(null);
  const [preflight, setPreflight] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);

  // Selected configuration state
  const [selectedAudioProvider, setSelectedAudioProvider] = useState('edge_tts');
  const [selectedVideoProvider, setSelectedVideoProvider] = useState('');
  const [selectedVoice, setSelectedVoice] = useState('');
  const [selectedVoiceName, setSelectedVoiceName] = useState('');
  const [syncStrategy, setSyncStrategy] = useState('trim_video');

  const pollIntervalRef = useRef(null);

  // Load project details and provider list
  const loadProjectData = async () => {
    try {
      const [projRes, provRes] = await Promise.all([
        projectsApi.get(projectId),
        providersApi.list(),
      ]);

      if (projRes.success) {
        const p = projRes.data;
        setProject(p);
        setSelectedAudioProvider(p.audio_provider_id || 'edge_tts');
        setSelectedVideoProvider(p.video_provider_id || '');
        setSelectedVoice(p.voice_id || '');
        setSelectedVoiceName(p.voice_name || '');
        setSyncStrategy(p.sync_strategy || 'trim_video');
      }

      if (provRes.success) {
        setProviders(provRes.data);
      }
    } catch (err) {
      setError('Failed to load project details');
    } finally {
      setLoading(false);
    }
  };

  // Load voices whenever audio provider changes
  useEffect(() => {
    if (selectedAudioProvider) {
      providersApi.listVoices(selectedAudioProvider)
        .then(res => {
          if (res.success && res.data.length > 0) {
            setVoices(res.data);
            // Default to first voice if none selected
            if (!selectedVoice) {
              setSelectedVoice(res.data[0].id);
              setSelectedVoiceName(res.data[0].name);
            }
          }
        })
        .catch(err => console.error('Failed to load voices:', err));
    }
  }, [selectedAudioProvider]);

  useEffect(() => {
    loadProjectData();
  }, [projectId]);

  // Polling for live status when running
  useEffect(() => {
    const isRunning = project && [
      'generating_audio', 'generating_video', 'syncing', 'merging'
    ].includes(project.workflow_status);

    if (isRunning) {
      pollIntervalRef.current = setInterval(async () => {
        try {
          const statusRes = await projectsApi.status(projectId);
          if (statusRes.success) {
            setStatus(statusRes.data);
          }
          const projRes = await projectsApi.get(projectId);
          if (projRes.success) {
            setProject(projRes.data);
          }
        } catch (e) {
          console.error('Polling status failed', e);
        }
      }, 2000);
    } else {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    }

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [project?.workflow_status, projectId]);

  // Handle Estimate
  const handleEstimate = async () => {
    setActionLoading(true);
    try {
      const res = await projectsApi.estimate(projectId);
      if (res.success) setEstimate(res.data);
    } catch (err) {
      setError('Estimation failed');
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Save Configuration & Run Precheck
  const handlePrecheck = async () => {
    setActionLoading(true);
    setError(null);
    try {
      // Save config first
      await projectsApi.configure(projectId, {
        audio_provider_id: selectedAudioProvider,
        video_provider_id: selectedVideoProvider,
        voice_id: selectedVoice,
        voice_name: selectedVoiceName,
        sync_strategy: syncStrategy,
      });

      // Run precheck
      const res = await projectsApi.precheck(projectId);
      if (res.success) {
        setPreflight(res.data);
        loadProjectData();
      }
    } catch (err) {
      setError('Precheck failed');
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Start Workflow
  const handleRun = async () => {
    setActionLoading(true);
    try {
      const res = await projectsApi.run(projectId);
      if (res.success) {
        loadProjectData();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start workflow');
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Resume Workflow
  const handleResume = async () => {
    setActionLoading(true);
    try {
      const res = await projectsApi.resume(projectId);
      if (res.success) {
        loadProjectData();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to resume workflow');
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Cancel Workflow
  const handleCancel = async () => {
    try {
      await projectsApi.cancel(projectId);
      loadProjectData();
    } catch (err) {
      setError('Failed to cancel workflow');
    }
  };

  if (loading) return <div className="card">Loading project...</div>;
  if (!project) return <div className="card">Project not found</div>;

  const isRunning = [
    'generating_audio', 'generating_video', 'syncing', 'merging'
  ].includes(project.workflow_status);

  return (
    <div>
      <div className="page-header">
        <div>
          <button
            className="btn btn-secondary"
            onClick={onBack}
            style={{ marginBottom: '0.5rem', padding: '0.25rem 0.75rem', fontSize: '0.8rem' }}
          >
            ← Back to Dashboard
          </button>
          <h1 className="page-title">{project.title}</h1>
          <p className="page-subtitle">
            ID: <code>{project.id}</code> | Mode: {project.workflow_mode === 'audio_video' ? 'Audio + Video' : 'Audio Only'}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {project.workflow_status === 'parsed' && (
            <button className="btn btn-primary" onClick={handleEstimate} disabled={actionLoading}>
              Estimate Resources
            </button>
          )}

          {project.workflow_status === 'estimated' && (
            <button className="btn btn-primary" onClick={handlePrecheck} disabled={actionLoading}>
              Save Config & Run Preflight →
            </button>
          )}

          {project.workflow_status === 'prechecked' && (
            <button className="btn btn-primary" onClick={handleRun} disabled={actionLoading}>
              ▶️ Start Workflow
            </button>
          )}

          {['failed', 'interrupted'].includes(project.workflow_status) && (
            <button className="btn btn-primary" onClick={handleResume} disabled={actionLoading}>
              🔄 Resume Workflow
            </button>
          )}

          {isRunning && (
            <button className="btn btn-danger" onClick={handleCancel}>
              ⏹️ Cancel Workflow
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="banner banner-danger">
          <span>❌ {error}</span>
        </div>
      )}

      {project.error_message && (
        <div className="banner banner-danger">
          <strong>Workflow Failure:</strong> {project.error_message}
        </div>
      )}

      {/* Progress View when Running or Completed */}
      {(isRunning || project.workflow_status === 'completed' || status) && (
        <div className="card">
          <div className="card-title">
            <span>Workflow Execution Progress</span>
            <span className="badge badge-info">{project.workflow_status}</span>
          </div>

          <div className="progress-container">
            <div className="progress-label">
              <span>Overall Status</span>
              <span>{status ? `${status.audio_completed}/${status.total_segments} Segments` : ''}</span>
            </div>
            <div className="progress-bar-bg">
              <div
                className={`progress-bar-fill ${project.workflow_status === 'completed' ? 'success' : ''}`}
                style={{
                  width: `${status ? (status.audio_completed / Math.max(status.total_segments, 1)) * 100 : (project.workflow_status === 'completed' ? 100 : 10)}%`
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Provider & Voice Configuration Cards */}
      <div className="grid-2">
        {/* Audio Provider Card */}
        <div className="card">
          <div className="card-title">
            <span>🎙️ Audio Provider (TTS)</span>
            <span className="badge badge-success">Free Tier</span>
          </div>

          <div className="form-group">
            <label className="form-label">Provider</label>
            <select
              className="form-select"
              value={selectedAudioProvider}
              onChange={(e) => setSelectedAudioProvider(e.target.value)}
              disabled={isRunning}
            >
              {providers.audio.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} {p.free_tier ? '(Free Tier ✅)' : ''}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Voice Selection</label>
            <select
              className="form-select"
              value={selectedVoice}
              onChange={(e) => {
                setSelectedVoice(e.target.value);
                const v = voices.find(x => x.id === e.target.value);
                if (v) setSelectedVoiceName(v.name);
              }}
              disabled={isRunning || voices.length === 0}
            >
              {voices.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} ({v.language})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Video Provider Card */}
        {project.workflow_mode === 'audio_video' && (
          <div className="card">
            <div className="card-title">
              <span>🎥 Video Provider (Text-to-Video)</span>
              <span className="badge badge-info">8s Clips</span>
            </div>

            <div className="form-group">
              <label className="form-label">Provider</label>
              <select
                className="form-select"
                value={selectedVideoProvider}
                onChange={(e) => setSelectedVideoProvider(e.target.value)}
                disabled={isRunning}
              >
                <option value="">-- Select Video Provider --</option>
                {providers.video.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Audio/Video Sync Strategy</label>
              <select
                className="form-select"
                value={syncStrategy}
                onChange={(e) => setSyncStrategy(e.target.value)}
                disabled={isRunning}
              >
                <option value="trim_video">Trim Video (Cut video to match audio length)</option>
                <option value="loop_video">Loop Video (Repeat video to fill audio length)</option>
                <option value="pad_video">Pad Video (Add black frames at the end)</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Preflight Checklist Results */}
      {preflight && (
        <div className="card">
          <div className="card-title">
            <span>📋 Preflight Check Results</span>
            <span className={`badge ${preflight.passed ? 'badge-success' : 'badge-danger'}`}>
              {preflight.passed ? '✅ Passed All Checks' : '❌ Checks Failed'}
            </span>
          </div>

          <table className="table">
            <thead>
              <tr>
                <th>Check</th>
                <th>Description</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {preflight.checks.map((c, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: '600' }}><code>{c.name}</code></td>
                  <td>{c.description}</td>
                  <td>
                    {c.passed ? (
                      <span className="badge badge-success">Passed</span>
                    ) : (
                      <span className="badge badge-danger">Failed: {c.error_message}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Segment List */}
      <div className="card">
        <div className="card-title">
          <span>Parsed Script Segments ({project.segments.length})</span>
        </div>

        <table className="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Text Preview</th>
              <th>Chars</th>
              <th>Audio Status</th>
              <th>Video Status</th>
              <th>Duration</th>
            </tr>
          </thead>
          <tbody>
            {project.segments.map((seg) => (
              <tr key={seg.number}>
                <td style={{ fontWeight: '700' }}>{seg.number}</td>
                <td style={{ maxWidth: '400px' }}>{seg.text_preview}</td>
                <td>{seg.char_count}</td>
                <td>
                  <span className={`badge ${seg.audio_status === 'completed' ? 'badge-success' : (seg.audio_status === 'failed' ? 'badge-danger' : 'badge-neutral')}`}>
                    {seg.audio_status}
                  </span>
                </td>
                <td>
                  <span className={`badge ${seg.video_status === 'completed' ? 'badge-success' : (seg.video_status === 'failed' ? 'badge-danger' : 'badge-neutral')}`}>
                    {seg.video_status}
                  </span>
                </td>
                <td>
                  {seg.audio_duration ? `${seg.audio_duration}s` : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
