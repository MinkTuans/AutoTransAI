import React, { useState, useEffect } from 'react';

export default function ProjectGlossaryManager({ projectId }) {
  const [activeTab, setActiveTab] = useState('manual');
  const [terms, setTerms] = useState([]);
  const [memoryTerms, setMemoryTerms] = useState([]);
  const [sourceTerm, setSourceTerm] = useState('');
  const [translatedTerm, setTranslatedTerm] = useState('');
  const [termType, setTermType] = useState('character');

  const fetchGlossary = async () => {
    if (!projectId) return;
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

  const fetchMemory = async () => {
    if (!projectId) return;
    try {
      const res = await fetch(`/api/video-translator/projects/${projectId}/terminology-memory`);
      const data = await res.json();
      if (data.success) {
        setMemoryTerms(data.data || []);
      }
    } catch (err) {
      console.error('Failed fetching terminology memory', err);
    }
  };

  useEffect(() => {
    if (projectId) {
      fetchGlossary();
      fetchMemory();
    }
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

  const handleDeleteMemoryTerm = async (termId) => {
    try {
      const res = await fetch(`/api/video-translator/projects/${projectId}/terminology-memory/${termId}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      if (data.success) {
        fetchMemory();
      }
    } catch (err) {
      console.error('Failed deleting memory term', err);
    }
  };

  const handlePromoteMemoryToGlossary = async (item) => {
    try {
      await fetch(`/api/video-translator/projects/${projectId}/glossary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_term: item.source_term,
          translated_term: item.suggested_term,
          term_type: item.term_type,
        }),
      });
      fetchGlossary();
    } catch (err) {
      console.error('Failed promoting memory term', err);
    }
  };

  return (
    <div className="card" style={{ marginTop: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <h3 className="card-title" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          📖 Project Glossary & Terminology Memory
        </h3>
        
        {/* Sub-tabs */}
        <div style={{ display: 'flex', gap: '0.25rem', background: '#0f1117', padding: '0.25rem', borderRadius: '6px' }}>
          <button
            onClick={() => setActiveTab('manual')}
            style={{
              padding: '0.35rem 0.85rem',
              borderRadius: '4px',
              border: 'none',
              fontSize: '0.85rem',
              fontWeight: 500,
              cursor: 'pointer',
              background: activeTab === 'manual' ? '#3b82f6' : 'transparent',
              color: activeTab === 'manual' ? '#fff' : '#94a3b8',
            }}
          >
            ✏️ Glossary Thủ Công ({terms.length})
          </button>
          <button
            onClick={() => setActiveTab('memory')}
            style={{
              padding: '0.35rem 0.85rem',
              borderRadius: '4px',
              border: 'none',
              fontSize: '0.85rem',
              fontWeight: 500,
              cursor: 'pointer',
              background: activeTab === 'memory' ? '#10b981' : 'transparent',
              color: activeTab === 'memory' ? '#fff' : '#94a3b8',
            }}
          >
            🤖 AI Auto Terminology Memory ({memoryTerms.length})
          </button>
        </div>
      </div>

      {activeTab === 'manual' ? (
        <>
          {/* Form */}
          <form onSubmit={handleAddTerm} style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', alignItems: 'center', width: '100%', flexWrap: 'wrap' }}>
            <input
              type="text"
              className="form-control"
              placeholder="Source Term (e.g. 张三)"
              value={sourceTerm}
              onChange={(e) => setSourceTerm(e.target.value)}
              style={{ flex: 1, minWidth: '150px' }}
            />
            <input
              type="text"
              className="form-control"
              placeholder="Vietnamese Translation (e.g. Trương Tam)"
              value={translatedTerm}
              onChange={(e) => setTranslatedTerm(e.target.value)}
              style={{ flex: 1, minWidth: '150px' }}
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

          {/* Manual Glossary Table */}
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
                    Chưa có từ điển thủ công nào.
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
        </>
      ) : (
        <>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '1rem' }}>
            💡 Danh sách thuật ngữ tên riêng, địa danh, kỹ năng do AI tự động phát hiện trong quá trình phân tích kịch bản video.
          </p>
          <table className="table" style={{ fontSize: '0.85rem' }}>
            <thead>
              <tr>
                <th>Source Term</th>
                <th>AI Suggested Translation</th>
                <th>Type</th>
                <th>Confidence</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {memoryTerms.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                    Chưa có thuật ngữ tự động nào được ghi nhớ.
                  </td>
                </tr>
              ) : (
                memoryTerms.map((tm) => (
                  <tr key={tm.id}>
                    <td style={{ fontWeight: 'bold' }}>{tm.source_term}</td>
                    <td style={{ color: '#34d399' }}>{tm.suggested_term}</td>
                    <td style={{ textTransform: 'capitalize', color: 'var(--text-secondary)' }}>{tm.term_type}</td>
                    <td>
                      <span className="badge badge-info" style={{ fontSize: '0.75rem' }}>
                        {Math.round(tm.confidence * 100)}%
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                      <button
                        type="button"
                        className="btn btn-sm btn-primary"
                        onClick={() => handlePromoteMemoryToGlossary(tm)}
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', background: '#10b981' }}
                      >
                        ✓ Duyệt vào Glossary
                      </button>
                      <button
                        type="button"
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDeleteMemoryTerm(tm.id)}
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
