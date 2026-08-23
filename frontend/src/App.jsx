import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import CreateProject from './pages/CreateProject';
import ProjectDetail from './pages/ProjectDetail';
import Settings from './pages/Settings';
import VideoTranslator from './pages/VideoTranslator';
import AppSelector from './pages/AppSelector';
import ExternalAppViewer from './components/ExternalAppViewer';
import './App.css';

export default function App() {
  const [activePage, setActivePage] = useState('app_selector');
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [activeExternalApp, setActiveExternalApp] = useState(null);
  const [isHeaderCollapsed, setIsHeaderCollapsed] = useState(() => {
    const saved = localStorage.getItem('external_app_header_collapsed');
    return saved !== null ? JSON.parse(saved) : false;
  });

  const toggleHeaderCollapse = () => {
    setIsHeaderCollapsed((prev) => {
      const nextState = !prev;
      localStorage.setItem('external_app_header_collapsed', JSON.stringify(nextState));
      return nextState;
    });
  };

  const APP_CONFIGS = {
    krillin_ai: { title: 'KrillinAI', url: '/apps/krillin_ai/' },
    py_video_trans: { title: 'pyVideoTrans', url: '/apps/py_video_trans/?__theme=light' },
    soni_translate: { title: 'SoniTranslate', url: '/apps/soni_translate/' },
  };

  const handleSelectApp = (appKey) => {
    if (appKey === 'workflow_vd_ai') {
      setActiveExternalApp(null);
      setActivePage('dashboard');
    } else {
      setActiveExternalApp(appKey);
      setActivePage('external_app');
    }
  };

  const handleSelectProject = (item) => {
    if (typeof item === 'object' && item !== null) {
      if (item.type === 'video_translator') {
        setSelectedJobId(item.id || item.job_id);
        setActivePage('translator');
        return;
      }
      setSelectedProjectId(item.id);
      setActivePage('detail');
      return;
    }
    setSelectedProjectId(item);
    setActivePage('detail');
  };

  const handleCreateNew = () => {
    setActivePage('create');
  };

  const handleProjectCreated = (projectId) => {
    setSelectedProjectId(projectId);
    setActivePage('detail');
  };

  const showNavbar = activePage !== 'external_app' || !isHeaderCollapsed;

  return (
    <div className="app-container">
      {showNavbar && (
        <Navbar
          activePage={activePage}
          setActivePage={(page) => {
            setSelectedJobId(null);
            if (page !== 'external_app') {
              setActiveExternalApp(null);
            }
            setActivePage(page);
          }}
        />
      )}

      <main className="main-content">
        {activePage === 'app_selector' && (
          <AppSelector
            onSelectApp={handleSelectApp}
            currentApp={activeExternalApp || 'workflow_vd_ai'}
          />
        )}

        {activePage === 'external_app' && activeExternalApp && (
          <ExternalAppViewer
            appKey={activeExternalApp}
            appUrl={APP_CONFIGS[activeExternalApp].url}
            appTitle={APP_CONFIGS[activeExternalApp].title}
            onBack={() => setActivePage('app_selector')}
            isHeaderCollapsed={isHeaderCollapsed}
            onToggleHeaderCollapse={toggleHeaderCollapse}
          />
        )}

        {activePage === 'dashboard' && (
          <Dashboard
            onSelectProject={handleSelectProject}
            onCreateNew={handleCreateNew}
          />
        )}

        {activePage === 'create' && (
          <CreateProject onProjectCreated={handleProjectCreated} />
        )}

        {activePage === 'detail' && selectedProjectId && (
          <ProjectDetail
            projectId={selectedProjectId}
            onBack={() => setActivePage('dashboard')}
          />
        )}

        {activePage === 'translator' && <VideoTranslator initialJobId={selectedJobId} />}

        {activePage === 'settings' && <Settings />}
      </main>
    </div>
  );
}
