import React, { useState, useEffect, useRef } from 'react';
import { videoTranslatorApi, providersApi, projectsApi } from '../api';
import VideoEditorStudio from '../components/VideoEditorStudio';
import AIQCScorecard from '../components/AIQCScorecard';
import YouTubePublisherModal from '../components/YouTubePublisherModal';
import WorkflowTimeline from '../components/WorkflowTimeline';
import ProjectGlossaryManager from '../components/ProjectGlossaryManager';
import { LoadingSpinner, ButtonSpinner } from '../components/LoadingSpinner';

function CollapsibleCard({ title, icon, defaultOpen = true, children, extraHeaderRight }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="card" style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', marginBottom: '20px', overflow: 'hidden' }}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        style={{
          padding: '14px 18px',
          background: '#0f172a',
          cursor: 'pointer',
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center',
          userSelect: 'none',
          borderBottom: isOpen ? '1px solid #334155' : 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '18px' }}>{icon}</span>
          <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 'bold', color: '#f8fafc' }}>{title}</h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {extraHeaderRight && <div onClick={(e) => e.stopPropagation()}>{extraHeaderRight}</div>}
          <span style={{ fontSize: '12px', color: '#94a3b8', background: '#1e293b', padding: '4px 8px', borderRadius: '6px', fontWeight: 'bold', border: '1px solid #334155' }}>
            {isOpen ? '▲ Thu gọn' : '▼ Mở rộng'}
          </span>
        </div>
      </div>
      {isOpen && <div style={{ padding: '16px 18px' }}>{children}</div>}
    </div>
  );
}

export default function VideoTranslator({ initialJobId, initialProjectId, onProcessingStateChange }) {
  const [showYouTubeModal, setShowYouTubeModal] = useState(false);
  const [inputMode, setInputMode] = useState('url');
  const [videoUrl, setVideoUrl] = useState('');
  const [uploadFile, setUploadFile] = useState(null);

  // Status & Metadata
  const [isCheckingUrl, setIsCheckingUrl] = useState(false);
  const [urlMetadata, setUrlMetadata] = useState(null);
  const [checkError, setCheckError] = useState(null);

  // Config options
  const [sourceLanguage, setSourceLanguage] = useState('auto');
  const [targetLanguage, setTargetLanguage] = useState('vi');
  const [audioProviderId, setAudioProviderId] = useState('edge_tts');
  const [llmProviderId, setLlmProviderId] = useState('gemini');
  const [sttModel, setSttModel] = useState('gemini-2.0-flash');
  const [voices, setVoices] = useState([]);
  const [voiceId, setVoiceId] = useState('vi-VN-HoaiMyNeural');
  const [originalAudioMode, setOriginalAudioMode] = useState('mute');
  const [originalAudioVolume, setOriginalAudioVolume] = useState(0.20);
  const [autoConfirmTranslation, setAutoConfirmTranslation] = useState(true);

  // Watermark Settings State
  const [watermarkEnabled, setWatermarkEnabled] = useState(false);
  const [watermarkType, setWatermarkType] = useState('image');
  const [watermarkImagePath, setWatermarkImagePath] = useState('');
  const [watermarkImageAssetId, setWatermarkImageAssetId] = useState(null);
  const [watermarkImagePreview, setWatermarkImagePreview] = useState('');
  const [watermarkText, setWatermarkText] = useState('© AutoTransAI Studio');
  const [watermarkPosition, setWatermarkPosition] = useState('bottom_right');
  const [watermarkScale, setWatermarkScale] = useState(0.20);
  const [watermarkOpacity, setWatermarkOpacity] = useState(0.80);
  const [watermarkMargin, setWatermarkMargin] = useState(20);
  const [watermarkFontSize, setWatermarkFontSize] = useState(32);
  const [isUploadingLogo, setIsUploadingLogo] = useState(false);
  const [watermarkValidationError, setWatermarkValidationError] = useState('');
  const [showWatermarkDetails, setShowWatermarkDetails] = useState(false);

  // AI Thumbnail Settings State
  const [thumbnailEnabled, setThumbnailEnabled] = useState(false);
  const [thumbnailProvider, setThumbnailProvider] = useState('pollinations');
  const [thumbnailModel, setThumbnailModel] = useState('default');
  const [thumbnailStyle, setThumbnailStyle] = useState('auto');
  const [thumbnailInstruction, setThumbnailInstruction] = useState('');

  // Project Management & Pre-flight State
  const [projectsList, setProjectsList] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(initialProjectId || null);
  const [savedProjectSettings, setSavedProjectSettings] = useState(null);
  const [isSettingsDirty, setIsSettingsDirty] = useState(false);
  const [isSavingSettings, setIsSavingSettings] = useState(false);

  // Modals & Switch Project Guard
  const [showNoProjectModal, setShowNoProjectModal] = useState(false);
  const [showCreateProjectModal, setShowCreateProjectModal] = useState(false);
  const [newProjectTitle, setNewProjectTitle] = useState('');
  const [newProjectDescription, setNewProjectDescription] = useState('');
  const [isCreatingProject, setIsCreatingProject] = useState(false);

  const [showEditTitleModal, setShowEditTitleModal] = useState(false);
  const [editTitleInput, setEditTitleInput] = useState('');
  const [isSavingTitle, setIsSavingTitle] = useState(false);

  const handleOpenEditTitleModal = () => {
    if (!selectedProjectId) return;
    const currentProj = projectsList.find(p => p.id === selectedProjectId);
    const titleToEdit = currentProj?.title || job?.asset?.title || '';
    setEditTitleInput(titleToEdit);
    setShowEditTitleModal(true);
  };

  const handleSaveProjectTitleInStudio = async () => {
    if (!selectedProjectId || !editTitleInput.trim()) return;
    setIsSavingTitle(true);
    try {
      const res = await projectsApi.update(selectedProjectId, { title: editTitleInput.trim() });
      if (res.success) {
        setShowEditTitleModal(false);
        await fetchProjectsList();
        if (job) {
          setJob(prev => prev ? { ...prev, asset: { ...prev.asset, title: editTitleInput.trim() } } : prev);
        }
      } else {
        alert('Không thể cập nhật tên dự án: ' + (res.message || 'Lỗi không xác định'));
      }
    } catch (err) {
      alert('Lỗi khi cập nhật tên dự án: ' + formatApiError(err, 'Lỗi hệ thống'));
    } finally {
      setIsSavingTitle(false);
    }
  };


  const [showPreflightModal, setShowPreflightModal] = useState(false);
  const [isPreflighting, setIsPreflighting] = useState(false);
  const [preflightResult, setPreflightResult] = useState(null);

  const [showSwitchGuardModal, setShowSwitchGuardModal] = useState(false);
  const [pendingSwitchProjectId, setPendingSwitchProjectId] = useState(null);

  const getCurrentSettingsObject = () => ({
    input_mode: inputMode,
    video_url: videoUrl,
    source_language: sourceLanguage,
    target_language: targetLanguage,
    stt_provider_id: llmProviderId,
    stt_model: sttModel,
    llm_provider_id: llmProviderId,
    translation_provider_id: llmProviderId,
    translation_model: sttModel,
    audio_provider_id: audioProviderId,
    voice_id: voiceId,
    original_audio_mode: originalAudioMode,
    original_audio_volume: originalAudioVolume,
    auto_confirm_translation: autoConfirmTranslation,
    watermark_enabled: watermarkEnabled,
    watermark_type: watermarkType,
    watermark_image_path: watermarkImagePath,
    watermark_image_asset_id: watermarkImageAssetId,
    watermark_text: watermarkText,
    watermark_position: watermarkPosition,
    watermark_scale: watermarkScale,
    watermark_opacity: watermarkOpacity,
    watermark_margin: watermarkMargin,
    watermark_font_size: watermarkFontSize,
    thumbnail_enabled: thumbnailEnabled,
    thumbnail_provider: thumbnailProvider,
    thumbnail_model: thumbnailModel,
    thumbnail_style: thumbnailStyle,
    thumbnail_custom_instruction: thumbnailInstruction,
  });

  const handleLogoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setWatermarkValidationError('');
    setIsUploadingLogo(true);
    try {
      const res = await videoTranslatorApi.uploadWatermarkLogo(file, selectedProjectId);
      if (res.success && res.data) {
        const imgPath = res.data.image_path;
        setWatermarkImagePath(imgPath);
        if (res.data.asset_id) setWatermarkImageAssetId(res.data.asset_id);
        const urlStr = res.data.url || URL.createObjectURL(file);
        setWatermarkImagePreview(urlStr);

        if (selectedProjectId && selectedProjectId !== 'default_project') {
          const currentConfig = getCurrentSettingsObject();
          currentConfig.watermark_image_path = imgPath;
          currentConfig.watermark_enabled = true;
          currentConfig.watermark_type = 'image';
          projectsApi.saveSettings(selectedProjectId, currentConfig).then(saveRes => {
            if (saveRes.success && saveRes.data) {
              setSavedProjectSettings(saveRes.data);
              setIsSettingsDirty(false);
            }
          }).catch(() => { });
        }
      }
    } catch (err) {
      setWatermarkValidationError('Lỗi upload logo: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsUploadingLogo(false);
    }
  };

  // Job execution state
  const [asset, setAsset] = useState(null);
  const [job, setJob] = useState(null);
  const [segments, setSegments] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [pipelineError, setPipelineError] = useState(null);

  // Workflow engine state & actions
  const [workflowStatusData, setWorkflowStatusData] = useState(null);
  const [loadingWorkflowAction, setLoadingWorkflowAction] = useState(null);

  // Handle browser tab close/refresh guard & notify parent App
  useEffect(() => {
    const isRunning = isProcessing || (workflowStatusData && ['running', 'processing'].includes(workflowStatusData.status));

    if (onProcessingStateChange) {
      onProcessingStateChange(Boolean(isRunning));
    }

    if (!isRunning) return;

    const handleBeforeUnload = (e) => {
      e.preventDefault();
      const msg = '⚠️ Tiến trình dịch video đang chạy! Nếu bạn đóng hoặc tải lại trang, quá trình theo dõi real-time có thể bị ngắt quãng. Bạn có chắc chắn muốn rời đi?';
      e.returnValue = msg;
      return msg;
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isProcessing, workflowStatusData?.status, onProcessingStateChange]);

  const activeProjectId = selectedProjectId || job?.project_id || asset?.project_id || (job?.id && job.id !== 'default_project' ? job.id : null);

  // Load Projects List
  const fetchProjectsList = async () => {
    try {
      const res = await projectsApi.list(1, 100);
      if (res.success && Array.isArray(res.data)) {
        setProjectsList(res.data);
      }
    } catch (err) {
      console.error('Failed fetching projects list', err);
    }
  };

  useEffect(() => {
    fetchProjectsList();
  }, []);

  const parseBool = (val, defaultVal = false) => {
    if (val === null || val === undefined) return defaultVal;
    if (typeof val === 'boolean') return val;
    if (typeof val === 'number') return val !== 0;
    if (typeof val === 'string') {
      const clean = val.trim().toLowerCase();
      if (clean === 'true' || clean === '1' || clean === 'yes' || clean === 'on') return true;
      if (clean === 'false' || clean === '0' || clean === 'no' || clean === 'off') return false;
    }
    return Boolean(val);
  };

  const hydrateSettings = (cfg) => {
    setSavedProjectSettings(cfg);
    if (cfg.input_mode) setInputMode(cfg.input_mode);
    if (cfg.video_url !== undefined) setVideoUrl(cfg.video_url);
    if (cfg.source_language) setSourceLanguage(cfg.source_language);
    if (cfg.target_language) setTargetLanguage(cfg.target_language);
    if (cfg.audio_provider_id) setAudioProviderId(cfg.audio_provider_id);
    if (cfg.llm_provider_id) setLlmProviderId(cfg.llm_provider_id);
    if (cfg.stt_model) setSttModel(cfg.stt_model);
    if (cfg.voice_id) setVoiceId(cfg.voice_id);
    if (cfg.original_audio_mode) setOriginalAudioMode(cfg.original_audio_mode);
    if (cfg.original_audio_volume !== undefined) setOriginalAudioVolume(cfg.original_audio_volume);
    setAutoConfirmTranslation(parseBool(cfg.auto_confirm_translation, true));

    setWatermarkEnabled(parseBool(cfg.watermark_enabled, false));
    setWatermarkType(cfg.watermark_type || 'image');
    setWatermarkImagePath(cfg.watermark_image_path || '');
    setWatermarkImageAssetId(cfg.watermark_image_asset_id || null);
    if (cfg.watermark_image_path) {
      const rel = cfg.watermark_image_path.replace(/\\/g, '/');
      setWatermarkImagePreview(rel.startsWith('http') || rel.startsWith('blob:') ? rel : `/api/storage/files/${rel}`);
    } else {
      setWatermarkImagePreview('');
    }
    setWatermarkText(cfg.watermark_text || '© AutoTransAI Studio');
    setWatermarkPosition(cfg.watermark_position || 'bottom_right');
    setWatermarkScale(cfg.watermark_scale !== undefined ? cfg.watermark_scale : 0.20);
    setWatermarkOpacity(cfg.watermark_opacity !== undefined ? cfg.watermark_opacity : 0.80);
    setWatermarkMargin(cfg.watermark_margin !== undefined ? cfg.watermark_margin : 20);
    setWatermarkFontSize(cfg.watermark_font_size !== undefined ? cfg.watermark_font_size : 32);

    setThumbnailEnabled(parseBool(cfg.thumbnail_enabled, false));
    setThumbnailProvider(cfg.thumbnail_provider || 'pollinations');
    setThumbnailModel(cfg.thumbnail_model || 'default');
    setThumbnailStyle(cfg.thumbnail_style || 'auto');
    setThumbnailInstruction(cfg.thumbnail_custom_instruction || '');

    setIsSettingsDirty(false);
  };

  useEffect(() => {
    if (!selectedProjectId || selectedProjectId === 'default_project') return;

    projectsApi.getSettings(selectedProjectId).then(res => {
      if (res.success && (res.data || res.settings)) {
        const cfg = res.data || res.settings;
        hydrateSettings(cfg);
      }
    }).catch(err => console.error('Failed loading project settings', err));

    fetchWorkflowStatus(selectedProjectId);
  }, [selectedProjectId]);

  useEffect(() => {
    if (!savedProjectSettings || !selectedProjectId) {
      setIsSettingsDirty(false);
      return;
    }
    const current = getCurrentSettingsObject();
    const compareKeys = [
      'target_language', 'source_language', 'audio_provider_id', 'llm_provider_id',
      'stt_model', 'voice_id', 'original_audio_mode', 'original_audio_volume', 'auto_confirm_translation',
      'watermark_enabled', 'watermark_type', 'watermark_image_path', 'watermark_text',
      'watermark_position', 'watermark_scale', 'watermark_opacity', 'watermark_margin',
      'watermark_font_size', 'thumbnail_enabled', 'thumbnail_provider', 'thumbnail_model',
      'thumbnail_style', 'thumbnail_custom_instruction'
    ];

    let isDifferent = false;
    for (const key of compareKeys) {
      const curVal = current[key];
      const savedVal = savedProjectSettings[key];
      if (JSON.stringify(curVal) !== JSON.stringify(savedVal)) {
        isDifferent = true;
        break;
      }
    }

    setIsSettingsDirty(isDifferent);
  }, [
    selectedProjectId,
    targetLanguage,
    sourceLanguage,
    audioProviderId,
    llmProviderId,
    sttModel,
    voiceId,
    originalAudioMode,
    originalAudioVolume,
    autoConfirmTranslation,
    watermarkEnabled,
    watermarkType,
    watermarkImagePath,
    watermarkImageAssetId,
    watermarkText,
    watermarkPosition,
    watermarkScale,
    watermarkOpacity,
    watermarkMargin,
    watermarkFontSize,
    thumbnailEnabled,
    thumbnailProvider,
    thumbnailModel,
    thumbnailStyle,
    thumbnailInstruction,
    savedProjectSettings,
  ]);

  const handleSaveSettingsToProject = async () => {
    if (!selectedProjectId) return;
    setIsSavingSettings(true);
    try {
      const currentConfig = getCurrentSettingsObject();
      const res = await projectsApi.saveSettings(selectedProjectId, currentConfig);
      if (res.success && (res.data || res.settings)) {
        const savedData = res.data || res.settings;
        setSavedProjectSettings(savedData);
        setIsSettingsDirty(false);
      }
    } catch (err) {
      alert('Không thể lưu cấu hình dự án: ' + formatApiError(err, 'Lỗi hệ thống'));
    } finally {
      setIsSavingSettings(false);
    }
  };

  const handleDiscardChanges = () => {
    if (savedProjectSettings) {
      hydrateSettings(savedProjectSettings);
    }
  };

  const handleProjectSelectAttempt = (targetId) => {
    if (targetId === selectedProjectId) return;
    if (isSettingsDirty) {
      setPendingSwitchProjectId(targetId);
      setShowSwitchGuardModal(true);
    } else {
      setSelectedProjectId(targetId);
    }
  };

  const fetchWorkflowStatus = async (targetProjId) => {
    const projId = targetProjId || activeProjectId;
    if (!projId || projId === 'default_project') return;
    try {
      const res = await videoTranslatorApi.getWorkflowStatus(projId);
      if (res.success) {
        setWorkflowStatusData(res.data);
      }
    } catch (err) {
      console.error('Failed fetching workflow status', err);
    }
  };

  // SSE Real-time workflow status updates
  useEffect(() => {
    if (!activeProjectId || activeProjectId === 'default_project') return;

    fetchWorkflowStatus(activeProjectId);

    let eventSource = null;
    let retryTimeout = null;

    const connectSSE = () => {
      const sseUrl = `http://127.0.0.1:8000/api/projects/${activeProjectId}/workflow-stream`;
      eventSource = new EventSource(sseUrl);

      eventSource.onmessage = (event) => {
        try {
          if (event.data === 'ping') return;
          const payload = JSON.parse(event.data);
          if (payload && payload.type === 'workflow_update') {
            fetchWorkflowStatus(activeProjectId);
          }
        } catch (err) {
          console.error("SSE parse error", err);
        }
      };

      eventSource.onerror = (err) => {
        console.error("SSE Connection Error", err);
        eventSource.close();
        retryTimeout = setTimeout(connectSSE, 5000);
      };
    };

    connectSSE();

    return () => {
      if (eventSource) eventSource.close();
      if (retryTimeout) clearTimeout(retryTimeout);
    };
  }, [activeProjectId]);

  const handleOpenPreflightOrPromptProject = async () => {
    if (!activeProjectId || activeProjectId === 'default_project') {
      setShowNoProjectModal(true);
      return;
    }
    runPreflightCheck(activeProjectId);
  };

  const runPreflightCheck = async (targetProjId) => {
    const projId = targetProjId || activeProjectId;
    if (!projId || projId === 'default_project') return;

    setIsPreflighting(true);
    setShowPreflightModal(true);
    try {
      const payload = {
        video_url: inputMode === 'url' ? videoUrl : null,
        video_path: asset?.file_path || asset?.video_path || null,
        has_upload_file: inputMode === 'upload' && Boolean(uploadFile),
        target_language: targetLanguage,
        audio_provider_id: audioProviderId,
        llm_provider_id: llmProviderId,
        voice_id: voiceId,
        watermark_enabled: watermarkEnabled,
        watermark_type: watermarkType,
        watermark_image_path: watermarkImagePath,
        watermark_text: watermarkText,
        watermark_position: watermarkPosition,
        watermark_scale: watermarkScale,
        watermark_opacity: watermarkOpacity,
        watermark_margin: watermarkMargin,
        watermark_font_size: watermarkFontSize,
      };

      const res = await videoTranslatorApi.preflightWorkflow(projId, payload);
      if (res.success) {
        setPreflightResult(res.data);
      }
    } catch (err) {
      alert('Không thể thực hiện Pre-flight check: ' + formatApiError(err, 'Lỗi hệ thống'));
    } finally {
      setIsPreflighting(false);
    }
  };

  const executeStartWorkflowAfterPreflight = async () => {
    setShowPreflightModal(false);
    setLoadingWorkflowAction('start');
    setIsProcessing(true);
    setPipelineError(null);
    setWorkflowStatusData(prev => ({
      ...(prev || {}),
      status: 'running',
      current_stage: 'INGEST',
      current_step: 'Đang khởi chạy workflow...',
      overall_progress_pct: 0,
      stages: [
        { name: 'INGEST', status: 'running' },
        { name: 'ANALYZE', status: 'pending' },
        { name: 'TRANSLATE', status: 'pending' },
        { name: 'DUB', status: 'pending' },
        { name: 'PRODUCE', status: 'pending' },
        { name: 'PUBLISH', status: 'pending' },
      ]
    }));
    if (!asset && ((inputMode === 'upload' && uploadFile) || (inputMode === 'url' && videoUrl))) {
      handleStartImportAndTranslation();
    } else {
      handleStartWorkflow();
    }
  };

  const handleCreateProjectSubmit = async (e) => {
    e.preventDefault();
    if (!newProjectTitle.trim()) return;

    setIsCreatingProject(true);
    try {
      const currentConfig = getCurrentSettingsObject();

      const res = await projectsApi.create({
        title: newProjectTitle,
        description: newProjectDescription,
        workflow_mode: 'video_translator',
        settings_json: currentConfig,
      });

      if (res.success && res.data) {
        const createdId = res.data.project_id || res.data.id;
        setSelectedProjectId(createdId);
        hydrateSettings(res.data.settings || currentConfig);
        setIsSettingsDirty(false);
        setShowCreateProjectModal(false);
        setShowNoProjectModal(false);
        setNewProjectTitle('');
        setNewProjectDescription('');
        await fetchProjectsList();
        runPreflightCheck(createdId);
      }
    } catch (err) {
      alert('Không thể tạo dự án mới: ' + formatApiError(err, 'Lỗi hệ thống'));
    } finally {
      setIsCreatingProject(false);
    }
  };

  const closeCreateProjectModalSafely = () => {
    if ((newProjectTitle.trim() || newProjectDescription.trim()) && !isCreatingProject) {
      if (window.confirm('⚠️ Bạn có dữ liệu tên/mô tả dự án chưa lưu! Bạn có chắc chắn muốn thoát không?')) {
        setNewProjectTitle('');
        setNewProjectDescription('');
        setShowCreateProjectModal(false);
      }
    } else {
      setShowCreateProjectModal(false);
    }
  };

  const handleStartWorkflow = async () => {
    if (!activeProjectId || activeProjectId === 'default_project') {
      setShowNoProjectModal(true);
      return;
    }
    setLoadingWorkflowAction('start');
    setIsProcessing(true);
    setPipelineError(null);
    try {
      const payload = {
        video_url: inputMode === 'url' ? videoUrl : null,
        video_path: asset?.file_path || asset?.video_path || null,
        target_language: targetLanguage,
        audio_provider_id: audioProviderId,
        llm_provider_id: llmProviderId,
        voice_id: voiceId,
        watermark_enabled: watermarkEnabled,
        watermark_type: watermarkType,
        watermark_image_path: watermarkImagePath,
        watermark_text: watermarkText,
        watermark_position: watermarkPosition,
        watermark_scale: watermarkScale,
        watermark_opacity: watermarkOpacity,
        watermark_margin: watermarkMargin,
        watermark_font_size: watermarkFontSize,
      };

      await videoTranslatorApi.startWorkflow(activeProjectId, payload);
      await fetchWorkflowStatus(activeProjectId);
    } catch (err) {
      alert('Không thể bắt đầu workflow: ' + formatApiError(err, 'Lỗi hệ thống'));
      setIsProcessing(false);
    } finally {
      setLoadingWorkflowAction(null);
    }
  };

  const handlePauseWorkflow = async () => {
    if (!activeProjectId) return;
    setLoadingWorkflowAction('pause');
    try {
      await videoTranslatorApi.pauseWorkflow(activeProjectId);
      await fetchWorkflowStatus(activeProjectId);
    } catch (err) {
      alert('Không thể tạm dừng workflow: ' + formatApiError(err, 'Lỗi hệ thống'));
    } finally {
      setLoadingWorkflowAction(null);
    }
  };

  const handleResumeWorkflow = async () => {
    if (!activeProjectId) return;
    setLoadingWorkflowAction('resume');
    try {
      await videoTranslatorApi.resumeWorkflow(activeProjectId);
      await fetchWorkflowStatus(activeProjectId);
    } catch (err) {
      alert('Không thể tiếp tục workflow: ' + formatApiError(err, 'Lỗi hệ thống'));
    } finally {
      setLoadingWorkflowAction(null);
    }
  };

  const handleCancelWorkflow = async () => {
    if (!activeProjectId) return;
    setLoadingWorkflowAction('cancel');
    try {
      await videoTranslatorApi.cancelWorkflow(activeProjectId);
      await fetchWorkflowStatus(activeProjectId);
    } catch (err) {
      alert('Không thể hủy workflow: ' + formatApiError(err, 'Lỗi hệ thống'));
    } finally {
      setLoadingWorkflowAction(null);
    }
  };

  const handleRetryStage = async (stageName) => {
    if (!activeProjectId) return;
    setLoadingWorkflowAction('retry');
    setIsProcessing(true);
    setPipelineError(null);

    try {
      if (activeJobId) {
        await videoTranslatorApi.retryJob(activeJobId);
      } else if (activeProjectId && activeProjectId !== 'default_project') {
        await videoTranslatorApi.retryStage(activeProjectId, stageName);
        await fetchWorkflowStatus(activeProjectId);
      }

      if (activeJobId) {
        const res = await videoTranslatorApi.getJob(activeJobId);
        if (res && res.success && res.data) {
          setJob({ ...res.data, id: res.data.id || res.data.job_id });
        }
      }
    } catch (err) {
      setPipelineError(`Không thể thử lại stage ${stageName}: ` + formatApiError(err, 'Lỗi hệ thống'));
      setIsProcessing(false);
    } finally {
      setLoadingWorkflowAction(null);
    }
  };

  const autoSaveTimerRef = useRef(null);

  useEffect(() => {
    if (initialJobId) {
      videoTranslatorApi.getStudioState(initialJobId).then(res => {
        if (res.success && res.data) {
          const { job: loadedJob, asset: loadedAsset, settings_snapshot, segments: loadedSegs } = res.data;
          setJob({ ...loadedJob, asset: loadedAsset || loadedJob?.asset });
          if (loadedSegs) setSegments(loadedSegs);
          if (settings_snapshot) {
            if (settings_snapshot.language?.source_language) setSourceLanguage(settings_snapshot.language.source_language);
            if (settings_snapshot.language?.target_language) setTargetLanguage(settings_snapshot.language.target_language);
            if (settings_snapshot.tts?.provider) setAudioProviderId(settings_snapshot.tts.provider);
            if (settings_snapshot.tts?.voice_id) setVoiceId(settings_snapshot.tts.voice_id);
            if (settings_snapshot.stt?.provider) setLlmProviderId(settings_snapshot.stt.provider);
            if (settings_snapshot.stt?.model) setSttModel(settings_snapshot.stt.model);
            if (settings_snapshot.audio_mix?.original_audio_mode) setOriginalAudioMode(settings_snapshot.audio_mix.original_audio_mode);
            if (settings_snapshot.watermark) {
              setWatermarkEnabled(settings_snapshot.watermark.enabled ?? false);
              setWatermarkType(settings_snapshot.watermark.type || 'image');
              setWatermarkImagePath(settings_snapshot.watermark.image_path || '');
              setWatermarkText(settings_snapshot.watermark.text || '');
              setWatermarkPosition(settings_snapshot.watermark.position || 'bottom_right');
              setWatermarkScale(settings_snapshot.watermark.scale ?? 0.20);
              setWatermarkOpacity(settings_snapshot.watermark.opacity ?? 0.80);
              setWatermarkMargin(settings_snapshot.watermark.margin ?? 20);
              setWatermarkFontSize(settings_snapshot.watermark.font_size ?? 32);
            }
          }
          fetchWorkflowStatus(loadedJob.project_id || loadedJob.id);
        }
      }).catch(err => console.error('Failed to load initial studio state:', err));
    }
  }, [initialJobId]);

  useEffect(() => {
    if (!job?.id || !segments || segments.length === 0) return;
    if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);

    autoSaveTimerRef.current = setTimeout(async () => {
      try {
        const updateItems = segments.map(s => ({ id: s.id, translated_text: s.translated_text }));
        await videoTranslatorApi.updateSegments(job.id, updateItems);
      } catch (e) {
        console.error('Autosave segments failed:', e);
      }
    }, 800);

    return () => {
      if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);
    };
  }, [segments, job?.id]);

  // Log Modal state
  const [showLogModal, setShowLogModal] = useState(false);
  const [logsContent, setLogsContent] = useState('');
  const [isFetchingLogs, setIsFetchingLogs] = useState(false);
  const [copySuccess, setCopySuccess] = useState('');

  // Polling ref & Timestamps
  const pollingRef = useRef(null);
  const [lastPollTime, setLastPollTime] = useState(null);
  const [lastApiResponseTime, setLastApiResponseTime] = useState(null);

  useEffect(() => {
    providersApi.listVoices(audioProviderId, targetLanguage)
      .then(res => {
        if (res.success && res.data) {
          setVoices(res.data);
          if (res.data.length > 0) {
            setVoiceId(res.data[0].id);
          }
        }
      })
      .catch(() => setVoices([]));
  }, [audioProviderId, targetLanguage]);

  const activeJobId = job?.id || job?.job_id;
  const lastPollTimestampRef = useRef(0);

  useEffect(() => {
    if (!activeJobId) return;

    if (['completed', 'failed', 'cancelled', 'segment_editing'].includes(job?.status)) {
      if (isProcessing) setIsProcessing(false);
    }

    const isFinalTerminal = ['completed', 'failed', 'cancelled'].includes(job?.status);
    if (isFinalTerminal) return;

    const fetchJobStatus = () => {
      const reqTimestamp = Date.now();
      const nowStr = new Date().toLocaleTimeString('vi-VN');
      setLastPollTime(nowStr);

      videoTranslatorApi.getJob(activeJobId)
        .then(res => {
          const respTimeStr = new Date().toLocaleTimeString('vi-VN');
          setLastApiResponseTime(respTimeStr);

          if (res.success && res.data) {
            const rawData = res.data;
            const newJob = {
              ...rawData,
              id: rawData.id || rawData.job_id,
            };

            if (reqTimestamp < lastPollTimestampRef.current) return;
            lastPollTimestampRef.current = reqTimestamp;

            setJob(prev => {
              if (prev && ['completed', 'failed', 'cancelled'].includes(prev.status)) {
                return prev;
              }
              return newJob;
            });

            if (newJob.segments && newJob.segments.length > 0) {
              setSegments(newJob.segments);
            }

            if (['completed', 'failed', 'cancelled', 'segment_editing'].includes(newJob.status)) {
              setIsProcessing(false);
            }

            if (['completed', 'failed', 'cancelled'].includes(newJob.status)) {
              if (pollingRef.current) clearInterval(pollingRef.current);
            }
          }
        })
        .catch(err => console.error('[JOB POLL ERROR]', err));
    };

    fetchJobStatus();
    fetchWorkflowStatus(activeProjectId);
    pollingRef.current = setInterval(() => {
      fetchJobStatus();
      fetchWorkflowStatus(activeProjectId);
    }, 1500);

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [activeJobId, activeProjectId, job?.status]);

  const formatApiError = (err, defaultMsg) => {
    const status = err.response?.status ? `[HTTP ${err.response.status}] ` : '';
    const method = err.config?.method ? err.config.method.toUpperCase() + ' ' : '';
    const serverDetail = err.response?.data?.detail;
    const errorMsg = err.response?.data?.error || err.message;

    let detailStr = '';
    if (serverDetail) {
      detailStr = typeof serverDetail === 'object' ? JSON.stringify(serverDetail, null, 2) : serverDetail;
    } else if (errorMsg) {
      detailStr = errorMsg;
    } else {
      detailStr = defaultMsg;
    }
    return `${status}${method} Lỗi: ${detailStr}`;
  };

  const fetchLogs = async (jobId) => {
    const targetId = jobId || activeJobId;
    if (!targetId) {
      setLogsContent(
        pipelineError
          ? `⚠️ Chưa có Job ID được gán.\n\n[Chi Tiết Lỗi Pipeline]:\n${pipelineError}`
          : 'Chưa có thông tin Job ID hoặc log execution.'
      );
      return;
    }
    setIsFetchingLogs(true);
    try {
      const res = await videoTranslatorApi.getLogs(targetId);
      if (res.success) {
        setLogsContent(res.data.logs || 'Chưa có dữ liệu log.');
      }
    } catch (err) {
      const errFormatted = formatApiError(err, 'Lỗi không thể lấy log từ server');
      setLogsContent(`Không thể tải log cho Job ID (${targetId}):\n${errFormatted}\n\n[Lỗi Pipeline]:\n${pipelineError || job?.error_message || 'N/A'}`);
    } finally {
      setIsFetchingLogs(false);
    }
  };

  const handleOpenLogs = () => {
    setShowLogModal(true);
    fetchLogs(activeJobId);
  };

  const handleCheckUrl = async () => {
    if (!videoUrl) return;
    setIsCheckingUrl(true);
    setCheckError(null);
    setUrlMetadata(null);
    try {
      const res = await videoTranslatorApi.checkUrl(videoUrl);
      if (res.success) {
        setUrlMetadata(res.data);
      }
    } catch (err) {
      setCheckError(formatApiError(err, 'Lỗi kiểm tra URL'));
    } finally {
      setIsCheckingUrl(false);
    }
  };

  const handleStartImportAndTranslation = async () => {
    setIsProcessing(true);
    setPipelineError(null);
    setJob(null);
    setSegments([]);

    try {
      let importedAsset;
      if (inputMode === 'upload') {
        if (!uploadFile) throw new Error('Vui lòng chọn file video.');
        const res = await videoTranslatorApi.importUpload(uploadFile);
        importedAsset = res.data;
      } else {
        if (!videoUrl) throw new Error('Vui lòng nhập URL video.');
        const res = await videoTranslatorApi.importUrl(videoUrl);
        importedAsset = res.data;
      }
      setAsset(importedAsset);

      if (watermarkEnabled) {
        if (watermarkType === 'image' && !watermarkImagePath) {
          setWatermarkValidationError('❌ Vui lòng upload logo ảnh trước khi bắt đầu.');
          setIsProcessing(false);
          return;
        }
        if (watermarkType === 'text' && !watermarkText.trim()) {
          setWatermarkValidationError('❌ Vui lòng nhập nội dung văn bản watermark.');
          setIsProcessing(false);
          return;
        }
      }
      setWatermarkValidationError('');

      const jobRes = await videoTranslatorApi.createJob({
        project_id: activeProjectId,
        asset_id: importedAsset.asset_id,
        source_language: 'auto',
        target_language: targetLanguage,
        audio_provider_id: audioProviderId,
        llm_provider_id: llmProviderId,
        voice_id: voiceId,
        original_audio_mode: originalAudioMode,
        auto_confirm_translation: autoConfirmTranslation,
        watermark_enabled: watermarkEnabled,
        watermark_type: watermarkType,
        watermark_image_path: watermarkImagePath,
        watermark_text: watermarkText,
        watermark_position: watermarkPosition,
        watermark_scale: watermarkScale,
        watermark_opacity: watermarkOpacity,
        watermark_margin: watermarkMargin,
        watermark_font_size: watermarkFontSize,
      });

      const newJobId = jobRes.data.job_id || jobRes.data.id;
      const realProjectId = jobRes.data.project_id || newJobId;

      const initialPendingJob = {
        id: newJobId,
        job_id: newJobId,
        project_id: realProjectId,
        status: 'created',
        stage: 'QUEUED',
        overall_progress_pct: 0,
        stage_progress_pct: 0,
        current_step: 'Đang bắt đầu pipeline...',
      };
      setJob(initialPendingJob);

      await videoTranslatorApi.startJob(newJobId);
      const initialJob = await videoTranslatorApi.getJob(newJobId);
      const normalizedInitial = {
        ...initialJob.data,
        id: initialJob.data.id || initialJob.data.job_id,
        project_id: initialJob.data.project_id || realProjectId,
      };
      setJob(normalizedInitial);
      if (normalizedInitial.segments && normalizedInitial.segments.length > 0) {
        setSegments(normalizedInitial.segments);
      }
    } catch (err) {
      const detail = formatApiError(err, 'Không thể bắt đầu dịch video');
      setPipelineError(detail);
      setIsProcessing(false);
    }
  };

  const handleSegmentTextChange = (segmentId, text) => {
    setSegments(prev => prev.map(s => s.id === segmentId ? { ...s, translated_text: text } : s));
  };

  const handleRenderFinalVideo = async () => {
    if (!activeJobId) return;
    setIsProcessing(true);
    setPipelineError(null);

    try {
      const updateItems = segments.map(s => ({ id: s.id, translated_text: s.translated_text }));
      await videoTranslatorApi.updateSegments(activeJobId, updateItems);
      await videoTranslatorApi.renderFinalVideo(activeJobId);
      const updatedJob = await videoTranslatorApi.getJob(activeJobId);
      const normalizedUpdated = {
        ...updatedJob.data,
        id: updatedJob.data.id || updatedJob.data.job_id,
      };
      setJob(normalizedUpdated);
    } catch (err) {
      const detail = formatApiError(err, 'Lỗi render video');
      setPipelineError(detail);
      setIsProcessing(false);
    }
  };

  const handleRetryJob = async () => {
    setPipelineError(null);
    setLoadingWorkflowAction('retry');
    setIsProcessing(true);

    const targetStage = workflowStatusData?.current_stage || 'INGEST';

    try {
      if (activeJobId) {
        await videoTranslatorApi.retryJob(activeJobId);
      } else if (activeProjectId && activeProjectId !== 'default_project') {
        await videoTranslatorApi.retryStage(activeProjectId, targetStage);
        await fetchWorkflowStatus(activeProjectId);
      }

      if (activeJobId) {
        const res = await videoTranslatorApi.getJob(activeJobId);
        if (res && res.success && res.data) {
          setJob({ ...res.data, id: res.data.id || res.data.job_id });
        }
      }
    } catch (err) {
      setPipelineError('Không thể thử lại job: ' + formatApiError(err, 'Lỗi hệ thống'));
      setIsProcessing(false);
    } finally {
      setLoadingWorkflowAction(null);
    }
  };

  const formatTime = (sec) => {
    if (!sec || isNaN(sec)) return '00:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="video-translator-studio">
      {/* Studio Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h1 style={{ fontSize: '22px', fontWeight: 'bold', margin: 0, color: '#818cf8', display: 'flex', alignItems: 'center', gap: '8px' }}>
            🎬 Video Translator – Studio Dịch & Lồng Tiếng
          </h1>
          <p style={{ color: '#94a3b8', margin: '2px 0 0 0', fontSize: '13px' }}>
            Tự động dịch giọng nói trong video với Unified 6-Stage Engine, realtime tracking & AI controls.
          </p>
        </div>

        {/* Project Selector Compact Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#1e1b4b', border: '1px solid #4338ca', padding: '6px 12px', borderRadius: '8px' }}>
          <span style={{ fontSize: '13px', fontWeight: 'bold', color: '#fff', whiteSpace: 'nowrap' }}>Dự án:</span>
          <select
            value={selectedProjectId || ''}
            onChange={(e) => handleProjectSelectAttempt(e.target.value || null)}
            style={{ padding: '6px 10px', borderRadius: '6px', background: '#0f1117', color: '#fff', border: '1px solid #4338ca', fontSize: '13px', minWidth: '180px' }}
          >
            <option value="">-- Chọn dự án --</option>
            {projectsList.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title} (ID: {p.id})
              </option>
            ))}
          </select>
          {selectedProjectId && (
            <button
              onClick={handleOpenEditTitleModal}
              title="Đổi tên dự án hiện tại"
              style={{ background: '#3730a3', color: '#e0e7ff', border: '1px solid #6366f1', padding: '6px 10px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '12px', whiteSpace: 'nowrap' }}
            >
              ✏️ Sửa tên
            </button>
          )}
          <button
            onClick={() => setShowCreateProjectModal(true)}
            style={{ background: '#4f46e5', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '12px', whiteSpace: 'nowrap' }}
          >
            ➕ Tạo mới
          </button>

        </div>
      </div>

      {/* Dirty Settings Warning Banner */}
      {isSettingsDirty && selectedProjectId && (
        <div style={{ background: '#1e3a8a', border: '1px solid #3b82f6', borderRadius: '8px', padding: '10px 16px', marginBottom: '14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#fff', flexWrap: 'wrap', gap: '10px', fontSize: '13px' }}>
          <span style={{ color: '#93c5fd', fontWeight: 'bold' }}>
            ⚠️ Bạn có thay đổi cấu hình dự án chưa lưu.
          </span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={handleSaveSettingsToProject}
              disabled={isSavingSettings}
              style={{ background: '#2563eb', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '12px' }}
            >
              {isSavingSettings ? 'Đang lưu DB...' : '💾 Lưu DB'}
            </button>
            <button
              onClick={handleDiscardChanges}
              style={{ background: '#475569', color: '#f8fafc', border: 'none', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '12px' }}
            >
              ↩️ Hủy
            </button>
          </div>
        </div>
      )}

      {/* MAIN 2-COLUMN STUDIO GRID */}
      <div className="translator-studio-grid">
        
        {/* LEFT PRIMARY COLUMN: PIPELINE + CONFIG */}
        <div className="studio-left-col">
          
          {/* Unified 6-Stage Workflow Pipeline Card */}
          <WorkflowTimeline
            projectId={activeProjectId}
            statusData={workflowStatusData || {
              status: job?.status === 'running' || ['extracting_audio', 'stt', 'translating', 'generating_tts', 'syncing_audio', 'rendering'].includes(job?.status)
                ? 'running'
                : job?.status === 'paused'
                  ? 'paused'
                  : job?.status === 'failed'
                    ? 'failed'
                    : job?.status === 'completed'
                      ? 'completed'
                      : job?.status === 'cancelled'
                        ? 'cancelled'
                        : (job?.status || 'not_started'),
              current_stage: job?.stage || 'INGEST',
              current_step: job?.current_step || 'Ready',
              overall_progress_pct: job?.overall_progress_pct || 0,
              stages: [
                { name: 'INGEST', status: job ? 'passed' : 'pending' },
                { name: 'ANALYZE', status: job?.stage === 'TRANSLATING' || job?.status === 'completed' ? 'passed' : job?.stage === 'TRANSCRIBING' ? 'running' : 'pending' },
                { name: 'TRANSLATE', status: job?.stage === 'SYNTHESIZING' || job?.status === 'completed' ? 'passed' : job?.stage === 'TRANSLATING' ? 'running' : 'pending' },
                { name: 'DUB', status: job?.stage === 'RENDERING' || job?.status === 'completed' ? 'passed' : job?.stage === 'SYNTHESIZING' ? 'running' : 'pending' },
                { name: 'PRODUCE', status: job?.status === 'completed' ? 'passed' : job?.stage === 'RENDERING' ? 'running' : 'pending' },
                { name: 'PUBLISH', status: 'pending' },
              ]
            }}
            job={job}
            pipelineError={pipelineError}
            onStart={handleOpenPreflightOrPromptProject}
            onPause={handlePauseWorkflow}
            onResume={handleResumeWorkflow}
            onCancel={handleCancelWorkflow}
            onRetryStage={handleRetryStage}
            onRetryJob={handleRetryJob}
            onOpenLogs={handleOpenLogs}
            loadingAction={loadingWorkflowAction}
            lastPollTime={lastPollTime}
            lastApiResponseTime={lastApiResponseTime}
            segments={segments}
          />

          {/* Compact Input Video & Configuration Options */}
          <div className="compact-card">
            <div className="compact-card-header">
              <h3 className="compact-card-title">
                ⚙️ Cấu hình Nhập Video, Dịch & Lồng Tiếng
              </h3>
            </div>

            {/* Mode Selector */}
            <div style={{ display: 'flex', gap: '10px', marginBottom: '14px' }}>
              <button
                onClick={() => setInputMode('url')}
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: inputMode === 'url' ? '2px solid #818cf8' : '1px solid #334155',
                  background: inputMode === 'url' ? '#312e81' : '#0f172a',
                  color: '#fff',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  fontSize: '13px',
                }}
              >
                🔗 Dán Link/URL Video
              </button>
              <button
                onClick={() => setInputMode('upload')}
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: inputMode === 'upload' ? '2px solid #818cf8' : '1px solid #334155',
                  background: inputMode === 'upload' ? '#312e81' : '#0f172a',
                  color: '#fff',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  fontSize: '13px',
                }}
              >
                📁 Upload File từ Máy
              </button>
            </div>

            {inputMode === 'url' ? (
              <div style={{ marginBottom: '14px' }}>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input
                    type="text"
                    placeholder="https://example.com/video.mp4"
                    value={videoUrl}
                    onChange={(e) => setVideoUrl(e.target.value)}
                    style={{
                      flex: 1,
                      padding: '8px 12px',
                      borderRadius: '6px',
                      border: '1px solid #475569',
                      background: '#0f172a',
                      color: '#fff',
                      fontSize: '13px',
                    }}
                  />
                  <button
                    onClick={handleCheckUrl}
                    disabled={isCheckingUrl || !videoUrl}
                    style={{
                      padding: '8px 14px',
                      borderRadius: '6px',
                      background: '#4f46e5',
                      color: '#fff',
                      border: 'none',
                      fontWeight: 'bold',
                      fontSize: '12px',
                      cursor: isCheckingUrl ? 'not-allowed' : 'pointer',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {isCheckingUrl ? <><ButtonSpinner /> Kiểm tra...</> : '🔍 Kiểm tra URL'}
                  </button>
                </div>
                {checkError && <div style={{ color: '#ef4444', fontSize: '12px', marginTop: '4px' }}>{checkError}</div>}
                {urlMetadata && (
                  <div style={{ marginTop: '8px', padding: '8px 12px', background: '#0f172a', borderRadius: '6px', fontSize: '12px', border: '1px solid #334155', display: 'flex', gap: '16px' }}>
                    <span style={{ color: '#4ade80', fontWeight: 'bold' }}>✓ Metadata Hợp Lệ</span>
                    <span><strong>Tiêu đề:</strong> {urlMetadata.title}</span>
                    <span><strong>Thời lượng:</strong> {formatTime(urlMetadata.duration)}</span>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ marginBottom: '14px' }}>
                <input
                  type="file"
                  accept="video/*"
                  onChange={(e) => setUploadFile(e.target.files[0] || null)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    borderRadius: '6px',
                    border: '1px solid #475569',
                    background: '#0f172a',
                    color: '#fff',
                    fontSize: '13px',
                  }}
                />
              </div>
            )}

            {/* Compact Configuration Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px', marginBottom: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#94a3b8' }}>LLM Provider:</label>
                <select
                  value={llmProviderId}
                  onChange={(e) => setLlmProviderId(e.target.value)}
                  style={{ width: '100%', padding: '6px 8px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569', fontSize: '12px' }}
                >
                  <option value="gemini">✨ Google Gemini AI Studio</option>
                  <option value="openai">🤖 OpenAI ChatGPT</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#94a3b8' }}>Target Language:</label>
                <select
                  value={targetLanguage}
                  onChange={(e) => setTargetLanguage(e.target.value)}
                  style={{ width: '100%', padding: '6px 8px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569', fontSize: '12px' }}
                >
                  <option value="vi">🇻🇳 Tiếng Việt (Vietnamese)</option>
                  <option value="en">🇬🇧 Tiếng Anh (English)</option>
                  <option value="ja">🇯🇵 Tiếng Nhật (Japanese)</option>
                  <option value="ko">🇰🇷 Tiếng Hàn (Korean)</option>
                  <option value="zh">🇨🇳 Tiếng Trung (Chinese)</option>
                  <option value="fr">🇫🇷 Tiếng Pháp (French)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#94a3b8' }}>TTS Provider:</label>
                <select
                  value={audioProviderId}
                  onChange={(e) => setAudioProviderId(e.target.value)}
                  style={{ width: '100%', padding: '6px 8px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569', fontSize: '12px' }}
                >
                  <option value="edge_tts">Edge TTS (Miễn phí / Nhanh)</option>
                  <option value="elevenlabs">ElevenLabs (Cao cấp)</option>
                  <option value="google_tts">Google Cloud TTS</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#94a3b8' }}>Giọng đọc (Voice):</label>
                <select
                  value={voiceId}
                  onChange={(e) => setVoiceId(e.target.value)}
                  style={{ width: '100%', padding: '6px 8px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569', fontSize: '12px' }}
                >
                  {voices.map(v => (
                    <option key={v.id} value={v.id}>{v.name} ({v.gender})</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px', color: '#94a3b8' }}>Âm thanh gốc:</label>
                <select
                  value={originalAudioMode}
                  onChange={(e) => setOriginalAudioMode(e.target.value)}
                  style={{ width: '100%', padding: '6px 8px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569', fontSize: '12px' }}
                >
                  <option value="mute">Tắt hoàn toàn tiếng gốc (Mute)</option>
                  <option value="duck">Giảm âm lượng gốc (Ducking 20%)</option>
                  <option value="keep">Giữ âm thanh gốc trộn cùng</option>
                </select>
              </div>

              <div style={{ display: 'flex', alignItems: 'center' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', fontSize: '12px', color: '#e2e8f0', marginTop: '16px' }}>
                  <input
                    type="checkbox"
                    checked={autoConfirmTranslation}
                    onChange={(e) => setAutoConfirmTranslation(e.target.checked)}
                    style={{ width: '16px', height: '16px', accentColor: '#10b981', cursor: 'pointer' }}
                  />
                  Auto-Confirm Translation
                </label>
              </div>
            </div>

            {/* Start Pipeline Action Button */}
            <button
              onClick={handleOpenPreflightOrPromptProject}
              disabled={isProcessing}
              style={{
                width: '100%',
                padding: '10px 16px',
                borderRadius: '8px',
                background: 'linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%)',
                color: '#fff',
                fontWeight: 'bold',
                fontSize: '14px',
                border: 'none',
                cursor: isProcessing ? 'not-allowed' : 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
              }}
            >
              {isProcessing ? <><ButtonSpinner /> ⚡ Đang xử lý Pipeline...</> : '🚀 Bắt đầu Nhập & Dịch Video'}
            </button>
          </div>

        </div>

        {/* RIGHT SIDEBAR COLUMN: WATERMARK & AI THUMBNAIL */}
        <div className="studio-right-col">
          
          {/* Watermark Branding Section */}
          <div className="compact-card">
            <div className="compact-card-header">
              <h3 className="compact-card-title">
                🏷️ Watermark (Logo/Branding)
              </h3>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', fontSize: '12px', color: '#e2e8f0' }}>
                <input
                  type="checkbox"
                  checked={watermarkEnabled}
                  onChange={(e) => setWatermarkEnabled(e.target.checked)}
                  style={{ width: '16px', height: '16px', accentColor: '#6366f1', cursor: 'pointer' }}
                />
                Bật
              </label>
            </div>

            {watermarkEnabled ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div style={{ display: 'flex', gap: '12px', fontSize: '12px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', color: '#cbd5e1' }}>
                    <input
                      type="radio"
                      name="wm_type"
                      value="image"
                      checked={watermarkType === 'image'}
                      onChange={() => setWatermarkType('image')}
                      style={{ accentColor: '#6366f1' }}
                    />
                    🖼️ Logo Ảnh
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', color: '#cbd5e1' }}>
                    <input
                      type="radio"
                      name="wm_type"
                      value="text"
                      checked={watermarkType === 'text'}
                      onChange={() => setWatermarkType('text')}
                      style={{ accentColor: '#6366f1' }}
                    />
                    🔤 Text
                  </label>
                </div>

                {watermarkType === 'image' ? (
                  <div>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <input
                        type="file"
                        accept="image/png,image/jpeg,image/webp"
                        onChange={handleLogoUpload}
                        disabled={isUploadingLogo}
                        style={{ background: '#0f172a', padding: '6px', borderRadius: '6px', color: '#fff', border: '1px solid #475569', fontSize: '11px', flex: 1 }}
                      />
                      {isUploadingLogo && <span style={{ color: '#818cf8', fontSize: '11px' }}><ButtonSpinner /></span>}
                    </div>
                    {watermarkImagePreview && (
                      <div style={{ marginTop: '6px', display: 'flex', alignItems: 'center', gap: '8px', background: '#0f172a', padding: '4px 8px', borderRadius: '6px' }}>
                        <img src={watermarkImagePreview} alt="Logo" style={{ maxHeight: '28px', maxWidth: '80px', objectFit: 'contain' }} />
                        <span style={{ color: '#4ade80', fontSize: '11px' }}>✓ Đã chọn logo</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div>
                    <input
                      type="text"
                      value={watermarkText}
                      onChange={(e) => setWatermarkText(e.target.value)}
                      placeholder="© Watermark Text"
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '6px', background: '#0f172a', border: '1px solid #475569', color: '#fff', fontSize: '12px' }}
                    />
                  </div>
                )}

                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: '#94a3b8', marginBottom: '3px' }}>Vị trí:</label>
                  <select
                    value={watermarkPosition}
                    onChange={(e) => setWatermarkPosition(e.target.value)}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569', fontSize: '12px' }}
                  >
                    <option value="bottom_right">↘️ Góc Dưới Phải</option>
                    <option value="bottom_left">↙️ Góc Dưới Trái</option>
                    <option value="top_right">↗️ Góc Trên Phải</option>
                    <option value="top_left">↖️ Góc Trên Trái</option>
                    <option value="center">⏹️ Chính Giữa</option>
                  </select>
                </div>

                <div>
                  <button
                    type="button"
                    onClick={() => setShowWatermarkDetails(!showWatermarkDetails)}
                    style={{ background: 'none', border: 'none', color: '#818cf8', fontSize: '11px', cursor: 'pointer', padding: 0, fontWeight: 'bold' }}
                  >
                    {showWatermarkDetails ? '▲ Thu gọn tùy chỉnh' : '⚙️ Tùy chỉnh kích thước & opacity'}
                  </button>
                </div>

                {showWatermarkDetails && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '8px', background: '#0f172a', borderRadius: '6px', fontSize: '11px' }}>
                    <div>
                      <span style={{ color: '#94a3b8' }}>Scale ({Math.round(watermarkScale * 100)}%):</span>
                      <input
                        type="range"
                        min="0.10"
                        max="0.50"
                        step="0.05"
                        value={watermarkScale}
                        onChange={(e) => setWatermarkScale(parseFloat(e.target.value))}
                        style={{ width: '100%', accentColor: '#818cf8' }}
                      />
                    </div>
                    <div>
                      <span style={{ color: '#94a3b8' }}>Opacity ({Math.round(watermarkOpacity * 100)}%):</span>
                      <input
                        type="range"
                        min="0.10"
                        max="1.00"
                        step="0.05"
                        value={watermarkOpacity}
                        onChange={(e) => setWatermarkOpacity(parseFloat(e.target.value))}
                        style={{ width: '100%', accentColor: '#818cf8' }}
                      />
                    </div>
                  </div>
                )}

                {watermarkValidationError && (
                  <div style={{ color: '#ef4444', fontSize: '11px', fontWeight: 'bold' }}>
                    {watermarkValidationError}
                  </div>
                )}
              </div>
            ) : (
              <div style={{ fontSize: '12px', color: '#94a3b8', fontStyle: 'italic' }}>
                🚫 Watermark hiện đang TẮT.
              </div>
            )}
          </div>

          {/* AI Auto Thumbnail Branding Section */}
          <div className="compact-card">
            <div className="compact-card-header">
              <h3 className="compact-card-title">
                🖼️ Tự Động Tạo Thumbnail AI
              </h3>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', fontSize: '12px', color: '#e2e8f0' }}>
                <input
                  type="checkbox"
                  checked={thumbnailEnabled}
                  onChange={(e) => setThumbnailEnabled(e.target.checked)}
                  style={{ width: '16px', height: '16px', accentColor: '#6366f1', cursor: 'pointer' }}
                />
                Bật
              </label>
            </div>

            {thumbnailEnabled ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: '#94a3b8', marginBottom: '3px' }}>Phong cách (Style):</label>
                  <select
                    value={thumbnailStyle}
                    onChange={(e) => setThumbnailStyle(e.target.value)}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569', fontSize: '12px' }}
                  >
                    <option value="auto">🤖 Tự động theo kịch bản</option>
                    <option value="cinematic">🎬 Cinematic Kịch tính</option>
                    <option value="youtube_viral">🚀 YouTube Viral Bắt mắt</option>
                    <option value="anime">🌸 Anime Nhật Bản</option>
                    <option value="realistic">📸 Realistic 8K</option>
                    <option value="cartoon">🎨 Cartoon 3D</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: '#94a3b8', marginBottom: '3px' }}>AI Provider:</label>
                  <select
                    value={thumbnailProvider}
                    onChange={(e) => setThumbnailProvider(e.target.value)}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569', fontSize: '12px' }}
                  >
                    <option value="pollinations">⚡ Pollinations AI (Miễn phí)</option>
                    <option value="fal">🎨 fal.ai FLUX</option>
                    <option value="openai">🤖 OpenAI DALL-E 3</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: '#94a3b8', marginBottom: '3px' }}>Custom Instruction:</label>
                  <textarea
                    rows={2}
                    placeholder="Tập trung nhân vật chính, tông u tối..."
                    value={thumbnailInstruction}
                    onChange={(e) => setThumbnailInstruction(e.target.value)}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569', fontSize: '11px', resize: 'vertical' }}
                  />
                </div>
              </div>
            ) : (
              <div style={{ fontSize: '12px', color: '#94a3b8', fontStyle: 'italic' }}>
                🖼️ Tạo Thumbnail AI hiện đang TẮT.
              </div>
            )}
          </div>

        </div>

      </div>

      {/* BELOW VIEWPORT SECTION: GLOSSARY MANAGER (DEFAULT CLOSED) */}
      <div style={{ marginTop: '20px' }}>
        <CollapsibleCard title="📖 Quản Lý Thuật Ngữ Dự Án (Glossary & Terminology Memory)" icon="📖" defaultOpen={false}>
          <ProjectGlossaryManager projectId={activeProjectId} />
        </CollapsibleCard>
      </div>

      {/* Segment Editor when phase 1 completes */}
      {job && (job.status === 'segment_editing' || job.status === 'completed' || segments.length > 0) && (
        <div className="card" style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '20px', color: '#fff', marginBottom: '20px' }}>
          <div style={{ marginBottom: '16px', padding: '12px 16px', background: '#064e3b', border: '1px solid #10b981', borderRadius: '8px', color: '#a7f3d0' }}>
            <h4 style={{ margin: '0 0 4px 0', fontSize: '15px', fontWeight: 'bold', color: '#6ee7b7' }}>
              🟢 Phase 1 Hoàn Thành – Đã Trích Xuất & Dịch Phân Đoạn!
            </h4>
            <p style={{ margin: 0, fontSize: '12px' }}>
              Hệ thống đã dịch thành công <strong>{segments.length}</strong> phân đoạn. Vui lòng xem lại và chỉnh sửa bản dịch dưới đây trước khi xác nhận render video lồng tiếng.
            </p>
          </div>

          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '12px' }}>📝 Xem lại & Chỉnh sửa Văn Bản Dịch</h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '400px', overflowY: 'auto', paddingRight: '4px' }}>
            {segments.map((seg) => (
              <div key={seg.id} style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', color: '#818cf8', fontWeight: 'bold', fontSize: '12px' }}>
                  <span>Phân đoạn #{seg.number}</span>
                  <span>⏱ {formatTime(seg.start_time)} → {formatTime(seg.end_time)}</span>
                </div>
                <div style={{ fontSize: '12px', color: '#cbd5e1', marginBottom: '6px', fontStyle: 'italic' }}>
                  Gốc ({job.detected_language || 'Auto'}): "{seg.original_text}"
                </div>
                <div>
                  <textarea
                    rows={2}
                    value={seg.translated_text}
                    onChange={(e) => handleSegmentTextChange(seg.id, e.target.value)}
                    style={{
                      width: '100%',
                      padding: '8px',
                      borderRadius: '6px',
                      background: '#1e293b',
                      color: '#fff',
                      border: '1px solid #475569',
                      fontSize: '13px',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          {job.status === 'segment_editing' && (
            <button
              onClick={handleRenderFinalVideo}
              disabled={isProcessing}
              style={{
                marginTop: '16px',
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                background: 'linear-gradient(90deg, #10b981 0%, #059669 100%)',
                color: '#fff',
                fontWeight: 'bold',
                fontSize: '15px',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              🎙️ Xác Nhận Bản Dịch & Render Video Lồng Tiếng
            </button>
          )}
        </div>
      )}

      {/* Final Dubbed Video Player */}
      {job && job.status === 'completed' && (job.output_url || job.output_video_path) && (
        <div className="card" style={{ background: '#064e3b', border: '1px solid #10b981', borderRadius: '12px', padding: '20px', color: '#fff', marginBottom: '20px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#6ee7b7', marginBottom: '14px' }}>🎉 Video Lồng Tiếng Đã Hoàn Thành!</h3>
          <div style={{ width: '100%', borderRadius: '8px', overflow: 'hidden', marginBottom: '14px', background: '#000' }}>
            <video
              controls
              style={{ width: '100%', maxHeight: '480px' }}
              src={job.output_url || `/media/${job.output_video_path.replace(/^.*[\\\/]data[\\\/]/, '')}`}
            />
          </div>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <a
              href={`http://127.0.0.1:8000/api/storage/download?path=${encodeURIComponent(job.output_video_path?.replace(/^.*[\\\/]data[\\\/]/, '') || '')}&filename=video_long_tieng.mp4`}
              download="final_translated_video.mp4"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-block',
                padding: '10px 20px',
                borderRadius: '6px',
                background: '#10b981',
                color: '#fff',
                fontWeight: 'bold',
                textDecoration: 'none',
                fontSize: '13px',
              }}
            >
              📥 Tải Video Lồng Tiếng (MP4)
            </a>
            <button
              onClick={() => setShowYouTubeModal(true)}
              style={{
                padding: '10px 20px',
                borderRadius: '6px',
                background: '#f43f5e',
                color: '#fff',
                fontWeight: 'bold',
                border: 'none',
                cursor: 'pointer',
                fontSize: '13px',
              }}
            >
              🔴 Tự Động SEO & Đăng Bài YouTube
            </button>
          </div>

          <AIQCScorecard jobId={job.id} />
          <VideoEditorStudio jobId={job.id} />
        </div>
      )}

      {/* YouTube Publisher Modal */}
      {showYouTubeModal && job && (
        <YouTubePublisherModal
          jobId={job.id}
          onClose={() => setShowYouTubeModal(false)}
        />
      )}

      {/* Log Terminal Modal */}
      {showLogModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0, 0, 0, 0.75)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: '#090d16', border: '1px solid #3b82f6', borderRadius: '12px', width: '100%', maxWidth: '850px', maxHeight: '80vh', display: 'flex', flexDirection: 'column', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)' }}>
            <div style={{ padding: '14px 18px', borderBottom: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 'bold', color: '#60a5fa' }}>
                📜 Job Execution Logs ({job?.id || job?.job_id})
              </h3>
              <button onClick={() => setShowLogModal(false)} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '20px', cursor: 'pointer' }}>✕</button>
            </div>

            <div style={{ padding: '14px', flex: 1, overflowY: 'auto', background: '#020617', fontFamily: 'monospace', fontSize: '12px', color: '#38bdf8', whiteSpace: 'pre-wrap' }}>
              {isFetchingLogs ? 'Đang tải log...' : logsContent}
            </div>

            <div style={{ padding: '10px 18px', borderTop: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>{copySuccess && <span style={{ color: '#4ade80', fontSize: '12px' }}>✓ {copySuccess}</span>}</div>
              <div style={{ display: 'flex', gap: '8px' }}>
                {job?.error_message && (
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(job.error_message);
                      setCopySuccess('Đã sao chép câu thông báo lỗi');
                      setTimeout(() => setCopySuccess(''), 2000);
                    }}
                    style={{ padding: '6px 12px', borderRadius: '6px', background: '#7f1d1d', color: '#fca5a5', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '12px' }}
                  >
                    ⚠️ Sao Chép Lỗi
                  </button>
                )}
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(logsContent);
                    setCopySuccess('Đã sao chép toàn bộ log');
                    setTimeout(() => setCopySuccess(''), 2000);
                  }}
                  style={{ padding: '6px 12px', borderRadius: '6px', background: '#334155', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '12px' }}
                >
                  📋 Sao Chép Full Log
                </button>
                <button
                  onClick={() => fetchLogs(job?.id || job?.job_id)}
                  style={{ padding: '6px 12px', borderRadius: '6px', background: '#2563eb', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '12px' }}
                >
                  🔄 Làm Mới
                </button>
                <button
                  onClick={() => setShowLogModal(false)}
                  style={{ padding: '6px 12px', borderRadius: '6px', background: '#475569', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '12px' }}
                >
                  Đóng
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Switch Project Guard Modal */}
      {showSwitchGuardModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.75)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '14px', padding: '24px', maxWidth: '460px', width: '90%', color: '#fff' }}>
            <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', color: '#f59e0b' }}>⚠️ Có thay đổi cấu hình chưa lưu</h3>
            <p style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '16px', lineHeight: '1.5' }}>
              Bạn vừa thay đổi cấu hình của dự án hiện tại nhưng chưa bấm <strong>Lưu cấu hình</strong>. Vui lòng chọn thao tác:
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button
                onClick={async () => {
                  await handleSaveSettingsToProject();
                  setSelectedProjectId(pendingSwitchProjectId);
                  setShowSwitchGuardModal(false);
                }}
                style={{ background: '#2563eb', color: '#fff', border: 'none', padding: '8px 14px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' }}
              >
                💾 Lưu thay đổi & Chuyển dự án
              </button>
              <button
                onClick={() => {
                  handleDiscardChanges();
                  setSelectedProjectId(pendingSwitchProjectId);
                  setShowSwitchGuardModal(false);
                }}
                style={{ background: '#475569', color: '#fff', border: 'none', padding: '8px 14px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' }}
              >
                🗑️ Bỏ qua thay đổi & Chuyển dự án
              </button>
              <button
                onClick={() => setShowSwitchGuardModal(false)}
                style={{ background: 'transparent', color: '#94a3b8', border: '1px solid #475569', padding: '8px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' }}
              >
                ❌ Hủy
              </button>
            </div>
          </div>
        </div>
      )}

      {/* No Project Selected Modal */}
      {showNoProjectModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999 }}>
          <div style={{ background: '#1e1b4b', border: '1px solid #4338ca', borderRadius: '14px', padding: '24px', maxWidth: '460px', width: '90%', color: '#fff' }}>
            <h2 style={{ margin: '0 0 10px 0', fontSize: '18px', fontWeight: 'bold', color: '#fbbf24' }}>
              ⚠️ Chưa chọn dự án
            </h2>
            <p style={{ color: '#cbd5e1', fontSize: '13px', lineHeight: '1.5', margin: '0 0 16px 0' }}>
              Để bắt đầu dịch video, vui lòng chọn một dự án có sẵn hoặc tạo dự án mới.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <button
                onClick={() => {
                  setShowNoProjectModal(false);
                  setShowCreateProjectModal(true);
                }}
                style={{ background: '#4f46e5', color: '#fff', border: 'none', padding: '10px', borderRadius: '6px', fontWeight: 'bold', fontSize: '13px', cursor: 'pointer' }}
              >
                ➕ Tạo dự án mới ngay
              </button>

              {projectsList.length > 0 && (
                <div>
                  <select
                    style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#0f1117', color: '#fff', border: '1px solid #4338ca', fontSize: '13px' }}
                    onChange={(e) => {
                      if (e.target.value) {
                        setSelectedProjectId(e.target.value);
                        setShowNoProjectModal(false);
                      }
                    }}
                    defaultValue=""
                  >
                    <option value="" disabled>-- Chọn dự án trong danh sách --</option>
                    {projectsList.map((p) => (
                      <option key={p.id} value={p.id}>{p.title} (ID: {p.id})</option>
                    ))}
                  </select>
                </div>
              )}

              <button
                onClick={() => setShowNoProjectModal(false)}
                style={{ background: '#374151', color: '#94a3b8', border: 'none', padding: '8px', borderRadius: '6px', fontSize: '12px', cursor: 'pointer' }}
              >
                Hủy bỏ
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Project Modal */}
      {showCreateProjectModal && (
        <div
          style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999 }}
          onClick={(e) => { if (e.target === e.currentTarget) closeCreateProjectModalSafely(); }}
        >
          <div style={{ background: '#1e1b4b', border: '1px solid #4338ca', borderRadius: '14px', padding: '24px', maxWidth: '480px', width: '90%', color: '#fff' }}>
            <h2 style={{ margin: '0 0 14px 0', fontSize: '18px', fontWeight: 'bold', color: '#818cf8' }}>
              📁 Tạo Dự Án Mới
            </h2>
            <form onSubmit={handleCreateProjectSubmit}>
              <div style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '12px', color: '#cbd5e1', marginBottom: '4px', fontWeight: '500' }}>
                  Tên dự án <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <input
                  type="text"
                  placeholder="Ví dụ: Dịch phim hoạt hình"
                  value={newProjectTitle}
                  onChange={(e) => setNewProjectTitle(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f1117', color: '#fff', border: '1px solid #4338ca', fontSize: '13px' }}
                  required
                  autoFocus
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '12px', color: '#cbd5e1', marginBottom: '4px', fontWeight: '500' }}>
                  Mô tả dự án (Tùy chọn)
                </label>
                <textarea
                  placeholder="Ghi chú dự án..."
                  value={newProjectDescription}
                  onChange={(e) => setNewProjectDescription(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#0f1117', color: '#fff', border: '1px solid #4338ca', fontSize: '12px', minHeight: '70px', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button
                  type="button"
                  onClick={closeCreateProjectModalSafely}
                  style={{ background: '#374151', color: '#cbd5e1', border: 'none', padding: '8px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={isCreatingProject}
                  style={{ background: '#4f46e5', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' }}
                >
                  {isCreatingProject ? <ButtonSpinner text="Đang tạo..." /> : '🚀 Tạo dự án'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Pre-flight Check Modal */}
      {showPreflightModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999 }}>
          <div style={{ background: '#1e1b4b', border: '1px solid #4338ca', borderRadius: '14px', padding: '24px', maxWidth: '600px', width: '90%', color: '#fff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold', color: '#818cf8' }}>
                📋 WORKFLOW PRE-FLIGHT CHECK
              </h2>
              <button onClick={() => setShowPreflightModal(false)} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '22px', cursor: 'pointer' }}>×</button>
            </div>

            {isPreflighting ? (
              <div style={{ padding: '24px 0', textAlign: 'center' }}>
                <LoadingSpinner size="lg" />
                <p style={{ marginTop: '12px', color: '#94a3b8', fontSize: '13px' }}>Đang kiểm tra tiền điều kiện hệ thống...</p>
              </div>
            ) : preflightResult ? (
              <div>
                <div style={{ padding: '10px 14px', borderRadius: '6px', background: preflightResult.can_start ? '#065f4633' : '#991b1b33', border: `1px solid ${preflightResult.can_start ? '#059669' : '#dc2626'}`, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '18px' }}>{preflightResult.can_start ? '✅' : '❌'}</span>
                  <div>
                    <div style={{ fontWeight: 'bold', color: preflightResult.can_start ? '#34d399' : '#f87171', fontSize: '14px' }}>
                      {preflightResult.can_start ? 'READY TO START — Tất cả kiểm tra bắt buộc đã đạt' : 'CRITICAL FAILURE — Kiểm tra bắt buộc thất bại'}
                    </div>
                  </div>
                </div>

                <div style={{ maxHeight: '260px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {preflightResult.checks.map((chk, idx) => (
                    <div key={idx} style={{ padding: '8px 12px', borderRadius: '6px', background: '#0f1117', border: '1px solid #2a2f3d', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span>{chk.passed ? '✓' : (chk.category === 'optional' ? '⚠️' : '❌')}</span>
                        <span style={{ fontSize: '12px', color: chk.passed ? '#e2e8f0' : (chk.category === 'optional' ? '#fbbf24' : '#f87171') }}>{chk.description}</span>
                      </div>
                      <span style={{ fontSize: '10px', fontWeight: 'bold', padding: '2px 6px', borderRadius: '4px', background: chk.passed ? '#065f46' : '#7f1d1d', color: chk.passed ? '#a7f3d0' : '#fecaca' }}>
                        {chk.passed ? 'PASS' : 'FAILED'}
                      </span>
                    </div>
                  ))}
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #334155' }}>
                  <button onClick={() => setShowPreflightModal(false)} style={{ background: '#374151', color: '#cbd5e1', border: 'none', padding: '8px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}>
                    Đóng
                  </button>
                  {preflightResult.can_start && (
                    <button
                      onClick={executeStartWorkflowAfterPreflight}
                      disabled={loadingWorkflowAction === 'start'}
                      style={{ background: 'linear-gradient(90deg, #059669 0%, #10b981 100%)', color: '#fff', border: 'none', padding: '8px 18px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' }}
                    >
                      {loadingWorkflowAction === 'start' ? <ButtonSpinner text="Đang khởi chạy..." /> : '🚀 Bắt đầu Workflow ngay'}
                    </button>
                  )}
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}

      {/* Edit Project Title Modal */}
      {showEditTitleModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999 }}>
          <div style={{ background: '#1e1b4b', border: '1px solid #4338ca', borderRadius: '14px', padding: '24px', maxWidth: '480px', width: '90%', color: '#fff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold', color: '#818cf8' }}>
                ✏️ Chỉnh sửa tên dự án
              </h2>
              <button onClick={() => setShowEditTitleModal(false)} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '22px', cursor: 'pointer' }}>×</button>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '12px', color: '#cbd5e1', marginBottom: '6px', fontWeight: '500' }}>
                Tên mới cho dự án (ID: <code>{selectedProjectId}</code>):
              </label>
              <input
                type="text"
                value={editTitleInput}
                onChange={(e) => setEditTitleInput(e.target.value)}
                placeholder="Tên dự án..."
                autoFocus
                style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', background: '#0f1117', color: '#fff', border: '1px solid #4338ca', fontSize: '13px', boxSizing: 'border-box' }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSaveProjectTitleInStudio();
                  if (e.key === 'Escape') setShowEditTitleModal(false);
                }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
              <button
                type="button"
                onClick={() => setShowEditTitleModal(false)}
                disabled={isSavingTitle}
                style={{ background: '#374151', color: '#cbd5e1', border: 'none', padding: '8px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}
              >
                Hủy
              </button>
              <button
                type="button"
                onClick={handleSaveProjectTitleInStudio}
                disabled={isSavingTitle || !editTitleInput.trim()}
                style={{ background: '#4f46e5', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' }}
              >
                {isSavingTitle ? <ButtonSpinner text="Đang lưu..." /> : '💾 Lưu tên mới'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

