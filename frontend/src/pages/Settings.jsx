import React, { useState, useEffect } from 'react';
import { providersApi, settingsApi, systemApi, tiktokApi, youtubeApi } from '../api';
import { LoadingSpinner, ButtonSpinner, LoadingOverlay, SkeletonLoader } from '../components/LoadingSpinner';
import ModelCatalog from '../components/settings/ModelCatalog';
import FunctionRouting from '../components/settings/FunctionRouting';


export default function Settings() {
  const [activeTab, setActiveTab] = useState('providers');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  // 1. Providers State
  const [providers, setProviders] = useState({ audio: [], video: [], llm: [] });
  const [selectedProviderForKeys, setSelectedProviderForKeys] = useState('gemini');
  const [keysList, setKeysList] = useState([]);
  const [keysLoading, setKeysLoading] = useState(false);
  const [showAddKeyModal, setShowAddKeyModal] = useState(false);
  const [newKeyInput, setNewKeyInput] = useState('');
  const [newKeyPriority, setNewKeyPriority] = useState(1);
  const [modalError, setModalError] = useState(null);

  // Custom Provider Modal State
  const [showAddProviderModal, setShowAddProviderModal] = useState(false);
  const [customProviderData, setCustomProviderData] = useState({
    id: '',
    name: '',
    provider_type: 'llm',
    website_url: '',
    doc_url: '',
    base_url: '',
    capabilities: ['LLM'],
    api_key: '',
  });

  // 4. Social Accounts State
  const [socialAccounts, setSocialAccounts] = useState([]);
  const [showAddSocialModal, setShowAddSocialModal] = useState(false);
  const [newSocialData, setNewSocialData] = useState({
    platform: 'youtube',
    account_name: '',
    channel_id: '',
    channel_name: '',
    priority: 1,
  });

  // 5. System Settings State (Storage, Processing, Workflow Defaults)
  const [systemSettings, setSystemSettings] = useState({
    storage_provider: 'local',
    r2_account_id: '',
    r2_access_key_id: '',
    r2_secret_access_key: '',
    r2_bucket_name: 'workflowvdai',
    r2_endpoint_url: '',
    r2_public_domain: '',
    max_concurrency: '2',
    max_retries: '3',
    retry_backoff: '2.0',
    video_target_duration: '8',
    video_output_resolution: '1080p',
    audio_format: 'wav',
    audio_sample_rate: '24000',
    sync_strategy: 'trim_video',
    sync_tolerance_seconds: '0.5',
    default_source_language: 'auto',
    default_target_language: 'vi',
    default_tts_voice: 'vi-VN-HoaiMyNeural',
    default_video_provider: 'kling',
    social_account_strategy: 'priority',
  });

  // Storage Test State
  const [storageTestStatus, setStorageTestStatus] = useState(null);
  const [storageTesting, setStorageTesting] = useState(false);

  // Data Loading Handlers
  const fetchProviders = () => {
    return providersApi.list()
      .then(res => {
        if (res.success) setProviders(res.data);
      })
      .catch(err => console.error('Failed fetching providers:', err));
  };

  const fetchKeys = (providerId) => {
    setKeysLoading(true);
    return providersApi.listKeys(providerId)
      .then(res => {
        if (res.success) setKeysList(res.data);
      })
      .catch(err => console.error('Failed fetching keys:', err))
      .finally(() => setKeysLoading(false));
  };

  const fetchSocialAccounts = async () => {
    try {
      const [settingsRes, ytAccounts, ttAccounts] = await Promise.allSettled([
        settingsApi.getSocialAccounts(),
        youtubeApi.listAccounts(),
        tiktokApi.listAccounts(),
      ]);

      let accounts = [];
      if (settingsRes.status === 'fulfilled' && settingsRes.value?.success) {
        accounts = [...(settingsRes.value.data || [])];
      }
      if (ytAccounts.status === 'fulfilled' && Array.isArray(ytAccounts.value)) {
        const ytList = ytAccounts.value.map(acc => ({
          id: acc.id,
          platform: 'youtube',
          account_name: acc.channel_name,
          channel_id: acc.channel_id,
          status: 'CONNECTED (OAuth 2.0)',
          priority: 1,
          is_oauth: true,
        }));
        accounts = [...ytList, ...accounts.filter(a => a.platform !== 'youtube')];
      }
      if (ttAccounts.status === 'fulfilled' && Array.isArray(ttAccounts.value)) {
        const ttList = ttAccounts.value.map(acc => ({
          id: acc.id,
          platform: 'tiktok',
          account_name: acc.display_name || acc.channel_name,
          channel_id: acc.open_id || acc.channel_id,
          status: 'CONNECTED (OAuth 2.0)',
          priority: 1,
          is_oauth: true,
        }));
        accounts = [...ttList, ...accounts.filter(a => a.platform !== 'tiktok')];
      }
      setSocialAccounts(accounts);
      return accounts;
    } catch (err) {
      console.error('Failed fetching social accounts:', err);
      return [];
    }
  };

  const openOAuthInChrome = async (authUrl) => {
    const res = await systemApi.openBrowser(authUrl);
    if (!res?.success) {
      throw new Error(res?.detail || 'Không mở được Google Chrome');
    }
  };

  const pollForNewOauthAccount = async (platform, previousIds) => {
    const started = Date.now();
    while (Date.now() - started < 180000) {
      const list = await fetchSocialAccounts();
      const found = (list || []).some(acc => acc.platform === platform && acc.is_oauth && !previousIds.has(acc.id));
      if (found) {
        setMessage({ type: 'success', text: `Đã kết nối ${platform === 'tiktok' ? 'TikTok' : 'YouTube'}. Có thể đóng tab Chrome.` });
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    return false;
  };

  const handleConnectOAuth = async (platform) => {
    const previousIds = new Set(socialAccounts.filter(a => a.platform === platform && a.is_oauth).map(a => a.id));
    try {
      const res = platform === 'tiktok'
        ? await tiktokApi.getAuthUrl()
        : await youtubeApi.getAuthUrl();
      if (!res?.auth_url) {
        alert(platform === 'tiktok'
          ? '❌ Không thể khởi tạo TikTok OAuth. Kiểm tra TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET trong .env'
          : '❌ Không thể khởi tạo kết nối Google OAuth. Vui lòng kiểm tra lại YOUTUBE_CLIENT_ID trong file .env');
        return;
      }
      await openOAuthInChrome(res.auth_url);
      setShowAddSocialModal(false);
      setMessage({
        type: 'info',
        text: `Đã mở tab mới trên Google Chrome. Đăng nhập ${platform === 'tiktok' ? 'TikTok' : 'Google/YouTube'} xong rồi quay lại app này — không đóng cửa sổ AutoTransAI.`,
      });
      pollForNewOauthAccount(platform, previousIds);
    } catch (err) {
      alert('❌ Lỗi mở Chrome cho OAuth: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleConnectYouTubeOAuth = () => handleConnectOAuth('youtube');
  const handleConnectTikTokOAuth = () => handleConnectOAuth('tiktok');

  const handleDeleteSocialAccount = async (accId, isOAuth, platform) => {
    if (!window.confirm('Bạn có chắc chắn muốn ngắt kết nối kênh này?')) return;
    try {
      if (isOAuth && platform === 'tiktok') {
        await tiktokApi.disconnectAccount(accId);
      } else if (isOAuth) {
        await youtubeApi.disconnectAccount(accId);
      } else {
        await settingsApi.deleteSocialAccount(accId);
      }
      await fetchSocialAccounts();
    } catch (err) {
      alert('❌ Lỗi ngắt kết nối kênh: ' + (err.response?.data?.detail || err.message));
    }
  };

  const fetchSystemSettings = () => {
    return settingsApi.getSettings()
      .then(res => {
        if (res.success) {
          setSystemSettings(prev => ({ ...prev, ...res.data }));
        }
      })
      .catch(err => console.error('Failed fetching system settings:', err));
  };

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchProviders(),
      fetchSocialAccounts(),
      fetchSystemSettings(),
    ]).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const onFocus = () => { fetchSocialAccounts(); };
    window.addEventListener('focus', onFocus);
    return () => window.removeEventListener('focus', onFocus);
  }, []);

  useEffect(() => {
    fetchKeys(selectedProviderForKeys);
  }, [selectedProviderForKeys]);

  // Handler: Add Multi-Key
  const handleAddKey = async (e) => {
    if (e) e.preventDefault();
    const cleanKey = newKeyInput.trim();
    if (!cleanKey) {
      setModalError('Vui lòng nhập API Key trước khi lưu!');
      return;
    }

    setSaving(true);
    setMessage(null);
    setModalError(null);
    try {
      const prio = parseInt(newKeyPriority, 10) || 1;
      const res = await providersApi.addKey(selectedProviderForKeys, cleanKey, prio);
      if (res.success) {
        setMessage({ type: 'success', text: `Đã thêm API Key cho ${selectedProviderForKeys.toUpperCase()} thành công!` });
        setNewKeyInput('');
        setModalError(null);
        setShowAddKeyModal(false);
        fetchKeys(selectedProviderForKeys);
        fetchProviders();
      } else {
        setModalError(res.error?.message || res.detail || 'Không thể thêm API Key');
      }
    } catch (err) {
      console.error('Error adding API Key:', err);
      const detailMsg = err.response?.data?.detail || err.response?.data?.message || err.message || 'Lỗi kết nối khi thêm API Key';
      setModalError(detailMsg);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteKey = async (keyId) => {
    if (!window.confirm('Are you sure you want to delete this API key?')) return;
    try {
      await providersApi.deleteKey(selectedProviderForKeys, keyId);
      setMessage({ type: 'success', text: 'API key deleted' });
      fetchKeys(selectedProviderForKeys);
      fetchProviders();
    } catch (err) {
      setMessage({ type: 'danger', text: 'Failed to delete API key' });
    }
  };

  const handleToggleKeyStatus = async (keyEntry) => {
    const newStatus = keyEntry.status === 'disabled' ? 'ready' : 'disabled';
    try {
      await providersApi.updateKey(selectedProviderForKeys, keyEntry.key_id, { status: newStatus });
      fetchKeys(selectedProviderForKeys);
    } catch (err) {
      setMessage({ type: 'danger', text: 'Failed to update key status' });
    }
  };

  const handleTestKey = async (keyId) => {
    setMessage({ type: 'info', text: 'Testing API key connection...' });
    try {
      const res = await providersApi.testKey(selectedProviderForKeys, keyId);
      if (res.success && res.data.valid) {
        setMessage({ type: 'success', text: `Key test passed: ${res.data.message}` });
      } else {
        setMessage({ type: 'danger', text: `Key test failed: ${res.data?.message || 'Invalid API Key'}` });
      }
      fetchKeys(selectedProviderForKeys);
    } catch (err) {
      setMessage({ type: 'danger', text: 'Key test call failed' });
    }
  };

  // Handler: Add Custom Provider
  const handleAddCustomProvider = async (e) => {
    e.preventDefault();
    if (!customProviderData.id || !customProviderData.name) return;

    setSaving(true);
    try {
      const res = await providersApi.addCustomProvider(customProviderData);
      if (res.success) {
        setMessage({ type: 'success', text: res.message || 'Custom provider added successfully!' });
        setShowAddProviderModal(false);
        setCustomProviderData({
          id: '',
          name: '',
          provider_type: 'llm',
          website_url: '',
          doc_url: '',
          base_url: '',
          capabilities: ['LLM'],
          api_key: '',
        });
        fetchProviders();
      }
    } catch (err) {
      setMessage({ type: 'danger', text: err.response?.data?.detail || 'Failed to add custom provider' });
    } finally {
      setSaving(false);
    }
  };

  // Handler: Save System Settings
  const handleSaveSystemSettings = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await settingsApi.updateSettings(systemSettings);
      if (res.success) {
        setMessage({ type: 'success', text: 'System settings saved successfully!' });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Failed saving system settings' });
    } finally {
      setSaving(false);
    }
  };

  // Handler: Test Storage Connection
  const handleTestStorageConnection = async () => {
    setStorageTesting(true);
    setStorageTestStatus(null);
    try {
      const res = await settingsApi.testStorage(systemSettings);
      setStorageTestStatus(res);
    } catch (err) {
      setStorageTestStatus({ success: false, message: 'Storage connection request failed.' });
    } finally {
      setStorageTesting(false);
    }
  };

  // Handler: Add Social Account
  const handleAddSocialAccount = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await settingsApi.addSocialAccount(newSocialData);
      if (res.success) {
        setMessage({ type: 'success', text: 'Social account connected successfully' });
        setShowAddSocialModal(false);
        fetchSocialAccounts();
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Failed connecting social account' });
    } finally {
      setSaving(false);
    }
  };

  const renderStatusBadge = (k) => {
    switch (k.status) {
      case 'active':
        return <span className="badge badge-success">● Active</span>;
      case 'ready':
        return <span className="badge badge-info">● Ready</span>;
      case 'rate_limited':
        return <span className="badge badge-warning">● Rate Limited (Cooldown 60s)</span>;
      case 'exhausted':
        return <span className="badge badge-danger">● Exhausted / Out of balance</span>;
      case 'invalid':
        return <span className="badge badge-danger">● Invalid API Key</span>;
      case 'disabled':
        return <span className="badge badge-neutral">● Disabled</span>;
      default:
        return <span className="badge badge-neutral">{k.status}</span>;
    }
  };

  const closeAddKeyModalSafely = () => {
    if (newKeyInput.trim()) {
      if (window.confirm('⚠️ Bạn có API Key đang nhập chưa lưu! Bạn có chắc chắn muốn đóng và thoát không?')) {
        setNewKeyInput('');
        setModalError(null);
        setShowAddKeyModal(false);
      }
    } else {
      setModalError(null);
      setShowAddKeyModal(false);
    }
  };

  const closeAddProviderModalSafely = () => {
    const isDirty = customProviderData.id || customProviderData.name || customProviderData.base_url || customProviderData.api_key;
    if (isDirty) {
      if (window.confirm('⚠️ Bạn có thông tin Custom Provider đang nhập chưa lưu! Bạn có chắc chắn muốn đóng và thoát không?')) {
        setShowAddProviderModal(false);
      }
    } else {
      setShowAddProviderModal(false);
    }
  };

  const closeAddSocialModalSafely = () => {
    const isDirty = newSocialData.account_name.trim() || newSocialData.channel_id.trim();
    if (isDirty) {
      if (window.confirm('⚠️ Bạn có thông tin kênh mạng xã hội đang nhập chưa lưu! Bạn có chắc chắn muốn đóng và thoát không?')) {
        setShowAddSocialModal(false);
      }
    } else {
      setShowAddSocialModal(false);
    }
  };

  if (loading) {
    return (
      <div className="card" style={{ marginTop: '1rem' }}>
        <div className="card-body" style={{ padding: '2rem' }}>
          <LoadingSpinner size="lg" label="Đang tải Settings Studio & AI Management..." sublabel="Khởi tạo danh mục AI Models, Key Pool và cấu hình hạ tầng..." />
          <div style={{ marginTop: '1.5rem' }}>
            <SkeletonLoader type="table" rows={6} columns={5} />
          </div>
        </div>
      </div>
    );
  }


  return (
    <div className="page-shell" style={{ paddingBottom: '3rem' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Cài đặt</h1>
          <p className="page-subtitle">
            Nhà cung cấp AI, API key, model, kênh YouTube và hạ tầng lưu trữ.
          </p>
        </div>
      </div>

      {/* Global Alert Notification */}
      {message && (
        <div className={`alert alert-${message.type}`} style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
          <span>{message.text}</span>
          <button style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }} onClick={() => setMessage(null)}>✕</button>
        </div>
      )}

      <div className="tab-bar">
        {[
          { id: 'providers', label: 'AI & API' },
          { id: 'functions', label: 'Function' },
          { id: 'models', label: 'Models' },
          { id: 'social', label: 'Social' },
          { id: 'system', label: 'System' },
        ].map(tab => (
          <button
            key={tab.id}
            type="button"
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => { setActiveTab(tab.id); setMessage(null); }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: AI & API PROVIDERS */}
      {activeTab === 'providers' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem' }}>
          {/* Provider Overview Card */}
          <div className="card">
            <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '1.1rem' }}>AI Provider Catalog & Status</h3>
              <button className="btn btn-secondary" style={{ fontSize: '0.8rem' }} onClick={() => setShowAddProviderModal(true)}>
                + Add Custom Provider
              </button>
            </div>
            <div className="card-body">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                {[
                  { id: 'gemini', name: 'Google Gemini', type: 'LLM & STT', supported: true, caps: ['STT', 'LLM', 'TRANSLATION'] },
                  { id: 'openai', name: 'OpenAI', type: 'LLM & STT', supported: true, caps: ['STT', 'LLM', 'TRANSLATION'] },
                  { id: 'edge_tts', name: 'Edge TTS', type: 'Audio TTS', supported: true, caps: ['TTS'], free: true },
                  { id: 'google_cloud_tts', name: 'Google Cloud TTS', type: 'Audio TTS', supported: true, caps: ['TTS'] },
                  { id: 'elevenlabs', name: 'ElevenLabs', type: 'Audio TTS', supported: true, caps: ['TTS'] },
                  { id: 'kling', name: 'Kling AI', type: 'Video Generation', supported: true, caps: ['VIDEO_GENERATION'] },
                  { id: 'fal', name: 'fal.ai', type: 'Video & Image', supported: true, caps: ['VIDEO_GENERATION', 'IMAGE_GENERATION'] },
                ].map(p => (
                  <div
                    key={p.id}
                    className={`provider-tile ${selectedProviderForKeys === p.id ? 'is-selected' : ''}`}
                    onClick={() => setSelectedProviderForKeys(p.id)}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <strong style={{ fontSize: '1rem', color: '#f8fafc' }}>{p.name}</strong>
                      <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>{p.type}</span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
                      {p.caps.map(c => <span key={c} className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>{c}</span>)}
                      {p.free && <span className="badge badge-success" style={{ fontSize: '0.65rem' }}> miễn phí</span>}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', color: '#94a3b8', gap: '0.5rem' }}>
                      <span>Status: {p.free ? 'Ready' : 'Multi-Key Pool'}</span>
                      <div style={{ display: 'flex', gap: '0.3rem' }}>
                        {!p.free && (
                          <button
                            className="btn btn-primary"
                            style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedProviderForKeys(p.id);
                              setShowAddKeyModal(true);
                            }}
                          >
                            + Thêm Key
                          </button>
                        )}
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedProviderForKeys(p.id);
                            const elem = document.getElementById('key-pool-manager');
                            if (elem) elem.scrollIntoView({ behavior: 'smooth' });
                          }}
                        >
                          Quản lý →
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Multi-Key Pool Manager Card */}
          <div className="card" id="key-pool-manager">
            <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.1rem' }}>
                  🔑 Key Pool & Rotation Manager — <span style={{ color: '#3b82f6' }}>{selectedProviderForKeys.toUpperCase()}</span>
                </h3>
                <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>
                  Automatic failover & cooldown on 429/Rate Limit. Masked keys enforced (`AIza****XXXX`).
                </p>
              </div>
              {selectedProviderForKeys !== 'edge_tts' ? (
                <button className="btn btn-primary" style={{ fontSize: '0.8rem' }} onClick={() => setShowAddKeyModal(true)}>
                  + Add API Key to Pool
                </button>
              ) : (
                <span className="badge badge-success" style={{ fontSize: '0.75rem' }}>Miễn phí (Không dùng API Key)</span>
              )}
            </div>
            <div className="card-body">
              {selectedProviderForKeys === 'edge_tts' ? (
                <div style={{ color: '#94a3b8', fontStyle: 'italic', padding: '1rem 0' }}>
                  ℹ️ Edge TTS là dịch vụ TTS miễn phí tích hợp sẵn. Không cần cấu hình API key.
                </div>
              ) : keysLoading ? (
                <div style={{ padding: '1rem 0' }}>
                  <LoadingSpinner size="sm" label={`Đang tải Key Pool cho ${selectedProviderForKeys.toUpperCase()}...`} />
                  <SkeletonLoader type="table" rows={3} columns={6} />
                </div>
              ) : keysList.length === 0 ? (
                <div style={{ color: '#94a3b8', fontStyle: 'italic', padding: '1rem 0' }}>
                  Chưa có API key nào cho {selectedProviderForKeys.toUpperCase()}. Bấm nút "+ Add API Key to Pool" hoặc "+ Thêm Key" trên thẻ phía trên để nhập API key mới.
                </div>
              ) : (
                <table className="table" style={{ width: '100%', fontSize: '0.85rem' }}>
                  <thead>
                    <tr>
                      <th>Priority</th>
                      <th>Masked API Key</th>
                      <th>Status</th>
                      <th>Requests (Success/Fail)</th>
                      <th>Quota Info</th>
                      <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {keysList.map(k => (
                      <tr key={k.key_id}>
                        <td><span className="badge badge-info">P{k.priority}</span></td>
                        <td style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>{k.masked_key}</td>
                        <td>{renderStatusBadge(k)}</td>
                        <td>{k.successful_requests} / {k.failed_requests} ({k.total_requests} total)</td>
                        <td>{k.quota_info?.status || 'Active'}</td>
                        <td style={{ textAlign: 'right', verticalAlign: 'middle' }}>
                          <div style={{ display: 'inline-flex', gap: '0.3rem', justifyContent: 'flex-end', alignItems: 'center' }}>
                            <button className="btn btn-secondary" style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }} onClick={() => handleTestKey(k.key_id)}>
                              🧪 Test
                            </button>
                            <button className="btn btn-secondary" style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }} onClick={() => handleToggleKeyStatus(k)}>
                              {k.status === 'disabled' ? 'Enable' : 'Disable'}
                            </button>
                            <button className="btn btn-danger" style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }} onClick={() => handleDeleteKey(k.key_id)}>
                              🗑️
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: AI FUNCTION CONFIGURATION */}
      {activeTab === 'functions' && <FunctionRouting />}

      {/* TAB 3: AI MODELS CATALOG */}
      {activeTab === 'models' && <ModelCatalog />}

      {/* TAB 4: SOCIAL ACCOUNTS */}
      {activeTab === 'social' && (
        <div className="card">
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.1rem' }}>📱 Social Accounts Manager</h3>
              <p style={{ margin: 0, fontSize: '0.85rem', color: '#94a3b8' }}>
                Manage connected YouTube, TikTok, Facebook & Instagram publishing channels.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                className="btn btn-primary"
                style={{ fontSize: '0.8rem', background: 'linear-gradient(135deg, #ef4444, #dc2626)' }}
                onClick={handleConnectYouTubeOAuth}
                title="Mở tab Google Chrome để đăng nhập Google OAuth 2.0"
              >
                🔴 Kết Nối YouTube
              </button>
              <button
                className="btn btn-primary"
                style={{ fontSize: '0.8rem', background: 'linear-gradient(135deg, #111827, #000000)', color: '#fff' }}
                onClick={handleConnectTikTokOAuth}
                title="Mở tab Google Chrome để đăng nhập TikTok Login Kit"
              >
                ♪ Kết Nối TikTok
              </button>
              <button className="btn btn-secondary" style={{ fontSize: '0.8rem' }} onClick={() => setShowAddSocialModal(true)}>
                + Thêm Kênh Khác
              </button>
            </div>
          </div>
          <div className="card-body">
            {socialAccounts.length === 0 ? (
              <div style={{ color: '#94a3b8', fontStyle: 'italic' }}>
                Chưa có tài khoản nào được kết nối. Hãy ấn Kết Nối YouTube hoặc Kết Nối TikTok (mở tab Chrome, không mở trong app).
              </div>
            ) : (
              <table className="table" style={{ width: '100%', fontSize: '0.85rem' }}>
                <thead>
                  <tr>
                    <th>Platform</th>
                    <th>Account / Channel Name</th>
                    <th>Channel ID</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {socialAccounts.map(acc => (
                    <tr key={acc.id}>
                      <td style={{ textTransform: 'capitalize', fontWeight: 'bold' }}>{acc.platform}</td>
                      <td>{acc.channel_name || acc.account_name}</td>
                      <td style={{ fontFamily: 'monospace' }}>{acc.channel_id || 'N/A'}</td>
                      <td><span className="badge badge-success">● {acc.status}</span></td>
                      <td><span className="badge badge-info">P{acc.priority}</span></td>
                      <td style={{ textAlign: 'right' }}>
                        <button className="btn btn-danger" style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }} onClick={() => handleDeleteSocialAccount(acc.id, acc.is_oauth, acc.platform)}>
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* TAB 5: SYSTEM (storage + workflow defaults + diagnostics) */}
      {activeTab === 'system' && (
        <form onSubmit={handleSaveSystemSettings} style={{ display: 'grid', gap: '1rem' }}>
          <div className="card">
            <div className="card-header">
              <h3 style={{ margin: 0, fontSize: '1.1rem' }}>System</h3>
              <p style={{ margin: '0.35rem 0 0', fontSize: '0.85rem', color: '#94a3b8' }}>
                Storage local, giá trị mặc định khi tạo job, và kiểm tra backend.
              </p>
            </div>
            <div className="card-body">
              <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>Storage</label>
                <select
                  className="form-control"
                  value={systemSettings.storage_provider}
                  onChange={(e) => setSystemSettings({ ...systemSettings, storage_provider: e.target.value })}
                >
                  <option value="local">Local Disk (`storage/projects/{'{project_id}'}/...`)</option>
                </select>
                <p style={{ margin: '0.4rem 0 0', fontSize: '0.8rem', color: '#94a3b8' }}>
                  Media nằm trên ổ đĩa máy, CSDL MySQL (Laragon).
                </p>
              </div>

              {storageTestStatus && (
                <div className={`alert alert-${storageTestStatus.success ? 'success' : 'danger'}`} style={{ marginBottom: '1rem' }}>
                  {storageTestStatus.message}
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
                <div className="form-group">
                  <label>Default Source Language</label>
                  <input
                    type="text"
                    className="form-control"
                    value={systemSettings.default_source_language}
                    onChange={(e) => setSystemSettings({ ...systemSettings, default_source_language: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Default Target Language</label>
                  <input
                    type="text"
                    className="form-control"
                    value={systemSettings.default_target_language}
                    onChange={(e) => setSystemSettings({ ...systemSettings, default_target_language: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Default TTS Voice</label>
                  <input
                    type="text"
                    className="form-control"
                    value={systemSettings.default_tts_voice}
                    onChange={(e) => setSystemSettings({ ...systemSettings, default_tts_voice: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Default Video Provider</label>
                  <select
                    className="form-control"
                    value={systemSettings.default_video_provider}
                    onChange={(e) => setSystemSettings({ ...systemSettings, default_video_provider: e.target.value })}
                  >
                    <option value="kling">Kling AI</option>
                    <option value="fal">fal.ai</option>
                  </select>
                </div>
              </div>

              <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
                Database: <strong>SQLite (WAL)</strong> + schema inspector (`_sync_schema_sync`).
              </p>

              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? <><ButtonSpinner /> Đang lưu...</> : 'Save System Settings'}
                </button>
                <button type="button" className="btn btn-secondary" onClick={handleTestStorageConnection} disabled={storageTesting}>
                  {storageTesting ? 'Testing...' : 'Test Storage'}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => systemApi.health().then(res => alert(JSON.stringify(res, null, 2)))}
                >
                  Check Backend Health
                </button>
              </div>
            </div>
          </div>
        </form>
      )}

      {/* MODAL: ADD API KEY */}
      {showAddKeyModal && (
        <div className="modal-backdrop" onClick={(e) => { if (e.target === e.currentTarget) closeAddKeyModalSafely(); }}>
          <div className="modal-dialog">
            <div className="modal-header">
              <h3>Add API Key to Pool — {selectedProviderForKeys.toUpperCase()}</h3>
              <button type="button" className="modal-close-btn" onClick={closeAddKeyModalSafely}>&times;</button>
            </div>
            <div className="modal-body">
              {modalError && (
                <div className="alert alert-danger" style={{ marginBottom: '1rem', padding: '0.6rem 1rem', fontSize: '0.85rem' }}>
                  ⚠️ {modalError}
                </div>
              )}
              <form onSubmit={handleAddKey}>
                <div className="form-group">
                  <label className="form-label">API Key</label>
                  <input
                    type="password"
                    className="form-control"
                    placeholder="Paste raw secret API Key..."
                    value={newKeyInput}
                    onChange={(e) => { setNewKeyInput(e.target.value); if (modalError) setModalError(null); }}
                    required
                    autoFocus
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Priority (1 = Highest)</label>
                  <input
                    type="number"
                    className="form-control"
                    value={newKeyPriority}
                    min="1"
                    onChange={(e) => setNewKeyPriority(e.target.value)}
                  />
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={closeAddKeyModalSafely}>Cancel</button>
                  <button type="button" className="btn btn-primary" disabled={saving} onClick={handleAddKey}>
                    {saving ? <><ButtonSpinner /> Đang lưu...</> : 'Save Key'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: ADD CUSTOM PROVIDER */}
      {showAddProviderModal && (
        <div className="modal-backdrop" onClick={(e) => { if (e.target === e.currentTarget) closeAddProviderModalSafely(); }}>
          <div className="modal-dialog">
            <div className="modal-header">
              <h3>Add Custom Provider</h3>
              <button type="button" className="modal-close-btn" onClick={closeAddProviderModalSafely}>&times;</button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleAddCustomProvider}>
                <div className="form-group">
                  <label className="form-label">Provider ID (slug)</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. custom_llm"
                    value={customProviderData.id}
                    onChange={(e) => setCustomProviderData({ ...customProviderData, id: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Provider Display Name</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. Custom LLM Provider"
                    value={customProviderData.name}
                    onChange={(e) => setCustomProviderData({ ...customProviderData, name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Base URL</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="https://api.custom.com/v1"
                    value={customProviderData.base_url}
                    onChange={(e) => setCustomProviderData({ ...customProviderData, base_url: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">API Key</label>
                  <input
                    type="password"
                    className="form-control"
                    placeholder="Optional API Key..."
                    value={customProviderData.api_key}
                    onChange={(e) => setCustomProviderData({ ...customProviderData, api_key: e.target.value })}
                  />
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={closeAddProviderModalSafely}>Cancel</button>
                  <button type="submit" className="btn btn-primary" disabled={saving}>
                    {saving ? <><ButtonSpinner /> Đang thêm...</> : 'Add Provider'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: ADD SOCIAL ACCOUNT */}
      {showAddSocialModal && (
        <div className="modal-backdrop" onClick={(e) => { if (e.target === e.currentTarget) closeAddSocialModalSafely(); }}>
          <div className="modal-dialog">
            <div className="modal-header">
              <h3>Connect Social Account</h3>
              <button type="button" className="modal-close-btn" onClick={closeAddSocialModalSafely}>&times;</button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleAddSocialAccount}>
                <div className="form-group">
                  <label className="form-label">Platform</label>
                  <select
                    className="form-control"
                    value={newSocialData.platform}
                    onChange={(e) => setNewSocialData({ ...newSocialData, platform: e.target.value })}
                  >
                    <option value="youtube">YouTube</option>
                    <option value="tiktok">TikTok</option>
                    <option value="facebook">Facebook</option>
                    <option value="instagram">Instagram</option>
                  </select>
                </div>
                {newSocialData.platform === 'youtube' && (
                  <div style={{ marginBottom: '1.25rem', padding: '1rem', background: '#1e1b4b', border: '1px solid #6366f1', borderRadius: '8px', textAlign: 'center' }}>
                    <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.85rem', color: '#c7d2fe' }}>
                      🔑 Đăng nhập YouTube sẽ mở tab mới trên Google Chrome (không mở trong app):
                    </p>
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={handleConnectYouTubeOAuth}
                      style={{ background: 'linear-gradient(135deg, #ef4444, #dc2626)', width: '100%', fontWeight: 'bold' }}
                    >
                      🔴 Đăng Nhập Google OAuth 2.0 (YouTube)
                    </button>
                  </div>
                )}
                {newSocialData.platform === 'tiktok' && (
                  <div style={{ marginBottom: '1.25rem', padding: '1rem', background: '#111827', border: '1px solid #6b7280', borderRadius: '8px', textAlign: 'center' }}>
                    <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.85rem', color: '#e5e7eb' }}>
                      ♪ Đăng nhập TikTok sẽ mở tab mới trên Google Chrome. Sau khi cấp quyền, đóng tab đó và quay lại app.
                    </p>
                    <button
                      type="button"
                      className="btn btn-primary"
                      onClick={handleConnectTikTokOAuth}
                      style={{ background: 'linear-gradient(135deg, #111827, #000000)', width: '100%', fontWeight: 'bold' }}
                    >
                      ♪ Đăng Nhập TikTok (Login Kit)
                    </button>
                  </div>
                )}
                <div className="form-group">
                  <label className="form-label">Account / Channel Name</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. Official Channel"
                    value={newSocialData.account_name}
                    onChange={(e) => setNewSocialData({ ...newSocialData, account_name: e.target.value, channel_name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Channel ID (Optional)</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. UC_x5XG1OV2P6uZZ5FSM9Ttw"
                    value={newSocialData.channel_id}
                    onChange={(e) => setNewSocialData({ ...newSocialData, channel_id: e.target.value })}
                  />
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={closeAddSocialModalSafely}>Cancel</button>
                  <button type="submit" className="btn btn-primary" disabled={saving}>Connect</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>

  );
}
