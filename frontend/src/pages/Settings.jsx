import React, { useState, useEffect } from 'react';
import { providersApi } from '../api';

export default function Settings() {
  const [providers, setProviders] = useState({ audio: [], video: [], llm: [] });
  const [loading, setLoading] = useState(true);
  const [editingProvider, setEditingProvider] = useState(null);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  // Multi-key state
  const [selectedVideoProvider, setSelectedVideoProvider] = useState('kling');
  const [keysList, setKeysList] = useState([]);
  const [keysLoading, setKeysLoading] = useState(false);
  const [showAddKeyModal, setShowAddKeyModal] = useState(false);
  const [newKeyInput, setNewKeyInput] = useState('');
  const [newKeyPriority, setNewKeyPriority] = useState(1);
  const [keyActionMsg, setKeyActionMsg] = useState(null);

  const fetchProviders = () => {
    providersApi.list()
      .then(res => {
        if (res.success) setProviders(res.data);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  const fetchKeys = (providerId) => {
    setKeysLoading(true);
    providersApi.listKeys(providerId)
      .then(res => {
        if (res.success) {
          setKeysList(res.data);
        }
      })
      .catch(err => console.error('Failed to fetch keys:', err))
      .finally(() => setKeysLoading(false));
  };

  useEffect(() => {
    fetchProviders();
    fetchKeys(selectedVideoProvider);
  }, [selectedVideoProvider]);

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
        fetchKeys(selectedVideoProvider);
      } else {
        setMessage({ type: 'danger', text: res.error?.message || 'Failed to configure API key' });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: err.response?.data?.detail || 'Failed to save API key' });
    } finally {
      setSaving(false);
    }
  };

  // Multi-key Handlers
  const handleAddMultiKey = async (e) => {
    e.preventDefault();
    if (!newKeyInput.trim()) return;

    setSaving(true);
    setKeyActionMsg(null);
    try {
      const res = await providersApi.addKey(selectedVideoProvider, newKeyInput.trim(), parseInt(newKeyPriority, 10));
      if (res.success) {
        setKeyActionMsg({ type: 'success', text: 'New API Key added successfully!' });
        setNewKeyInput('');
        setShowAddKeyModal(false);
        fetchKeys(selectedVideoProvider);
      } else {
        setKeyActionMsg({ type: 'danger', text: res.error?.message || 'Failed to add key' });
      }
    } catch (err) {
      setKeyActionMsg({ type: 'danger', text: err.response?.data?.detail || 'Failed to add key' });
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteKey = async (keyId) => {
    if (!window.confirm('Are you sure you want to remove this API key?')) return;
    try {
      await providersApi.deleteKey(selectedVideoProvider, keyId);
      setKeyActionMsg({ type: 'success', text: 'API Key removed' });
      fetchKeys(selectedVideoProvider);
    } catch (err) {
      setKeyActionMsg({ type: 'danger', text: 'Failed to delete key' });
    }
  };

  const handleToggleKeyStatus = async (keyEntry) => {
    const newStatus = keyEntry.status === 'disabled' ? 'ready' : 'disabled';
    try {
      await providersApi.updateKey(selectedVideoProvider, keyEntry.key_id, { status: newStatus });
      fetchKeys(selectedVideoProvider);
    } catch (err) {
      setKeyActionMsg({ type: 'danger', text: 'Failed to update key status' });
    }
  };

  const handlePriorityChange = async (keyId, newPriority) => {
    try {
      await providersApi.updateKey(selectedVideoProvider, keyId, { priority: parseInt(newPriority, 10) });
      fetchKeys(selectedVideoProvider);
    } catch (err) {
      setKeyActionMsg({ type: 'danger', text: 'Failed to update priority' });
    }
  };

  const handleTestKey = async (keyId) => {
    setKeyActionMsg({ type: 'info', text: 'Testing key connection...' });
    try {
      const res = await providersApi.testKey(selectedVideoProvider, keyId);
      if (res.success && res.data.valid) {
        setKeyActionMsg({ type: 'success', text: `Key test passed: ${res.data.message}` });
      } else {
        setKeyActionMsg({ type: 'danger', text: `Key test failed: ${res.data?.message || 'Invalid'}` });
      }
      fetchKeys(selectedVideoProvider);
    } catch (err) {
      setKeyActionMsg({ type: 'danger', text: 'Key test call failed' });
    }
  };

  const handleCheckQuota = async (keyId) => {
    setKeyActionMsg({ type: 'info', text: 'Fetching quota details...' });
    try {
      const res = await providersApi.checkQuota(selectedVideoProvider, keyId);
      if (res.success) {
        setKeyActionMsg({ type: 'info', text: `Quota info: ${res.data.status || 'Updated'}` });
        fetchKeys(selectedVideoProvider);
      }
    } catch (err) {
      setKeyActionMsg({ type: 'danger', text: 'Failed to fetch quota' });
    }
  };

  const renderStatusBadge = (k) => {
    switch (k.status) {
      case 'active':
        return <span className="badge badge-success">● Active</span>;
      case 'ready':
        return <span className="badge badge-info">● Ready</span>;
      case 'rate_limited':
        return (
          <span className="badge badge-warning">
            ● Rate Limited ({k.retry_after_seconds ? `Retry after ${k.retry_after_seconds}s` : 'Cooldown'})
          </span>
        );
      case 'exhausted':
        return <span className="badge badge-danger">● Exhausted / No Credit</span>;
      case 'invalid':
        return <span className="badge badge-danger">● Invalid API Key</span>;
      case 'disabled':
        return <span className="badge badge-neutral">● Disabled</span>;
      default:
        return <span className="badge badge-neutral">{k.status}</span>;
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
          <h1 className="page-title">Provider & API Key Management</h1>
          <p className="page-subtitle">Configure multi-key failover rotation and provider settings</p>
        </div>
        <button className="btn btn-secondary" onClick={() => { fetchProviders(); fetchKeys(selectedVideoProvider); }}>
          🔄 Refresh Status
        </button>
      </div>

      <div className="banner banner-warning">
        <span>🔒 <strong>API Key Security & Failover:</strong> API keys are stored strictly locally on your machine in <code>data/api_keys.json</code> and <code>.env</code>. Multiple keys per provider are automatically rotated upon rate limits or credit exhaustion.</span>
      </div>

      {message && (
        <div className={`banner banner-${message.type}`}>
          <span>{message.type === 'success' ? '✅' : '❌'} {message.text}</span>
        </div>
      )}

      {/* MULTI-KEY MANAGEMENT DASHBOARD FOR VIDEO GENERATION */}
      <div className="card" style={{ border: '1px solid var(--accent-primary)', backgroundColor: 'rgba(99, 102, 241, 0.03)' }}>
        <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <span style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>🔑 Video Generation API Keys Dashboard</span>
            <span className="badge badge-info" style={{ marginLeft: '0.75rem' }}>Auto-Failover Enabled</span>
          </div>
          <button
            className="btn btn-primary"
            style={{ fontSize: '0.85rem', padding: '0.4rem 0.8rem' }}
            onClick={() => setShowAddKeyModal(true)}
          >
            ➕ Add API Key
          </button>
        </div>

        {/* Provider Selector Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', margin: '1rem 0', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
          <button
            className={`btn ${selectedVideoProvider === 'kling' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setSelectedVideoProvider('kling')}
            style={{ fontSize: '0.9rem' }}
          >
            🎬 Kling AI
          </button>
          <button
            className={`btn ${selectedVideoProvider === 'fal' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setSelectedVideoProvider('fal')}
            style={{ fontSize: '0.9rem' }}
          >
            ⚡ fal.ai (Hunyuan / LTX-2)
          </button>
        </div>

        {keyActionMsg && (
          <div className={`banner banner-${keyActionMsg.type}`} style={{ margin: '0.5rem 0' }}>
            <span>{keyActionMsg.text}</span>
          </div>
        )}

        {/* Add Key Inline Form */}
        {showAddKeyModal && (
          <div className="card" style={{ backgroundColor: 'var(--bg-secondary)', marginBottom: '1rem', border: '1px dashed var(--accent-primary)' }}>
            <div className="card-title">
              <span>➕ Add New API Key for {selectedVideoProvider === 'kling' ? 'Kling AI' : 'fal.ai'}</span>
            </div>
            <form onSubmit={handleAddMultiKey}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 120px', gap: '0.75rem' }}>
                <div className="form-group">
                  <label className="form-label">API Key</label>
                  <input
                    type="password"
                    className="form-control"
                    placeholder="Paste API key string..."
                    value={newKeyInput}
                    onChange={(e) => setNewKeyInput(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Priority</label>
                  <input
                    type="number"
                    className="form-control"
                    value={newKeyPriority}
                    onChange={(e) => setNewKeyPriority(e.target.value)}
                    min="1"
                    max="10"
                    required
                  />
                </div>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddKeyModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Adding...' : 'Save Key'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Keys List Table */}
        {keysLoading ? (
          <p style={{ color: 'var(--text-secondary)' }}>Loading key pool...</p>
        ) : keysList.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)', padding: '1rem 0' }}>
            No API keys configured for {selectedVideoProvider.toUpperCase()}. Click "Add API Key" above or select <strong>Local AI & FFmpeg Generator</strong> in project settings for 100% free video generation.
          </p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Priority</th>
                <th>Masked Key</th>
                <th>Status</th>
                <th>Requests (Success / Failed)</th>
                <th>Quota / Balance</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {keysList.map((k) => (
                <tr key={k.key_id}>
                  <td>
                    <select
                      className="form-select"
                      style={{ width: '65px', padding: '0.15rem 0.4rem', fontSize: '0.85rem' }}
                      value={k.priority}
                      onChange={(e) => handlePriorityChange(k.key_id, e.target.value)}
                    >
                      {[1, 2, 3, 4, 5].map((p) => (
                        <option key={p} value={p}>#{p}</option>
                      ))}
                    </select>
                  </td>
                  <td style={{ fontWeight: '600', fontFamily: 'monospace' }}>{k.masked_key}</td>
                  <td>{renderStatusBadge(k)}</td>
                  <td>
                    {k.total_requests} reqs ({k.successful_requests} ✅ / {k.failed_requests} ❌)
                  </td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    {k.quota_info?.status || 'Unknown / Not available'}
                  </td>
                  <td style={{ textAlign: 'right', display: 'flex', gap: '0.3rem', justifyContent: 'flex-end' }}>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                      title="Test Key Validity"
                      onClick={() => handleTestKey(k.key_id)}
                    >
                      🧪 Test
                    </button>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                      title="Check Quota"
                      onClick={() => handleCheckQuota(k.key_id)}
                    >
                      📊 Quota
                    </button>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                      onClick={() => handleToggleKeyStatus(k)}
                    >
                      {k.status === 'disabled' ? '▶️ Enable' : '⏸️ Disable'}
                    </button>
                    <button
                      className="btn btn-danger"
                      style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                      onClick={() => handleDeleteKey(k.key_id)}
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Inline Modal Form for Standard Single Key Configuration */}
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
