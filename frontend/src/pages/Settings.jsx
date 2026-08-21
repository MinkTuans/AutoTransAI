import React, { useState, useEffect } from 'react';
import { providersApi } from '../api';

export default function Settings() {
  const [providers, setProviders] = useState({ audio: [], video: [], llm: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    providersApi.list()
      .then(res => {
        if (res.success) setProviders(res.data);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Provider & System Settings</h1>
          <p className="page-subtitle">Configure local AI provider integration keys</p>
        </div>
      </div>

      <div className="banner banner-warning">
        <span>🔒 <strong>API Key Security:</strong> All API keys are stored strictly on your local machine in the <code>.env</code> file. They are never sent to external servers except directly to provider APIs.</span>
      </div>

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
                </tr>
              </thead>
              <tbody>
                {providers.audio.map(p => (
                  <tr key={p.id}>
                    <td style={{ fontWeight: '600' }}>{p.name}</td>
                    <td>{p.free_tier ? 'Free Tier / Open' : 'Paid'}</td>
                    <td>{p.api_key_set ? 'No key required' : 'Requires key'}</td>
                    <td>
                      <span className="badge badge-success">Configured ✅</span>
                    </td>
                  </tr>
                ))}
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
                </tr>
              </thead>
              <tbody>
                {providers.video.map(p => (
                  <tr key={p.id}>
                    <td style={{ fontWeight: '600' }}>{p.name}</td>
                    <td>{p.free_tier ? 'Free Tier' : 'Pay-as-you-go'}</td>
                    <td>Yes</td>
                    <td>
                      <span className="badge badge-warning">Configure in .env</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
