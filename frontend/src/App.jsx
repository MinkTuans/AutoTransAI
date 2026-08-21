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

  const handleSelectProject = (projectId) => {
    setSelectedProjectId(projectId);
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
      <Navbar activePage={activePage} setActivePage={setActivePage} />
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

        {activePage === 'translator' && <VideoTranslator />}

        {activePage === 'settings' && <Settings />}
      </main>
    </div>
  );
}

