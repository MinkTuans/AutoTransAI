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
    <div className="page-shell">
      <div className="page-header">
        <div>
          <h1 className="page-title">Dự án</h1>
          <p className="page-subtitle">Mở studio, theo dõi tiến độ, đổi tên hoặc xóa dự án đã lưu.</p>
        </div>
        <div className="inline-row">
          {selectedIds.length > 0 && (
            <button className="btn btn-danger" onClick={promptDeleteSelected}>
              Xóa {selectedIds.length} mục đã chọn
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

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="card-header" style={{ margin: 0, padding: '1rem 1.2rem' }}>
          <h2 className="card-title">Tất cả dự án ({totalCount})</h2>
          <label className="inline-row" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <input
              type="checkbox"
              checked={isCurrentPageAllSelected}
              onChange={handleSelectAllCurrentPage}
              title="Chọn tất cả trên trang này"
              style={{ width: 'auto' }}
            />
            Chọn trang này
            {selectedIds.length > 0 && <span>· {selectedIds.length} đã chọn</span>}
          </label>
        </div>

        {loading ? (
          <div style={{ padding: '1.5rem 1rem' }}>
            <LoadingSpinner size="md" label="Đang tải danh sách dự án..." sublabel="Đồng bộ từ database và ổ đĩa local..." />
            <div style={{ marginTop: '1.5rem' }}>
              <SkeletonLoader type="card" rows={3} />
            </div>
          </div>
        ) : projects.length === 0 ? (
          <div className="empty-state">
            <p>Chưa có dự án. Vào Studio để dịch video hoặc tạo dự án mới.</p>
          </div>
        ) : (
          <>
            <div className="project-grid">
              {currentProjects.map((p) => {
                const isSelected = selectedIds.includes(p.id);
                return (
                  <article
                    key={p.id}
                    className={`project-card ${isSelected ? 'is-selected' : ''}`}
                    onClick={() => onSelectProject(p)}
                  >
                    <div className="project-card-top">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => handleToggleSelect(p.id, e)}
                        onClick={(e) => e.stopPropagation()}
                        style={{ width: 'auto' }}
                      />
                      {p.type === 'video_translator' ? (
                        <span className="badge badge-purple">Dịch video</span>
                      ) : (
                        <span className="badge badge-info">Script</span>
                      )}
                    </div>
                    <h3 className="project-card-title">{p.title}</h3>
                    {p.output_video_url && <div className="project-card-ready">Video đã sẵn sàng</div>}
                    <div className="project-card-meta">{p.id}</div>
                    <div className="inline-row">
                      {getStatusBadge(p)}
                      <span className="project-card-meta">{p.segment_count || 0} đoạn</span>
                      <span className="project-card-meta">
                        {p.created_at ? new Date(p.created_at).toLocaleDateString('vi-VN') : ''}
                      </span>
                    </div>
                    {p.progress > 0 && p.progress < 100 && (
                      <div className="progress-bar-bg">
                        <div className="progress-bar-fill" style={{ width: `${p.progress}%` }} />
                      </div>
                    )}
                    <div className="project-card-actions" onClick={(e) => e.stopPropagation()}>
                      <button type="button" className="btn btn-primary btn-sm" onClick={() => onSelectProject(p)}>
                        Mở
                      </button>
                      <button type="button" className="btn btn-secondary btn-sm" onClick={(e) => promptEditTitle(p, e)}>
                        Đổi tên
                      </button>
                      {p.output_video_url && (
                        <a
                          href={p.output_video_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn btn-secondary btn-sm"
                        >
                          Xem
                        </a>
                      )}
                      <button type="button" className="btn btn-danger btn-sm" onClick={(e) => promptDeleteSingle(p, e)}>
                        Xóa
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>

            <div className="pagination-bar">
              <div className="page-subtitle" style={{ margin: 0 }}>
                {startIndex}–{endIndex} / {totalCount}
              </div>
              <div className="inline-row">
                <button
                  className="btn btn-secondary btn-sm"
                  disabled={validCurrentPage === 1}
                  onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                >
                  Trước
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
                  <button
                    key={pageNum}
                    type="button"
                    className={`page-num ${pageNum === validCurrentPage ? 'active' : ''}`}
                    onClick={() => setCurrentPage(pageNum)}
                  >
                    {pageNum}
                  </button>
                ))}
                <button
                  className="btn btn-secondary btn-sm"
                  disabled={validCurrentPage === totalPages}
                  onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                >
                  Sau
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Confirmation Modal */}
      {confirmModal.open && (
        <div className="modal-backdrop">
          <div className="modal-dialog">
            <div className="modal-header">
              <h3>{confirmModal.title}</h3>
            </div>
            <div className="modal-body">
              <p className="page-subtitle">{confirmModal.message}</p>
              <div className="modal-footer">
                <button
                  className="btn btn-secondary"
                  onClick={() => setConfirmModal((prev) => ({ ...prev, open: false }))}
                >
                  Hủy
                </button>
                <button className="btn btn-danger" onClick={executeDelete}>
                  Xóa vĩnh viễn
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Project Title Modal */}
      {editModal.open && (
        <div className="modal-backdrop">
          <div className="modal-dialog">
            <div className="modal-header">
              <h3>Đổi tên dự án</h3>
            </div>
            <div className="modal-body">
              <p className="page-subtitle">
                ID: <code>{editModal.projectId}</code>
              </p>
              <input
                type="text"
                value={editingTitleValue}
                onChange={(e) => setEditingTitleValue(e.target.value)}
                placeholder="Tên dự án..."
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSaveProjectTitle();
                  if (e.key === 'Escape') setEditModal({ open: false, projectId: null, currentTitle: '' });
                }}
              />
              <div className="modal-footer">
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
                  {savingTitle ? 'Đang lưu...' : 'Lưu tên'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
