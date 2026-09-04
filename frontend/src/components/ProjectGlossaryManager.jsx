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
    <div style={{ background: '#1F2937', padding: '20px', borderRadius: '12px', color: '#F3F4F6', marginTop: '20px' }}>
      <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: 'bold' }}>📖 Project Glossary & Terminology Memory</h3>
      
      {/* Form */}
      <form onSubmit={handleAddTerm} style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <input
          type="text"
          placeholder="Source Term (e.g. 张三)"
          value={sourceTerm}
          onChange={(e) => setSourceTerm(e.target.value)}
          style={{ flex: 1, padding: '8px 12px', borderRadius: '6px', border: '1px solid #374151', background: '#111827', color: '#FFF' }}
        />
        <input
          type="text"
          placeholder="Translated Term (e.g. Trương Tam)"
          value={translatedTerm}
          onChange={(e) => setTranslatedTerm(e.target.value)}
          style={{ flex: 1, padding: '8px 12px', borderRadius: '6px', border: '1px solid #374151', background: '#111827', color: '#FFF' }}
        />
        <select
          value={termType}
          onChange={(e) => setTermType(e.target.value)}
          style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #374151', background: '#111827', color: '#FFF' }}
        >
          <option value="character">Character</option>
          <option value="location">Location</option>
          <option value="organization">Organization</option>
          <option value="skill">Skill / Weapon</option>
          <option value="title">Title</option>
          <option value="other">Other</option>
        </select>
        <button type="submit" style={{ padding: '8px 16px', background: '#10B981', color: '#FFF', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
          + Add Term
        </button>
      </form>

      {/* Table */}
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
        <thead>
          <tr style={{ background: '#111827', textAlign: 'left' }}>
            <th style={{ padding: '8px' }}>Source Term</th>
            <th style={{ padding: '8px' }}>Vietnamese Translation</th>
            <th style={{ padding: '8px' }}>Type</th>
            <th style={{ padding: '8px', textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {terms.length === 0 ? (
            <tr>
              <td colSpan={4} style={{ padding: '12px', textAlign: 'center', color: '#9CA3AF' }}>
                No glossary terms added yet.
              </td>
            </tr>
          ) : (
            terms.map((t) => (
              <tr key={t.id} style={{ borderBottom: '1px solid #374151' }}>
                <td style={{ padding: '8px', fontWeight: 'bold' }}>{t.source_term}</td>
                <td style={{ padding: '8px', color: '#60A5FA' }}>{t.translated_term}</td>
                <td style={{ padding: '8px', textTransform: 'capitalize', color: '#9CA3AF' }}>{t.term_type}</td>
                <td style={{ padding: '8px', textAlign: 'right' }}>
                  <button
                    onClick={() => handleDeleteTerm(t.id)}
                    style={{ padding: '4px 8px', background: '#EF4444', color: '#FFF', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                  >
                    🗑️
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
