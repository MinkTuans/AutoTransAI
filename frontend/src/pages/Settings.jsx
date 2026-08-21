import React, { useState, useEffect } from 'react';
import { providersApi } from '../api';

export default function Settings() {
  const [providers, setProviders] = useState({ audio: [], video: [], llm: [] });
  const [loading, setLoading] = useState(true);
  const [editingProvider, setEditingProvider] = useState(null);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  const fetchProviders = () => {
    providersApi.list()
      .then(res => {
        if (res.success) setProviders(res.data);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchProviders();
  }, []);

  const handleOpenConfig = (provider) => {
    setEditingProvider(provider);
    setApiKeyInput('');
    setMessage(null);
  };

  const handleSaveKey = async (e) => {
    e.preventDefault();
    if (!apiKeyInput.trim()) return;

    setSaving(true);
    setMessage(null);
    try {
      const res = await providersApi.configureKey(editingProvider.id, apiKeyInput.trim());
      if (res.success) {
        setMessage({ type: 'success', text: `API key for ${editingProvider.name} updated successfully!` });
        setEditingProvider(null);
        setApiKeyInput('');
        fetchProviders();
      } else {
        setMessage({ type: 'danger', text: res.error?.message || 'Failed to configure API key' });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: err.response?.data?.detail || 'Failed to save API key' });
    } finally {
      setSaving(false);
    }
  };

  const renderProviderRow = (p) => (
    <tr key={p.id}>
      <td style={{ fontWeight: '600' }}>{p.name}</td>
      <td>{p.free_tier ? 'Free Tier / Open' : 'Pay-as-you-go'}</td>
      <td>{p.api_key_set || !p.free_tier ? 'Requires Key' : 'No Key Needed'}</td>
      <td>
        {p.configured ? (
          <span className="badge badge-success">CONFIGURED ✅</span>
        ) : (
          <span className="badge badge-warning">API Key Missing</span>
        )}
      </td>
      <td style={{ textAlign: 'right' }}>
        {p.id !== 'edge_tts' && (
          <button
            className="btn btn-secondary"
            style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem' }}
            onClick={() => handleOpenConfig(p)}
          >
            ⚙️ Configure Key
          </button>
        )}
      </td>
    </tr>
  );

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Provider & System Settings</h1>
          <p className="page-subtitle">Configure local AI provider integration keys</p>
        </div>
        <button className="btn btn-secondary" onClick={fetchProviders}>
          🔄 Refresh Status
        </button>
      </div>

      <div className="banner banner-warning">
        <span>🔒 <strong>API Key Security:</strong> All API keys are stored strictly on your local machine in the <code>.env</code> file. They are never sent to third-party servers except directly to official provider APIs.</span>
      </div>

      {message && (
        <div className={`banner banner-${message.type}`}>
          <span>{message.type === 'success' ? '✅' : '❌'} {message.text}</span>
        </div>
      )}

      {/* Inline Modal Form for Editing Key */}
      {editingProvider && (
        <div className="card" style={{ border: '1px solid var(--accent-primary)', backgroundColor: 'var(--bg-secondary)' }}>
          <div className="card-title">
            <span>⚙️ Configure API Key for <strong>{editingProvider.name}</strong></span>
            <button
              className="btn btn-secondary"
              style={{ padding: '0.2rem 0.5rem', fontSize: '0.8rem' }}
              onClick={() => setEditingProvider(null)}
            >
              ✕ Cancel
            </button>
          </div>
          <form onSubmit={handleSaveKey}>
            <div className="form-group">
              <label className="form-label">Enter API Key</label>
              <input
                type="password"
                className="form-control"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder={`Paste your ${editingProvider.name} API Key here...`}
                required
                autoFocus
              />
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setEditingProvider(null)}
              >
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? 'Validating & Saving...' : 'Save Key to .env'}
              </button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <p style={{ color: 'var(--text-secondary)' }}>Loading settings...</p>
      ) : (
        <div>
          {/* Audio Providers */}
          <div className="card">
            <div className="card-title">
              <span>🎙️ Text-to-Speech (Audio) Providers</span>
            </div>

            <table className="table">
              <thead>
                <tr>
                  <th>Provider</th>
                  <th>Type</th>
                  <th>API Key Required</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {providers.audio.map(renderProviderRow)}
              </tbody>
            </table>
          </div>

          {/* Video Providers */}
          <div className="card">
            <div className="card-title">
              <span>🎥 Text-to-Video Providers</span>
            </div>

            <table className="table">
              <thead>
                <tr>
                  <th>Provider</th>
                  <th>Type</th>
                  <th>API Key Required</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {providers.video.map(renderProviderRow)}
              </tbody>
            </table>
          </div>

          {/* LLM Providers */}
          <div className="card">
            <div className="card-title">
              <span>🤖 Script & LLM Providers</span>
            </div>

            <table className="table">
              <thead>
                <tr>
                  <th>Provider</th>
                  <th>Type</th>
                  <th>API Key Required</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {providers.llm.map(renderProviderRow)}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
