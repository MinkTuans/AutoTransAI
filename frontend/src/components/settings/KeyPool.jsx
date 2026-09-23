import React, { useEffect, useRef, useState } from 'react';
import { aiApi } from '../../api';

const safeStatus = value => ['complete', 'partial', 'failed', 'stale', 'unsupported', 'empty', 'disabled', 'already_enabled'].includes(value)
  ? value : 'unknown';

export default function KeyPool() {
  const [providers, setProviders] = useState([]);
  const [providerLoad, setProviderLoad] = useState('loading');
  const [selectedId, setSelectedId] = useState(null);
  const [keys, setKeys] = useState([]);
  const [keysLoad, setKeysLoad] = useState('idle');
  const [adding, setAdding] = useState(false);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [refresh, setRefresh] = useState(null);
  const selectionGeneration = useRef(0);
  const selectedIdRef = useRef(null);
  const keysRequestSequence = useRef(0);
  const selected = providers.find(provider => provider.id === selectedId);
  const isCurrent = generation => generation === selectionGeneration.current;

  useEffect(() => () => {
    selectionGeneration.current += 1;
    keysRequestSequence.current += 1;
    selectedIdRef.current = null;
  }, []);

  useEffect(() => {
    let active = true;
    aiApi.listProviders().then(response => {
      if (!active) return;
      if (!response?.success || !Array.isArray(response.data)) throw new Error('Invalid provider response');
      setProviders(response.data);
      selectedIdRef.current = response.data[0]?.id || null;
      setSelectedId(response.data[0]?.id || null);
      setProviderLoad('ready');
    }).catch(() => { if (active) setProviderLoad('error'); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!selected || selected.keyless) {
      keysRequestSequence.current += 1;
      setKeys([]);
      setKeysLoad('idle');
      return;
    }
    let active = true;
    const request = ++keysRequestSequence.current;
    setKeys([]);
    setKeysLoad('loading');
    aiApi.listKeys(selected.id).then(response => {
      if (!active || request !== keysRequestSequence.current) return;
      if (!response?.success || !Array.isArray(response.data)) throw new Error('Invalid keys response');
      setKeys(response.data);
      setKeysLoad('ready');
    }).catch(() => { if (active && request === keysRequestSequence.current) setKeysLoad('error'); });
    return () => { active = false; };
  }, [selectedId, selected?.keyless]);

  async function reloadKeys(providerId, generation) {
    const request = ++keysRequestSequence.current;
    try {
      const response = await aiApi.listKeys(providerId);
      if (!isCurrent(generation) || request !== keysRequestSequence.current) return;
      if (!response?.success || !Array.isArray(response.data)) throw new Error('Invalid keys response');
      setKeys(response.data);
      setKeysLoad('ready');
    } catch {
      if (isCurrent(generation) && request === keysRequestSequence.current) {
        setKeys([]);
        setKeysLoad('error');
      }
    }
  }

  async function addKey(event) {
    event.preventDefault();
    const secret = input.trim();
    if (!secret || !selected) return;
    const providerId = selected.id;
    const generation = selectionGeneration.current;
    setBusy(true);
    setError('');
    setNotice('');
    try {
      const response = await aiApi.addKey(providerId, secret);
      if (!isCurrent(generation)) return;
      if (!response?.success || !response.data?.key) throw new Error('Invalid add response');
      const { key, discovery } = response.data;
      setNotice(key.enabled
        ? 'Đã thêm Key và bật sau khi xác minh discovery complete.'
        : `Đã thêm Key nhưng vẫn tắt: discovery ${safeStatus(discovery?.status)}. Hãy kiểm tra rồi bật lại.`);
      await reloadKeys(providerId, generation);
    } catch {
      if (isCurrent(generation)) setError('Không thể thêm API Key. Vui lòng kiểm tra và thử lại.');
    } finally {
      if (isCurrent(generation)) {
        setInput('');
        setBusy(false);
      } else if (selectedIdRef.current === providerId) {
        await reloadKeys(providerId, selectionGeneration.current);
      }
    }
  }

  async function toggleKey(key) {
    const providerId = key.provider_id;
    const generation = selectionGeneration.current;
    setBusy(true);
    setError('');
    setNotice('');
    try {
      const response = await aiApi.setKeyEnabled(key.id, !key.enabled);
      if (!isCurrent(generation)) return;
      if (!response?.success || !response.data?.key) throw new Error('Invalid key response');
      const result = response.data;
      setKeys(current => current.map(entry => entry.id === key.id ? result.key : entry));
      setNotice(!key.enabled && !result.key.enabled
        ? `Key vẫn tắt: discovery ${safeStatus(result.discovery?.status)}.`
        : result.key.enabled ? 'Key đã bật.' : 'Key đã tắt.');
    } catch {
      if (isCurrent(generation)) setError('Không thể cập nhật API Key. Vui lòng thử lại.');
    } finally {
      if (isCurrent(generation)) setBusy(false);
      else if (selectedIdRef.current === providerId) await reloadKeys(providerId, selectionGeneration.current);
    }
  }

  async function removeKey(key) {
    if (!window.confirm('Xóa API Key này? Models trong catalog vẫn được giữ đến lần cập nhật Models complete tiếp theo.')) return;
    const providerId = key.provider_id;
    const generation = selectionGeneration.current;
    setBusy(true);
    setError('');
    setNotice('');
    try {
      const response = await aiApi.deleteKey(key.id);
      if (!isCurrent(generation)) return;
      if (!response?.success || !response.data?.deleted) throw new Error('Invalid delete response');
      setKeys(current => current.filter(entry => entry.id !== key.id));
      setNotice('Đã xóa Key. Catalog models chỉ được dọn trong lần cập nhật Models complete tiếp theo.');
    } catch {
      if (isCurrent(generation)) setError('Không thể xóa API Key. Vui lòng thử lại.');
    } finally {
      if (isCurrent(generation)) setBusy(false);
      else if (selectedIdRef.current === providerId) await reloadKeys(providerId, selectionGeneration.current);
    }
  }

  async function refreshModels() {
    const generation = selectionGeneration.current;
    setBusy(true);
    setError('');
    setNotice('');
    setRefresh(null);
    try {
      const response = await aiApi.refreshModels();
      if (!isCurrent(generation)) return;
      if (!response?.data?.status || !response.data.providers) throw new Error('Invalid refresh response');
      setRefresh(response.data);
    } catch {
      if (isCurrent(generation)) setError('Không thể cập nhật Models. Không thể xác nhận việc dọn catalog.');
    } finally {
      if (isCurrent(generation)) setBusy(false);
    }
  }

  return <div style={{ display: 'grid', gap: '1.5rem' }}>
    <div className="card">
      <div className="card-header"><h3>AI Provider Catalog</h3></div>
      <div className="card-body">
        {providerLoad === 'loading' && <p>Đang tải nhà cung cấp AI…</p>}
        {providerLoad === 'error' && <p role="alert">Không thể tải nhà cung cấp AI.</p>}
        {providerLoad === 'ready' && providers.length === 0 && <p>Chưa có nhà cung cấp AI.</p>}
        {providerLoad === 'ready' && providers.length > 0 && <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '1rem' }}>
          {providers.map(provider => <button type="button" key={provider.id}
            className={`provider-tile ${selectedId === provider.id ? 'is-selected' : ''}`}
            aria-pressed={selectedId === provider.id}
            onClick={() => {
              if (provider.id === selectedId) return;
              selectionGeneration.current += 1;
              keysRequestSequence.current += 1;
              selectedIdRef.current = provider.id;
              setSelectedId(provider.id);
              setAdding(false);
              setInput('');
              setBusy(false);
              setError('');
              setNotice('');
              setRefresh(null);
            }}
            style={{ textAlign: 'left', color: '#f8fafc' }}>
            <strong>{provider.name}</strong><br />
            <span className="badge badge-neutral">{provider.provider_type}</span>
            {provider.keyless && <span className="badge badge-success">Keyless</span>}
          </button>)}
        </div>}
      </div>
    </div>
    {selected && <div className="card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
        <h3>🔑 Key Pool — {selected.name}</h3>
        <div data-testid="key-pool-actions" style={{ display: 'flex', gap: '0.5rem' }}>
          <button type="button" className="btn btn-secondary" disabled={busy} onClick={refreshModels}>🔄 Cập nhật Models</button>
          {!selected.keyless && <button type="button" className="btn btn-primary" disabled={busy} onClick={() => setAdding(true)}>+ Thêm Key</button>}
        </div>
      </div>
      <div className="card-body">
        {error && <p role="alert" className="alert alert-danger">{error}</p>}
        {notice && <p role="status" className="alert alert-info">{notice}</p>}
        {refresh && <div role="status">
          <p>Cập nhật Models: {safeStatus(refresh.status)}.</p>
          {Object.entries(refresh.providers).map(([id, result]) => <p key={id}>
            {providers.find(provider => provider.id === id)?.name || id}: {safeStatus(result.status)}; {result.keys_scanned} keys scanned
            {result.status === 'complete' ? `; ${result.retired} models đã được dọn.` : '; chưa thể xác nhận việc dọn catalog.'}
          </p>)}
        </div>}
        {selected.keyless ? <p>Không cần API key cho {selected.name}.</p> : <>
          {keysLoad === 'loading' && <p>Đang tải Key Pool…</p>}
          {keysLoad === 'error' && <p role="alert">Không thể tải Key Pool.</p>}
          {keysLoad === 'ready' && keys.length === 0 && <p>Chưa có API key cho {selected.name}.</p>}
          {keysLoad === 'ready' && keys.length > 0 && <table className="table" style={{ width: '100%' }}>
            <thead><tr><th>Masked API Key</th><th>Enabled</th><th>Actions</th></tr></thead>
            <tbody>{keys.map(key => <tr key={key.id}>
              <td style={{ fontFamily: 'monospace' }}>{key.masked_key}</td>
              <td>{key.enabled ? 'Bật' : 'Tắt'}</td>
              <td><button type="button" className="btn btn-secondary" disabled={busy} onClick={() => toggleKey(key)}>{key.enabled ? 'Tắt Key' : 'Bật Key'}</button>{' '}
                <button type="button" className="btn btn-danger" disabled={busy} onClick={() => removeKey(key)}>Xóa Key</button></td>
            </tr>)}</tbody>
          </table>}
          {adding && <form onSubmit={addKey}>
            <label htmlFor="pool-api-key">API Key</label>
            <input id="pool-api-key" type="password" className="form-control" autoComplete="off" value={input} onChange={event => setInput(event.target.value)} />
            <button type="submit" className="btn btn-primary" disabled={busy || !input.trim()}>Lưu Key</button>{' '}
            <button type="button" className="btn btn-secondary" disabled={busy} onClick={() => { setInput(''); setAdding(false); }}>Đóng</button>
          </form>}
        </>}
      </div>
    </div>}
  </div>;
}
