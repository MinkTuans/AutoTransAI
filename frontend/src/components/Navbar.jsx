import React from 'react';
import appLogo from '../assets/app-logo.png';

export default function Navbar({ activePage, setActivePage }) {
  return (
    <nav className="navbar">
      <a
        href="#"
        onClick={(e) => { e.preventDefault(); setActivePage('app_selector'); }}
        className="navbar-brand"
      >
        <img
          src={appLogo}
          alt="WorkflowVdAi Logo"
          className="navbar-logo-img"
        />
        <span>WorkflowVdAi Hub</span>
      </a>
      <div className="navbar-links">
        <button
          className={`nav-link ${activePage === 'app_selector' ? 'active' : ''}`}
          onClick={() => setActivePage('app_selector')}
          style={{ background: 'none', border: 'none', cursor: 'pointer', fontWeight: 'bold', color: '#60a5fa' }}
        >
          🎛️ Chọn ứng dụng
        </button>
        <button
          className={`nav-link ${activePage === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActivePage('dashboard')}
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}
        >
          Dự án
        </button>
        <button
          className={`nav-link ${activePage === 'create' ? 'active' : ''}`}
          onClick={() => setActivePage('create')}
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}
        >
          + Tạo dự án mới
        </button>
        <button
          className={`nav-link ${activePage === 'translator' ? 'active' : ''}`}
          onClick={() => setActivePage('translator')}
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}
        >
          🌐 Dịch Video
        </button>
        <button
          className={`nav-link ${activePage === 'settings' ? 'active' : ''}`}
          onClick={() => setActivePage('settings')}
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}
        >
          Cài đặt
        </button>
      </div>
    </nav>
  );
}
