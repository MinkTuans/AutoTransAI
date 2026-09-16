import React, { useEffect, useState } from 'react';
import { videoTranslatorApi } from '../api';

const EMPTY_FORM = { source_term: '', translated_term: '', term_type: 'character' };

export default function ProjectGlossaryManager({ projectId, refreshKey }) {
  const [terms, setTerms] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');

  const fetchGlossary = async () => {
    if (!projectId) return;
    try {
      const response = await videoTranslatorApi.getGlossary(projectId);
      if (response.success) setTerms(response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail?.message || 'Không thể tải Glossary.');
    }
  };

  useEffect(() => {
    fetchGlossary();
  }, [projectId, refreshKey]);

  const resetForm = () => {
    setForm(EMPTY_FORM);
    setEditingId(null);
    setError('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!form.source_term.trim() || !form.translated_term.trim()) return;
    setError('');
    try {
      if (editingId) await videoTranslatorApi.updateGlossary(projectId, editingId, form);
      else await videoTranslatorApi.addGlossary(projectId, form);
      resetForm();
      await fetchGlossary();
    } catch (err) {
      const detail = err.response?.data?.detail;
      const existing = detail?.existing;
      setError(existing
        ? `${detail.message}: ${existing.source_term} → ${existing.translated_term}`
        : detail || 'Không thể lưu Glossary.');
    }
  };

  const startEdit = (term) => {
    setEditingId(term.id);
    setForm({ source_term: term.source_term, translated_term: term.translated_term, term_type: term.term_type });
    setError('');
  };

  const handleDelete = async (termId) => {
    try {
      await videoTranslatorApi.deleteGlossary(projectId, termId);
      if (editingId === termId) resetForm();
      await fetchGlossary();
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể xóa Glossary entry.');
    }
  };

  const setField = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  return (
    <div className="card" style={{ marginTop: '1.5rem' }}>
      <h3 className="card-title" style={{ marginBottom: '1rem' }}>📖 Glossary ({terms.length})</h3>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.75rem', marginBottom: '0.75rem', alignItems: 'center', width: '100%', flexWrap: 'wrap' }}>
        <input className="form-control" value={form.source_term} onChange={(e) => setField('source_term', e.target.value)} placeholder="Source (ví dụ: 李道天)" style={{ flex: 1, minWidth: '150px' }} />
        <input className="form-control" value={form.translated_term} onChange={(e) => setField('translated_term', e.target.value)} placeholder="Canonical translation (ví dụ: Lý Đạo Thiên)" style={{ flex: 1, minWidth: '180px' }} />
        <select className="form-select" value={form.term_type} onChange={(e) => setField('term_type', e.target.value)} style={{ width: '150px' }}>
          <option value="character">Character</option><option value="creature">Creature</option>
          <option value="location">Location</option><option value="organization">Organization</option>
          <option value="skill">Skill</option><option value="weapon">Weapon</option>
          <option value="item">Item</option><option value="technique">Technique</option>
          <option value="title">Title</option><option value="other">Important Term</option>
        </select>
        <button type="submit" className="btn btn-primary">{editingId ? 'Save Edit' : '+ Add Term'}</button>
        {editingId && <button type="button" className="btn" onClick={resetForm}>Cancel</button>}
      </form>
      {error && <div className="alert alert-danger" role="alert" style={{ marginBottom: '1rem' }}>{String(error)}</div>}
      <table className="table" style={{ fontSize: '0.85rem' }}>
        <thead><tr><th>Source</th><th>Canonical Translation</th><th>Type</th><th style={{ textAlign: 'right' }}>Actions</th></tr></thead>
        <tbody>{terms.length === 0 ? (
          <tr><td colSpan={4} style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Chưa có Glossary entry.</td></tr>
        ) : terms.map((term) => (
          <tr key={term.id}>
            <td style={{ fontWeight: 'bold' }}>{term.source_term}</td><td style={{ color: '#60a5fa' }}>{term.translated_term}</td>
            <td style={{ textTransform: 'capitalize' }}>{term.term_type}</td>
            <td style={{ textAlign: 'right' }}>
              <button type="button" className="btn btn-sm" onClick={() => startEdit(term)} style={{ marginRight: '0.5rem' }}>Edit</button>
              <button type="button" className="btn btn-sm btn-danger" onClick={() => handleDelete(term.id)}>Delete</button>
            </td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  );
}
