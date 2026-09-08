import React from 'react';
import appLogo from '../assets/app-logo.png';

export default function Navbar({ activePage, setActivePage, onNavigate }) {
  const handleNavClick = (page) => {
    if (onNavigate) {
      onNavigate(page);
    } else if (setActivePage) {
      setActivePage(page);
    }
  };

  return (
    <nav className="navbar">
      <a
        href="#"
        onClick={(e) => { e.preventDefault(); handleNavClick('translator'); }}
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
          onClick={() => handleNavClick('translator')}
        >
          🌐 Dịch Video (Unified Workflow)
        </button>
        <button
          type="button"
          className={`nav-link ${activePage === 'dashboard' ? 'active' : ''}`}
          onClick={() => handleNavClick('dashboard')}
        >
          📁 Quản lý Dự án
        </button>
        <button
          type="button"
          className={`nav-link ${activePage === 'create' ? 'active' : ''}`}
          onClick={() => handleNavClick('create')}
        >
          + Tạo dự án mới
        </button>
        <button
          type="button"
          className={`nav-link ${activePage === 'settings' ? 'active' : ''}`}
          onClick={() => handleNavClick('settings')}
        >
          ⚙️ Cài đặt
        </button>
      </div>
    </nav>
  );
}
