import React, { useEffect, useState } from 'react';
import { aiApi } from '../../api';
import { ModelDetail } from './ModelCatalog';
import './FunctionRouting.css';

const PAGE_SIZE = 25;

function canSelect(model) {
  return model.selectable === true;
}

function accessLabel(model) {
  if (model.access_scope === 'keyless') return 'Keyless';
  if (!model.available_key_count) return 'No key';
  if (model.access_scope === 'catalog_unverified') return 'Public catalog · entitlement unverified';
  return 'Listing only';
}

function ModelPicker({ selectedFunction, onClose, onChoose, saving, saveError }) {
  const [providers, setProviders] = useState([]);
  const [providerError, setProviderError] = useState(false);
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
      if (active && response?.success) setProviders(response.data || []);
      else if (active) setProviderError(true);
    }).catch(() => { if (active) setProviderError(true); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(false);
    aiApi.listModels({ capability: selectedFunction.capability,
      provider_id: providerId || undefined, q: search || undefined,
      page, limit: PAGE_SIZE }).then(response => {
      if (active && response?.success) setResult(response.data);
      else if (active) setError(true);
    }).catch(() => { if (active) setError(true); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [selectedFunction.capability, providerId, search, page, retry]);

  const pages = Math.max(1, Math.ceil((result.total || 0) / PAGE_SIZE));
  const chooseProvider = id => {
    setProviderId(id);
    setSearch('');
    setQuery('');
    setPage(1);
  };

  return <div className="modal-backdrop" onClick={event => {
    if (event.target === event.currentTarget && !saving) onClose();
  }}>
    <div className="modal-dialog function-picker" role="dialog" aria-modal="true"
      style={{ width: 'min(1040px, 95vw)', maxWidth: 'min(1040px, 95vw)' }}
      aria-label={`Choose ${selectedFunction.capability} model for ${selectedFunction.function_name}`}>
      <div className="modal-header">
        <h3>Choose a model for {selectedFunction.function_name}</h3>
        <button type="button" className="modal-close-btn" aria-label="Close model picker"
          disabled={saving} onClick={onClose}>×</button>
      </div>
      <div className="modal-body">
        <p className="function-picker-note">Only a compatible, available catalog model can become this default.
          Public catalog listings do not prove per-key generation entitlement.</p>
        {providerError && <p role="alert">Could not load provider filters.</p>}
        <div className="catalog-providers" role="group" aria-label="Filter by provider">
          <button type="button" className={`btn ${!providerId ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => chooseProvider('')}>All providers</button>
          {providers.map(provider => <button type="button" key={provider.id}
            className={`btn ${providerId === provider.id ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => chooseProvider(provider.id)}>{provider.name}</button>)}
        </div>
        <form className="catalog-search" role="search" onSubmit={event => {
          event.preventDefault(); setSearch(query.trim()); setPage(1);
        }}>
          <input className="form-control" type="search" aria-label="Search models" maxLength={200}
            placeholder="Model ID, name, provider, capability" value={query}
            onChange={event => setQuery(event.target.value)} />
          <button className="btn btn-secondary" type="submit">Search</button>
        </form>
        {saveError && <p role="alert">{saveError}</p>}
        {loading ? <p role="status">Loading models…</p> : error ? <div role="alert">
          <p>Could not load models.</p>
          <button className="btn btn-secondary" type="button" onClick={() => setRetry(value => value + 1)}>Retry models</button>
        </div> : !result.items.length ? <p>No compatible catalog models found for this view.</p> : <>
          <div className="catalog-table-wrap"><table className="table catalog-table">
            <thead><tr><th>Model</th><th>Provider</th><th>Capabilities</th><th>Status</th><th>Access</th><th>Default for</th><th></th></tr></thead>
            <tbody>{result.items.map(model => {
              const label = model.display_name || model.remote_model_id;
              return <tr key={model.id}>
                <td><strong>{label}</strong><small>{model.remote_model_id}</small><small>Catalog ID: {model.id}</small></td>
                <td>{model.provider_name}</td>
                <td>{model.capability?.status === 'FULL_UNKNOWN'
                  ? <span className="badge badge-neutral">Capabilities unknown</span>
                  : model.capability?.capabilities?.length
                    ? model.capability.capabilities.map(cap => <span className="badge badge-purple" key={cap}>{cap}</span>)
                    : <span className="badge badge-neutral">No confirmed capabilities</span>}</td>
                <td><span className={`badge ${model.status === 'active' ? 'badge-success' : 'badge-warning'}`}>{model.status}</span></td>
                <td><span className="badge badge-info">{accessLabel(model)}</span>
                  <small>{model.access_scope === 'keyless' ? 'No key needed' : `${model.available_key_count} available keys`}</small></td>
                <td>{model.default_for?.length ? model.default_for.join(', ') : '—'}</td>
                <td className="function-picker-actions">
                  <button type="button" className="btn btn-secondary" aria-label={`Details for ${label}`}
                    onClick={() => setDetailId(model.id)}>Details</button>
                  <button type="button" className="btn btn-primary" aria-label={`Select ${label}`}
                    disabled={saving || !canSelect(model)}
                    onClick={() => onChoose(model)}>Select</button>
                </td>
              </tr>;
            })}</tbody>
          </table></div>
          <div className="catalog-pagination"><span>Page {page} of {pages} · {result.total} models</span>
            <div><button className="btn btn-secondary" type="button" aria-label="Previous page"
              disabled={page <= 1} onClick={() => setPage(value => value - 1)}>Previous</button>
            <button className="btn btn-secondary" type="button" aria-label="Next page"
              disabled={page >= pages} onClick={() => setPage(value => value + 1)}>Next</button></div>
          </div>
        </>}
      </div>
    </div>
    {detailId && <ModelDetail modelId={detailId} onClose={() => setDetailId(null)} />}
  </div>;
}

export default function FunctionRouting() {
  const [functions, setFunctions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [retry, setRetry] = useState(0);
  const [selectedFunction, setSelectedFunction] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState('');

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(false);
    aiApi.listFunctions().then(response => {
      if (active && response?.success) setFunctions(response.data || []);
      else if (active) setError(true);
    }).catch(() => { if (active) setError(true); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [retry]);

  const choose = async model => {
    if (!selectedFunction || !canSelect(model)) return;
    setSaving(true);
    setSaveError('');
    try {
      const response = await aiApi.updateFunction(selectedFunction.function_id, { model_id: model.id });
      if (!response?.success) throw new Error('Update unavailable');
      setFunctions(rows => rows.map(row => row.function_id === selectedFunction.function_id ? response.data : row));
      setSelectedFunction(null);
    } catch {
      setSaveError('Model unavailable; refresh the list and choose another.');
    } finally {
      setSaving(false);
    }
  };

  return <div className="card function-routing">
    <div className="card-header"><h3>⚡ AI Function Configuration & Routing</h3>
      <p>Choose exact catalog defaults. Invalid defaults stay visible until you replace them.</p></div>
    <div className="card-body">
      {loading ? <p role="status">Loading AI functions…</p> : error ? <div role="alert">
        <p>Could not load AI functions.</p>
        <button type="button" className="btn btn-secondary" onClick={() => setRetry(value => value + 1)}>Retry functions</button>
      </div> : !functions.length ? <p>No AI functions are configured yet.</p> :
        <div className="catalog-table-wrap"><table className="table function-routing-table">
          <thead><tr><th>AI Function</th><th>Capability</th><th>Default provider</th><th>Default model</th><th>Status</th><th></th></tr></thead>
          <tbody>{functions.map(fn => <tr key={fn.function_id}>
            <td><strong>{fn.function_name}</strong></td>
            <td><span className="badge badge-neutral">{fn.capability}</span></td>
            <td>{fn.primary_provider_id || '—'}</td>
            <td>{fn.model_display_name || <code>{fn.model_id || '—'}</code>}</td>
            <td><span className={`badge ${fn.default_status === 'ready' ? 'badge-success' : 'badge-warning'}`}>{fn.default_status}</span>
              {fn.configuration_error && <small>Configuration issue: {fn.configuration_error}</small>}</td>
            <td><button type="button" className="btn btn-secondary"
              aria-label={`Choose model for ${fn.function_name}`} onClick={() => {
                setSaveError(''); setSelectedFunction(fn);
              }}>Choose model</button></td>
          </tr>)}</tbody>
        </table></div>}
    </div>
    {selectedFunction && <ModelPicker selectedFunction={selectedFunction} saving={saving}
      saveError={saveError} onClose={() => setSelectedFunction(null)} onChoose={choose} />}
  </div>;
}
