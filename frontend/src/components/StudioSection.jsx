import React from 'react';

export default function StudioSection({ id, title, summary, open, onToggle, children }) {
  return (
    <section className="studio-section" data-studio-section={id}>
      <h2><button type="button" id={`${id}-heading`} aria-expanded={open}
        aria-controls={`${id}-panel`} onClick={() => onToggle(!open)}>
        <span>{title}</span><span className="collapse-chip">{open ? 'Thu gọn' : 'Mở rộng'}</span>
      </button></h2>
      {summary && <p className="studio-section-summary">{summary}</p>}
      <div id={`${id}-panel`} role="region" aria-labelledby={`${id}-heading`} hidden={!open}>
        {children}
      </div>
    </section>
  );
}
