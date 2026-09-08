import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import CreateProject from './pages/CreateProject';
import ProjectDetail from './pages/ProjectDetail';
import Settings from './pages/Settings';
import VideoTranslator from './pages/VideoTranslator';
import './App.css';

const getInitialStateFromUrl = () => {
  try {
    const params = new URLSearchParams(window.location.search);
    const page = params.get('page') || localStorage.getItem('autotrans_active_page') || 'translator';
    const projId = params.get('projectId') || localStorage.getItem('autotrans_project_id') || null;
    const jobId = params.get('jobId') || localStorage.getItem('autotrans_job_id') || null;
    return { page, projId, jobId };
  } catch (e) {
    return { page: 'translator', projId: null, jobId: null };
  }
};

const syncUrlAndStorage = (page, projId, jobId) => {
  try {
    const params = new URLSearchParams();
    if (page) params.set('page', page);
    if (projId) params.set('projectId', projId);
    if (jobId) params.set('jobId', jobId);
    
    const queryString = params.toString();
    const newUrl = queryString ? `${window.location.pathname}?${queryString}` : window.location.pathname;
    window.history.replaceState({}, '', newUrl);

    if (page) localStorage.setItem('autotrans_active_page', page);
    if (projId) localStorage.setItem('autotrans_project_id', projId); else localStorage.removeItem('autotrans_project_id');
    if (jobId) localStorage.setItem('autotrans_job_id', jobId); else localStorage.removeItem('autotrans_job_id');
  } catch (e) {
    console.error('Failed to sync URL state:', e);
  }
};

export default function App() {
  const initialState = getInitialStateFromUrl();
  const [activePage, setActivePage] = useState(initialState.page);
  const [selectedProjectId, setSelectedProjectId] = useState(initialState.projId);
  const [selectedJobId, setSelectedJobId] = useState(initialState.jobId);
  const [isTranslatorProcessing, setIsTranslatorProcessing] = useState(false);

  useEffect(() => {
    syncUrlAndStorage(activePage, selectedProjectId, selectedJobId);
  }, [activePage, selectedProjectId, selectedJobId]);

  const confirmNavigationIfRunning = (targetPage) => {
    if (activePage === 'translator' && targetPage !== 'translator' && isTranslatorProcessing) {
      const confirmLeave = window.confirm(
        '⚠️ Tiến trình Dịch Video đang chạy!\n\nNếu bạn chuyển trang lúc này, quá trình cập nhật tiến độ real-time trên giao diện sẽ bị tạm dừng (tiến trình ở Backend vẫn tiếp tục chạy ngầm).\n\nBạn có chắc chắn muốn chuyển trang không?'
      );
      if (!confirmLeave) {
        return false;
      }
    }
    return true;
  };

  const handleNavigatePage = (targetPage) => {
    if (!confirmNavigationIfRunning(targetPage)) return;
    if (targetPage !== 'translator') {
      setSelectedJobId(null);
    }
    setActivePage(targetPage);
    syncUrlAndStorage(targetPage, selectedProjectId, targetPage === 'translator' ? selectedJobId : null);
  };

  const handleSelectProject = (item) => {
    if (!confirmNavigationIfRunning('detail')) return;
    if (typeof item === 'object' && item !== null) {
      if (item.type === 'video_translator') {
        const jId = item.id || item.job_id;
        const pId = item.project_id || null;
        setSelectedJobId(jId);
        if (pId) setSelectedProjectId(pId);
        setActivePage('translator');
        syncUrlAndStorage('translator', pId || selectedProjectId, jId);
        return;
      }
      setSelectedProjectId(item.id);
      setSelectedJobId(null);
      setActivePage('detail');
      syncUrlAndStorage('detail', item.id, null);
      return;
    }
    setSelectedProjectId(item);
    setSelectedJobId(null);
    setActivePage('detail');
    syncUrlAndStorage('detail', item, null);
  };

  const handleCreateNew = () => {
    if (!confirmNavigationIfRunning('create')) return;
    setActivePage('create');
    syncUrlAndStorage('create', null, null);
  };

  const handleProjectCreated = (projectId) => {
    setSelectedProjectId(projectId);
    setSelectedJobId(null);
    setActivePage('detail');
    syncUrlAndStorage('detail', projectId, null);
  };

  return (
    <div className="app-container">
      <Navbar
        activePage={activePage}
        onNavigate={handleNavigatePage}
        setActivePage={handleNavigatePage}
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
              onBack={() => handleNavigatePage('dashboard')}
              onEditInTranslator={(projId, jobId) => {
                if (!confirmNavigationIfRunning('translator')) return;
                setSelectedProjectId(projId);
                setSelectedJobId(jobId || null);
                setActivePage('translator');
                syncUrlAndStorage('translator', projId, jobId || null);
              }}
            />
          ) : (
            <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#cbd5e1' }}>
              <h3 style={{ color: '#f87171', marginBottom: '0.5rem' }}>⚠️ Chưa chọn dự án</h3>
              <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>Vui lòng chọn một dự án từ danh sách Dashboard để xem chi tiết.</p>
              <button
                className="btn btn-secondary"
                onClick={() => handleNavigatePage('dashboard')}
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
            onProcessingStateChange={setIsTranslatorProcessing}
          />
        )}

        {activePage === 'settings' && <Settings />}
      </main>
    </div>
  );
}
