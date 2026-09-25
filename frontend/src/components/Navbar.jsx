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
          Studio
        </button>
        <button
          type="button"
          className={`nav-link ${activePage === 'merger' ? 'active' : ''}`}
          onClick={() => handleNavClick('merger')}
        >
          Ghép Video
        </button>
        <button
          type="button"
          className={`nav-link ${activePage === 'live_audio' ? 'active' : ''}`}
          onClick={() => handleNavClick('live_audio')}
        >
          Dịch Audio trực tiếp
        </button>
        <button
          type="button"
          className={`nav-link ${activePage === 'dashboard' || activePage === 'detail' ? 'active' : ''}`}
          onClick={() => handleNavClick('dashboard')}
        >
          Dự án
        </button>
        <button
          type="button"
          className={`nav-link ${activePage === 'settings' ? 'active' : ''}`}
          onClick={() => handleNavClick('settings')}
        >
          Cài đặt
        </button>
      </div>
    </nav>
  );
}
