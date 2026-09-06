import React, { useState, useEffect } from 'react';

export default function ProjectGlossaryManager({ projectId }) {
  const [terms, setTerms] = useState([]);
  const [sourceTerm, setSourceTerm] = useState('');
  const [translatedTerm, setTranslatedTerm] = useState('');
  const [termType, setTermType] = useState('character');

  const fetchGlossary = async () => {
    try {
      const res = await fetch(`/api/video-translator/projects/${projectId}/glossary`);
      const data = await res.json();
      if (data.success) {
        setTerms(data.data || []);
      }
    } catch (err) {
      console.error('Failed fetching glossary', err);
    }
  };

  useEffect(() => {
    if (projectId) fetchGlossary();
  }, [projectId]);

  const handleAddTerm = async (e) => {
    e.preventDefault();
    if (!sourceTerm.trim() || !translatedTerm.trim()) return;

    try {
      const res = await fetch(`/api/video-translator/projects/${projectId}/glossary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_term: sourceTerm,
          translated_term: translatedTerm,
          term_type: termType,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setSourceTerm('');
        setTranslatedTerm('');
        fetchGlossary();
      }
    } catch (err) {
      console.error('Failed adding term', err);
    }
  };

  const handleDeleteTerm = async (termId) => {
    try {
      const res = await fetch(`/api/video-translator/projects/${projectId}/glossary/${termId}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      if (data.success) {
        fetchGlossary();
      }
    } catch (err) {
      console.error('Failed deleting term', err);
    }
  };

  return (
    <div className="card" style={{ marginTop: '1.5rem' }}>
      <h3 className="card-title" style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        📖 Project Glossary & Terminology Memory
      </h3>
      
      {/* Form */}
      <form onSubmit={handleAddTerm} style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', alignItems: 'center', width: '100%' }}>
        <input
          type="text"
          className="form-control"
          placeholder="Source Term (e.g. 张三)"
          value={sourceTerm}
          onChange={(e) => setSourceTerm(e.target.value)}
          style={{ flex: 1, minWidth: 0 }}
        />
        <input
          type="text"
          className="form-control"
          placeholder="Vietnamese Translation (e.g. Trương Tam)"
          value={translatedTerm}
          onChange={(e) => setTranslatedTerm(e.target.value)}
          style={{ flex: 1, minWidth: 0 }}
        />
        <select
          className="form-select"
          value={termType}
          onChange={(e) => setTermType(e.target.value)}
          style={{ width: '150px', flexShrink: 0 }}
        >
          <option value="character">Character</option>
          <option value="location">Location</option>
          <option value="organization">Organization</option>
          <option value="skill">Skill / Weapon</option>
          <option value="title">Title</option>
          <option value="other">Other</option>
        </select>
        <button type="submit" className="btn btn-primary" style={{ backgroundColor: '#10b981', flexShrink: 0, whiteSpace: 'nowrap' }}>
          + Add Term
        </button>
      </form>

      {/* Table */}
      <table className="table" style={{ fontSize: '0.85rem' }}>
        <thead>
          <tr>
            <th>Source Term</th>
            <th>Vietnamese Translation</th>
            <th>Type</th>
            <th style={{ textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {terms.length === 0 ? (
            <tr>
              <td colSpan={4} style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                No glossary terms added yet.
              </td>
            </tr>
          ) : (
            terms.map((t) => (
              <tr key={t.id}>
                <td style={{ fontWeight: 'bold' }}>{t.source_term}</td>
                <td style={{ color: '#60a5fa' }}>{t.translated_term}</td>
                <td style={{ textTransform: 'capitalize', color: 'var(--text-secondary)' }}>{t.term_type}</td>
                <td style={{ textAlign: 'right' }}>
                  <button
                    type="button"
                    className="btn btn-danger"
                    onClick={() => handleDeleteTerm(t.id)}
                    style={{ padding: '0.25rem 0.625rem', fontSize: '0.8rem' }}
                  >
                    🗑️ Delete
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
