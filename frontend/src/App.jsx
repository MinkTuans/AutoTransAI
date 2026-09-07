import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import CreateProject from './pages/CreateProject';
import ProjectDetail from './pages/ProjectDetail';
import Settings from './pages/Settings';
import VideoTranslator from './pages/VideoTranslator';
import './App.css';

export default function App() {
  const [activePage, setActivePage] = useState('translator');
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
      <Navbar
        activePage={activePage}
        setActivePage={(page) => {
          setSelectedJobId(null);
          setActivePage(page);
        }}
      />

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

        {activePage === 'detail' && (
          selectedProjectId ? (
            <ProjectDetail
              projectId={selectedProjectId}
              onBack={() => setActivePage('dashboard')}
              onEditInTranslator={(projId) => {
                setSelectedProjectId(projId);
                setActivePage('translator');
              }}
            />
          ) : (
            <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#cbd5e1' }}>
              <h3 style={{ color: '#f87171', marginBottom: '0.5rem' }}>⚠️ Chưa chọn dự án</h3>
              <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>Vui lòng chọn một dự án từ danh sách Dashboard để xem chi tiết.</p>
              <button
                className="btn btn-secondary"
                onClick={() => setActivePage('dashboard')}
              >
                ← Quay lại Dashboard
              </button>
            </div>
          )
        )}

        {activePage === 'translator' && (
          <VideoTranslator
            initialJobId={selectedJobId}
            initialProjectId={selectedProjectId}
          />
        )}

        {activePage === 'settings' && <Settings />}
      </main>
    </div>
  );
}
