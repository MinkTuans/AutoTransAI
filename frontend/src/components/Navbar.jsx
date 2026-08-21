import React from 'react';
import appLogo from '../assets/app-logo.png';

export default function Navbar({ activePage, setActivePage }) {
  return (
    <nav className="navbar">
      <a
        href="#"
        onClick={(e) => { e.preventDefault(); setActivePage('dashboard'); }}
        className="navbar-brand"
      >
        <img
          src={appLogo}
          alt="WorkflowVdAi Logo"
          className="navbar-logo-img"
        />
        <span>WorkflowVdAi</span>
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
          className={`nav-link ${activePage === 'translator' ? 'active' : ''}`}
          onClick={() => setActivePage('translator')}
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}
        >
          🌐 Video Translator
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
