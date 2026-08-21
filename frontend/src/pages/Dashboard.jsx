import React, { useState, useEffect } from 'react';
import { projectsApi, systemApi } from '../api';

export default function Dashboard({ onSelectProject, onCreateNew }) {
  const [projects, setProjects] = useState([]);
  const [interrupted, setInterrupted] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [projRes, intRes] = await Promise.all([
        projectsApi.list(),
        systemApi.interrupted(),
      ]);
      if (projRes.success) setProjects(projRes.data);
      if (intRes.success) setInterrupted(intRes.data);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDelete = async (id, title, e) => {
    e.stopPropagation();
    if (window.confirm(`Are you sure you want to delete "${title}"?`)) {
      try {
        await projectsApi.delete(id);
        loadData();
      } catch (err) {
        alert('Failed to delete project');
      }
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed': return <span className="badge badge-success">Completed</span>;
      case 'failed': return <span className="badge badge-danger">Failed</span>;
      case 'interrupted': return <span className="badge badge-warning">Interrupted</span>;
      case 'generating_audio':
      case 'generating_video':
      case 'syncing':
      case 'merging': return <span className="badge badge-info">Running ({status})</span>;
      default: return <span className="badge badge-neutral">{status}</span>;
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Local-first Script-to-Video Production Pipeline</p>
        </div>
        <button className="btn btn-primary" onClick={onCreateNew}>
          + Create Project
        </button>
      </div>

      {/* Interrupted Projects Warning Banner */}
      {interrupted.length > 0 && (
        <div className="banner banner-warning">
          <div>
            <strong>⚠️ Interrupted Projects Detected!</strong>
            <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>
              The following project(s) were stopped mid-workflow. You can resume without losing completed segments.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {interrupted.map(p => (
              <button
                key={p.id}
                className="btn btn-secondary"
                onClick={() => onSelectProject(p.id)}
              >
                Resume "{p.title}"
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Projects List */}
      <div className="card">
        <div className="card-title">
          <span>Recent Projects ({projects.length})</span>
        </div>

        {loading ? (
          <p style={{ color: 'var(--text-secondary)' }}>Loading projects...</p>
        ) : projects.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              No projects created yet. Start by entering a script!
            </p>
            <button className="btn btn-primary" onClick={onCreateNew}>
              Create First Project
            </button>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Mode</th>
                <th>Segments</th>
                <th>Status</th>
                <th>Created</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p) => (
                <tr
                  key={p.id}
                  onClick={() => onSelectProject(p.id)}
                  style={{ cursor: 'pointer' }}
                >
                  <td style={{ fontWeight: '600' }}>{p.title}</td>
                  <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    {p.workflow_mode === 'audio_video' ? 'Audio + Video' : 'Audio Only'}
                  </td>
                  <td>{p.segment_count}</td>
                  <td>{getStatusBadge(p.workflow_status)}</td>
                  <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    {new Date(p.created_at).toLocaleDateString()}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem', marginRight: '0.5rem' }}
                      onClick={(e) => { e.stopPropagation(); onSelectProject(p.id); }}
                    >
                      Open
                    </button>
                    <button
                      className="btn btn-danger"
                      style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem' }}
                      onClick={(e) => handleDelete(p.id, p.title, e)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
