import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import CreateProject from './pages/CreateProject';
import ProjectDetail from './pages/ProjectDetail';
import Settings from './pages/Settings';
import VideoTranslator from './pages/VideoTranslator';
import './App.css';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [selectedJobId, setSelectedJobId] = useState(null);

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

  return (
    <div className="app-container">
      <Navbar activePage={activePage} setActivePage={(page) => { setSelectedJobId(null); setActivePage(page); }} />
      <main className="main-content">
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

