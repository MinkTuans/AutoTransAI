import React, { useEffect, useState } from 'react';
import { aiApi } from '../../api';
import './ModelCatalog.css';

const PAGE_SIZE = 25;
const METADATA_FIELDS = {
  gemini: ['inputTokenLimit', 'outputTokenLimit', 'thinking'],
  openai: ['created'],
  anthropic: ['max_input_tokens', 'max_tokens'],
  elevenlabs: ['can_do_text_to_speech', 'can_do_voice_conversion', 'requires_alpha_access'],
  fal: ['category'],
};

function visibleMetadata(providerId, metadata) {
  if (!metadata || typeof metadata !== 'object') return [];
  return (METADATA_FIELDS[providerId] || []).flatMap(key => {
    const value = metadata[key];
    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
      return [[key, String(value)]];
    }
    return [];
  });
}

function scopeLabel(model) {
  if (model.access_scope === 'keyless') return 'Keyless';
  if (!model.available_key_count) return 'No key';
  if (model.access_scope === 'catalog_unverified') return 'Public catalog';
  return 'Listing only';
}

function ModelDetail({ modelId, onClose }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(false);
    aiApi.getModel(modelId).then(response => {
      if (!active) return;
      if (!response?.success) throw new Error('Model detail unavailable');
      setDetail(response.data);
    }).catch(() => { if (active) setError(true); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [modelId]);

  const title = detail?.display_name || detail?.remote_model_id || 'Model details';
  return (
    <div className="modal-backdrop" onClick={event => { if (event.target === event.currentTarget) onClose(); }}>
      <div className="modal-dialog" role="dialog" aria-modal="true" aria-label={`Model details: ${title}`}>
        <div className="modal-header">
          <h3>{title}</h3>
          <button type="button" className="modal-close-btn" aria-label="Close details" onClick={onClose}>×</button>
        </div>
        <div className="modal-body catalog-detail">
          {loading && <p>Loading details…</p>}
          {error && <p role="alert">Could not load model details.</p>}
          {detail && !error && <>
            <p><strong>Model ID:</strong> <code>{detail.remote_model_id}</code></p>
            <p><strong>Provider:</strong> {detail.provider_name}</p>
            <p><strong>Status:</strong> {detail.status}</p>
            <p><strong>Access:</strong> {scopeLabel(detail)}{detail.access_scope === 'catalog_unverified' ? ' (entitlement unverified)' : ''}</p>
            <p><strong>Available keys:</strong> {detail.available_key_count}</p>
            <p><strong>Last seen:</strong> {detail.last_seen ? new Date(detail.last_seen).toLocaleString() : 'Never'}</p>
            <p><strong>Used by:</strong> {detail.default_for?.length ? detail.default_for.join(', ') : 'None'}</p>
            <div><strong>Capabilities:</strong> {detail.capability?.status === 'FULL_UNKNOWN'
              ? 'Capabilities unknown' : detail.capability?.capabilities?.join(', ') || 'No confirmed capabilities'}</div>
            {visibleMetadata(detail.provider_id, detail.metadata).length > 0 && <dl className="catalog-metadata">
              {visibleMetadata(detail.provider_id, detail.metadata).map(([key, value]) => (
                <React.Fragment key={key}><dt>{key}</dt><dd>{value}</dd></React.Fragment>
              ))}
            </dl>}
          </>}
        </div>
      </div>
    </div>
  );
}

export default function ModelCatalog() {
  const [providers, setProviders] = useState([]);
  const [providersError, setProvidersError] = useState(false);
  const [providerId, setProviderId] = useState('');
  const [query, setQuery] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [result, setResult] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [retry, setRetry] = useState(0);
  const [detailId, setDetailId] = useState(null);

  useEffect(() => {
    let active = true;
    aiApi.listProviders().then(response => {
      if (!active) return;
      if (!response?.success) throw new Error('Providers unavailable');
      setProviders(response.data || []);
    }).catch(() => { if (active) setProvidersError(true); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(false);
    aiApi.listModels({ provider_id: providerId || undefined, q: search || undefined,
      page, limit: PAGE_SIZE }).then(response => {
      if (!active) return;
      if (!response?.success) throw new Error('Models unavailable');
      setResult(response.data);
    }).catch(() => { if (active) setError(true); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [providerId, search, page, retry]);

  const pages = Math.max(1, Math.ceil((result.total || 0) / PAGE_SIZE));
  const selectedProvider = providers.find(provider => provider.id === providerId);
  const chooseProvider = id => {
    setProviderId(id);
    setQuery('');
    setSearch('');
    setPage(1);
  };

  return <div className="card model-catalog">
    <div className="card-header">
      <h3>🧠 AI Models Catalog</h3>
      <p>Browse discovered and system models. Listings show visibility, not generation entitlement.</p>
    </div>
    <div className="card-body">
      {providersError && <p role="alert">Could not load providers.</p>}
      <div className="catalog-providers" role="group" aria-label="Filter by provider">
        <button type="button" className={`btn ${!providerId ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => chooseProvider('')}>All providers</button>
        {providers.map(provider => <button key={provider.id} type="button"
          className={`btn ${providerId === provider.id ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => chooseProvider(provider.id)}>
          {provider.name} <span className="badge badge-neutral">{provider.model_count}</span>
        </button>)}
      </div>
      <form className="catalog-search" role="search" onSubmit={event => {
        event.preventDefault(); setSearch(query.trim()); setPage(1);
      }}>
        <input className="form-control" type="search" aria-label="Search models" maxLength={200}
          placeholder="Model ID, name, provider or capability" value={query}
          onChange={event => setQuery(event.target.value)} />
        <button className="btn btn-secondary" type="submit">Search</button>
      </form>
      {loading ? <p role="status">Loading models…</p> : error ? <div role="alert">
        <p>Could not load models.</p>
        <button className="btn btn-secondary" type="button" onClick={() => setRetry(value => value + 1)}>Retry models</button>
      </div> : result.items.length === 0 ? <div className="catalog-empty">
        <p>No models found for this view.</p>
        {selectedProvider && <p>{selectedProvider.name} has no catalog models yet.</p>}
      </div> : <>
        <div className="catalog-table-wrap"><table className="table catalog-table">
          <thead><tr><th>Model</th><th>Provider</th><th>Status</th><th>Capability</th><th>Access</th><th>Default for</th><th></th></tr></thead>
          <tbody>{result.items.map(model => <tr key={model.id}>
            <td><strong>{model.display_name || model.remote_model_id}</strong><small>{model.remote_model_id}</small></td>
            <td>{model.provider_name}</td>
            <td><span className={`badge ${model.status === 'active' ? 'badge-success' : model.status === 'retired' ? 'badge-warning' : 'badge-neutral'}`}>{model.status}</span></td>
            <td>{model.capability?.status === 'FULL_UNKNOWN'
              ? <span className="badge badge-neutral">Capabilities unknown</span>
              : model.capability?.capabilities?.length
                ? model.capability.capabilities.map(cap => <span key={cap} className="badge badge-purple">{cap}</span>)
                : <span className="badge badge-neutral">No confirmed capabilities</span>}</td>
            <td><span className="badge badge-info">{scopeLabel(model)}</span><small>{model.access_scope === 'keyless' ? 'No key needed' : `${model.available_key_count} available keys`}</small></td>
            <td>{model.default_for?.length ? model.default_for.map(fn => <span key={fn} className="badge badge-neutral">{fn}</span>) : '—'}</td>
            <td><button className="btn btn-secondary" type="button"
              aria-label={`Details for ${model.display_name || model.remote_model_id}`}
              onClick={() => setDetailId(model.id)}>Details</button></td>
          </tr>)}</tbody>
        </table></div>
        <div className="catalog-pagination">
          <span>Page {page} of {pages} · {result.total} models</span>
          <div><button className="btn btn-secondary" type="button" aria-label="Previous page"
            disabled={page <= 1} onClick={() => setPage(value => value - 1)}>Previous</button>
          <button className="btn btn-secondary" type="button" aria-label="Next page"
            disabled={page >= pages} onClick={() => setPage(value => value + 1)}>Next</button></div>
        </div>
      </>}
    </div>
    {detailId && <ModelDetail modelId={detailId} onClose={() => setDetailId(null)} />}
  </div>;
}
