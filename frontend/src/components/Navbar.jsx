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
          type="button"
          className={`nav-link ${activePage === 'translator' ? 'active' : ''}`}
          onClick={() => setActivePage('translator')}
        >
          🌐 Dịch Video (Unified Workflow)
        </button>
        <button
          type="button"
          className={`nav-link ${activePage === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActivePage('dashboard')}
        >
          📁 Quản lý Dự án
        </button>
        <button
          type="button"
          className={`nav-link ${activePage === 'create' ? 'active' : ''}`}
          onClick={() => setActivePage('create')}
        >
          + Tạo dự án mới
        </button>
        <button
          type="button"
          className={`nav-link ${activePage === 'settings' ? 'active' : ''}`}
          onClick={() => setActivePage('settings')}
        >
          ⚙️ Cài đặt
        </button>
      </div>
    </nav>
  );
}
