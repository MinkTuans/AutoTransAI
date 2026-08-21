import React from 'react';

export default function Navbar({ activePage, setActivePage }) {
  return (
    <nav className="navbar">
      <a href="#" onClick={(e) => { e.preventDefault(); setActivePage('dashboard'); }} className="navbar-brand">
        🎬 <span>WorkflowVdAi</span>
      </a>
      <div className="navbar-links">
        <button
          className={`nav-link ${activePage === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActivePage('dashboard')}
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}
        >
          Projects
        </button>
        <button
          className={`nav-link ${activePage === 'create' ? 'active' : ''}`}
          onClick={() => setActivePage('create')}
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}
        >
          + New Project
        </button>
        <button
          className={`nav-link ${activePage === 'settings' ? 'active' : ''}`}
          onClick={() => setActivePage('settings')}
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}
        >
          Settings
        </button>
      </div>
    </nav>
  );
}
