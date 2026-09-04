import React from 'react';
import appLogo from '../assets/app-logo.png';

export default function Navbar({ activePage, setActivePage }) {
  return (
    <nav className="navbar">
      <a
        href="#"
        onClick={(e) => { e.preventDefault(); setActivePage('translator'); }}
        className="navbar-brand"
      >
        <img
          src={appLogo}
          alt="AutoTransAi Logo"
          className="navbar-logo-img"
        />
        <span>AutoTransAi</span>
      </a>
      <div className="navbar-links">
        <button
          className={`nav-link ${activePage === 'translator' ? 'active' : ''}`}
          onClick={() => setActivePage('translator')}
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontWeight: 'bold', color: activePage === 'translator' ? '#60a5fa' : '#94a3b8' }}
        >
          🌐 Dịch Video (Unified Workflow)
        </button>
        <button
          className={`nav-link ${activePage === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActivePage('dashboard')}
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}
        >
          📁 Quản lý Dự án
        </button>
        <button
          className={`nav-link ${activePage === 'create' ? 'active' : ''}`}
          onClick={() => setActivePage('create')}
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}
        >
          + Tạo dự án mới
        </button>
        <button
          className={`nav-link ${activePage === 'settings' ? 'active' : ''}`}
          onClick={() => setActivePage('settings')}
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}
        >
          ⚙️ Cài đặt
        </button>
      </div>
    </nav>
  );
}
