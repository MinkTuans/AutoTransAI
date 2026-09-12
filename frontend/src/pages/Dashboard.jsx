import React, { useState, useEffect } from 'react';
import { projectsApi, systemApi } from '../api';
import { LoadingSpinner, SkeletonLoader } from '../components/LoadingSpinner';

export default function Dashboard({ onSelectProject, onCreateNew }) {

  const [projects, setProjects] = useState([]);
  const [interrupted, setInterrupted] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Selection state
  const [selectedIds, setSelectedIds] = useState([]);

  // Pagination state (8 items per page)
  const ITEMS_PER_PAGE = 8;
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  
  // Delete confirmation modal state
  const [confirmModal, setConfirmModal] = useState({
    open: false,
    title: '',
    message: '',
    itemsToDelete: [],
  });

  // Edit project title modal state
  const [editModal, setEditModal] = useState({
    open: false,
    projectId: null,
    currentTitle: '',
  });
  const [editingTitleValue, setEditingTitleValue] = useState('');
  const [savingTitle, setSavingTitle] = useState(false);

  const promptEditTitle = (p, e) => {
    if (e) e.stopPropagation();
    setEditModal({
      open: true,
      projectId: p.id,
      currentTitle: p.title || '',
    });
    setEditingTitleValue(p.title || '');
  };

  const handleSaveProjectTitle = async () => {
    if (!editModal.projectId || !editingTitleValue.trim()) return;
    setSavingTitle(true);
    try {
      const res = await projectsApi.update(editModal.projectId, { title: editingTitleValue.trim() });
      if (res.success) {
        setEditModal({ open: false, projectId: null, currentTitle: '' });
        await loadData();
      } else {
        alert('Không thể cập nhật tên dự án: ' + (res.message || 'Lỗi không xác định'));
      }
    } catch (err) {
      alert('Lỗi khi cập nhật tên dự án: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSavingTitle(false);
    }
  };


  const loadData = async (targetPage = currentPage) => {
    setLoading(true);
    try {
      const [projRes, intRes] = await Promise.all([
        projectsApi.list(targetPage, ITEMS_PER_PAGE),
        systemApi.interrupted().catch(() => ({ success: false, data: [] })),
      ]);
      if (projRes.success && Array.isArray(projRes.data)) {
        setProjects(projRes.data);
        setTotalCount(projRes.total !== undefined ? projRes.total : projRes.data.length);
      }
      if (intRes.success && Array.isArray(intRes.data)) {
        setInterrupted(intRes.data);
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(currentPage);
  }, [currentPage]);

  // Paginated projects calculations (server-side 8 per page)
  const totalPages = Math.max(1, Math.ceil(totalCount / ITEMS_PER_PAGE));
  const validCurrentPage = Math.min(currentPage, totalPages);
  const currentProjects = projects;
  const startIndex = totalCount === 0 ? 0 : (validCurrentPage - 1) * ITEMS_PER_PAGE + 1;
  const endIndex = Math.min((validCurrentPage - 1) * ITEMS_PER_PAGE + currentProjects.length, totalCount);

  // Multi-select handlers for current page
  const isCurrentPageAllSelected =
    currentProjects.length > 0 && currentProjects.every((p) => selectedIds.includes(p.id));

  const handleSelectAllCurrentPage = (e) => {
    if (e.target.checked) {
      const pageIds = currentProjects.map((p) => p.id);
      setSelectedIds((prev) => Array.from(new Set([...prev, ...pageIds])));
    } else {
      const pageIds = new Set(currentProjects.map((p) => p.id));
      setSelectedIds((prev) => prev.filter((id) => !pageIds.has(id)));
    }
  };

  const handleToggleSelect = (id, e) => {
    e.stopPropagation();
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const promptDeleteSingle = (p, e) => {
    e.stopPropagation();
    setConfirmModal({
      open: true,
      title: 'Confirm Project Deletion',
      message: `Are you sure you want to delete project "${p.title}" (ID: ${p.id})? This will permanently delete database records and associated Cloudflare R2 media files.`,
      itemsToDelete: [p.id],
    });
  };

  const promptDeleteSelected = () => {
    if (selectedIds.length === 0) return;
    setConfirmModal({
      open: true,
      title: `Confirm Batch Deletion (${selectedIds.length} Projects)`,
      message: `Are you sure you want to delete ${selectedIds.length} selected project(s)? This will permanently purge database records and R2 storage objects for all selected items.`,
      itemsToDelete: selectedIds,
    });
  };

  const executeDelete = async () => {
    const ids = confirmModal.itemsToDelete;
    setConfirmModal((prev) => ({ ...prev, open: false }));
    setLoading(true);
    try {
      if (ids.length === 1) {
        await projectsApi.delete(ids[0]);
      } else {
        await projectsApi.batchDelete(ids);
      }
      setSelectedIds([]);
      await loadData();
    } catch (err) {
      alert('❌ Failed to delete projects: ' + (err.message || 'Unknown error'));
      await loadData();
    }
  };

  const getStatusBadge = (p) => {
    const status = p.status || p.workflow_status;
    switch (status) {
      case 'completed':
        return <span className="badge badge-success">✓ Completed</span>;
      case 'failed':
        return <span className="badge badge-danger">❌ Failed</span>;
      case 'interrupted':
        return <span className="badge badge-warning">⚠️ Interrupted</span>;
      case 'segment_editing':
        return <span className="badge badge-warning">✏️ Edit Segments</span>;
      case 'generating_tts':
      case 'syncing_audio':
      case 'rendering':
      case 'generating_audio':
      case 'generating_video':
        return (
          <span className="badge badge-info">
            ⏳ Processing ({Math.round(p.progress || 0)}%)
          </span>
        );
      default:
        return <span className="badge badge-neutral">{status}</span>;
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">Projects Dashboard</h1>
          <p className="page-subtitle">Laragon MySQL Database & Persistent Local Media Storage</p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          {selectedIds.length > 0 && (
            <button className="btn btn-danger" onClick={promptDeleteSelected}>
              🗑️ Delete Selected ({selectedIds.length})
            </button>
          )}

        </div>
      </div>

      {/* Interrupted Projects Banner */}
      {interrupted.length > 0 && (
        <div className="banner banner-warning">
          <div>
            <strong>⚠️ Interrupted Projects Detected!</strong>
            <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>
              The following project(s) were stopped mid-workflow. You can resume without losing progress.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {interrupted.map((p) => (
              <button
                key={p.id}
                className="btn btn-secondary"
                onClick={() => onSelectProject(p)}
              >
                Resume "{p.title}"
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Projects List */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-color)', margin: 0 }}>
          <span>All Projects ({projects.length})</span>
          {selectedIds.length > 0 && (
            <span style={{ fontSize: '0.85rem', color: 'var(--accent-color)' }}>
              {selectedIds.length} of {projects.length} selected
            </span>
          )}
        </div>

        {loading ? (
          <div style={{ padding: '1.5rem 1rem' }}>
            <LoadingSpinner size="md" label="Đang tải danh sách dự án..." sublabel="Đang đồng bộ từ MySQL & Local Disk Storage..." />
            <div style={{ marginTop: '1.5rem' }}>
              <SkeletonLoader type="card" rows={3} />
            </div>
          </div>
        ) : projects.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              No projects in database. Start by creating a project or translating a video!
            </p>

          </div>
        ) : (
          <>
            <table className="table">
              <thead>
                <tr>
                  <th style={{ width: '40px' }}>
                    <input
                      type="checkbox"
                      checked={isCurrentPageAllSelected}
                      onChange={handleSelectAllCurrentPage}
                      title="Select All Projects on Current Page"
                    />
                  </th>
                  <th>Title / Name</th>
                  <th>Type</th>
                  <th>Job ID</th>
                  <th>Segments</th>
                  <th>Status & Progress</th>
                  <th>Created</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {currentProjects.map((p) => {
                  const isSelected = selectedIds.includes(p.id);
                  return (
                    <tr
                      key={p.id}
                      onClick={() => onSelectProject(p)}
                      style={{
                        cursor: 'pointer',
                        backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                      }}
                    >
                      <td onClick={(e) => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={(e) => handleToggleSelect(p.id, e)}
                        />
                      </td>
                      <td style={{ fontWeight: '600' }}>
                        {p.title}
                        {p.output_video_url && (
                          <div style={{ fontSize: '0.75rem', color: '#10b981', marginTop: '2px' }}>
                            🎥 Final Media Ready
                          </div>
                        )}
                      </td>
                      <td>
                        {p.type === 'video_translator' ? (
                          <span className="badge" style={{ backgroundColor: 'rgba(139, 92, 246, 0.2)', color: '#a78bfa' }}>
                            🌐 Video Translator
                          </span>
                        ) : (
                          <span className="badge" style={{ backgroundColor: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa' }}>
                            🎬 Script to Video
                          </span>
                        )}
                      </td>
                      <td style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        {p.id}
                      </td>
                      <td>{p.segment_count || 0}</td>
                      <td>
                        <div>{getStatusBadge(p)}</div>
                        {p.progress > 0 && p.progress < 100 && (
                          <div style={{ width: '100px', height: '4px', backgroundColor: '#374151', borderRadius: '2px', marginTop: '4px', overflow: 'hidden' }}>
                            <div style={{ width: `${p.progress}%`, height: '100%', backgroundColor: '#6366f1' }} />
                          </div>
                        )}
                      </td>
                      <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                        {p.created_at ? new Date(p.created_at).toLocaleDateString() : 'N/A'}
                      </td>
                      <td style={{ textAlign: 'right' }} onClick={(e) => e.stopPropagation()}>
                        {p.output_video_url && (
                          <a
                            href={p.output_video_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn btn-secondary"
                            style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem', marginRight: '0.4rem', textDecoration: 'none' }}
                            title="View / Download Final Video"
                          >
                            🎥 View
                          </a>
                        )}
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem', marginRight: '0.4rem' }}
                          onClick={(e) => promptEditTitle(p, e)}
                          title="Đổi tên dự án"
                        >
                          ✏️ Sửa tên
                        </button>
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem', marginRight: '0.4rem' }}
                          onClick={() => onSelectProject(p)}
                        >
                          Open
                        </button>
                        <button
                          className="btn btn-danger"
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem' }}
                          onClick={(e) => promptDeleteSingle(p, e)}
                        >
                          Delete
                        </button>

                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {/* Pagination Controls Bar */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.875rem 1.5rem', borderTop: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)' }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Hiển thị <strong>{startIndex}</strong> - <strong>{endIndex}</strong> trong tổng số <strong>{totalCount}</strong> dự án (8 dự án/trang)
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <button
                  className="btn btn-secondary"
                  style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
                  disabled={validCurrentPage === 1}
                  onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                >
                  ◀ Trang trước
                </button>

                {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    style={{
                      padding: '0.35rem 0.7rem',
                      fontSize: '0.8rem',
                      borderRadius: '6px',
                      border: pageNum === validCurrentPage ? '1px solid #6366f1' : '1px solid #374151',
                      backgroundColor: pageNum === validCurrentPage ? '#6366f1' : '#1f2937',
                      color: '#fff',
                      fontWeight: pageNum === validCurrentPage ? 'bold' : 'normal',
                      cursor: 'pointer',
                    }}
                  >
                    {pageNum}
                  </button>
                ))}

                <button
                  className="btn btn-secondary"
                  style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
                  disabled={validCurrentPage === totalPages}
                  onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                >
                  Trang sau ▶
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Confirmation Modal */}
      {confirmModal.open && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
          }}
        >
          <div
            style={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              padding: '1.5rem',
              maxWidth: '480px',
              width: '90%',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
            }}
          >
            <h3 style={{ marginTop: 0, color: '#f3f4f6' }}>{confirmModal.title}</h3>
            <p style={{ color: '#9ca3af', fontSize: '0.95rem', marginBottom: '1.5rem' }}>
              {confirmModal.message}
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button
                className="btn btn-secondary"
                onClick={() => setConfirmModal((prev) => ({ ...prev, open: false }))}
              >
                Cancel
              </button>
              <button className="btn btn-danger" onClick={executeDelete}>
                Yes, Delete Permanently
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Project Title Modal */}
      {editModal.open && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
          }}
        >
          <div
            style={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              padding: '1.5rem',
              maxWidth: '480px',
              width: '90%',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
            }}
          >
            <h3 style={{ marginTop: 0, color: '#f3f4f6' }}>✏️ Chỉnh sửa tên dự án</h3>
            <p style={{ color: '#9ca3af', fontSize: '0.85rem', margin: '0.5rem 0 1rem 0' }}>
              Nhập tên mới cho dự án (ID: <code>{editModal.projectId}</code>):
            </p>
            <input
              type="text"
              value={editingTitleValue}
              onChange={(e) => setEditingTitleValue(e.target.value)}
              placeholder="Tên dự án..."
              autoFocus
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '6px',
                border: '1px solid #4b5563',
                backgroundColor: '#111827',
                color: '#fff',
                fontSize: '14px',
                marginBottom: '1.25rem',
                boxSizing: 'border-box',
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSaveProjectTitle();
                if (e.key === 'Escape') setEditModal({ open: false, projectId: null, currentTitle: '' });
              }}
            />
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button
                className="btn btn-secondary"
                onClick={() => setEditModal({ open: false, projectId: null, currentTitle: '' })}
                disabled={savingTitle}
              >
                Hủy
              </button>
              <button
                className="btn btn-primary"
                onClick={handleSaveProjectTitle}
                disabled={savingTitle || !editingTitleValue.trim()}
              >
                {savingTitle ? '⏳ Đang lưu...' : '💾 Lưu tên mới'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
