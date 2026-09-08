import React, { useState, useEffect, useRef } from 'react';
import { videoTranslatorApi, providersApi, projectsApi } from '../api';
import VideoEditorStudio from '../components/VideoEditorStudio';
import AIQCScorecard from '../components/AIQCScorecard';
import YouTubePublisherModal from '../components/YouTubePublisherModal';
import WorkflowTimeline from '../components/WorkflowTimeline';
import ProjectGlossaryManager from '../components/ProjectGlossaryManager';
import AIThumbnailPanel from '../components/AIThumbnailPanel';
import { LoadingSpinner, ButtonSpinner, LoadingOverlay } from '../components/LoadingSpinner';

function CollapsibleCard({ title, icon, defaultOpen = true, children, extraHeaderRight }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="card" style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', marginBottom: '24px', overflow: 'hidden' }}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        style={{
          padding: '16px 20px',
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
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', color: '#f8fafc' }}>{title}</h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {extraHeaderRight && <div onClick={(e) => e.stopPropagation()}>{extraHeaderRight}</div>}
          <span style={{ fontSize: '13px', color: '#94a3b8', background: '#1e293b', padding: '4px 10px', borderRadius: '6px', fontWeight: 'bold', border: '1px solid #334155' }}>
            {isOpen ? '▲ Thu gọn' : '▼ Mở rộng'}
          </span>
        </div>
      </div>
      {isOpen && <div style={{ padding: '20px' }}>{children}</div>}
    </div>
  );
}


export default function VideoTranslator({ initialJobId, initialProjectId }) {
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
  const [sttModel, setSttModel] = useState('gemini-2.5-flash');
  const [voices, setVoices] = useState([]);
  const [voiceId, setVoiceId] = useState('vi-VN-HoaiMyNeural');
  const [originalAudioMode, setOriginalAudioMode] = useState('mute');
  const [originalAudioVolume, setOriginalAudioVolume] = useState(0.20);

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
        setWatermarkImagePath(res.data.image_path);
        if (res.data.asset_id) setWatermarkImageAssetId(res.data.asset_id);
        const urlStr = res.data.url || URL.createObjectURL(file);
        setWatermarkImagePreview(urlStr);
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

  // Sync Project Settings when Project selection changes
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

  // Detect dirty state changes across ALL fields
  useEffect(() => {
    if (!savedProjectSettings || !selectedProjectId) {
      setIsSettingsDirty(false);
      return;
    }
    const current = getCurrentSettingsObject();
    const compareKeys = [
      'target_language', 'source_language', 'audio_provider_id', 'llm_provider_id',
      'stt_model', 'voice_id', 'original_audio_mode', 'original_audio_volume',
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

  const handleStartWorkflow = async () => {
    if (!activeProjectId || activeProjectId === 'default_project') {
      setShowNoProjectModal(true);
      return;
    }
    setLoadingWorkflowAction('start');
    setIsProcessing(true);
    setPipelineError(null);
    setWorkflowStatusData(prev => ({
      ...(prev || {}),
      status: 'running',
      current_stage: prev?.current_stage || 'INGEST',
      current_step: 'Đang gửi yêu cầu khởi chạy...',
      overall_progress_pct: prev?.overall_progress_pct || 0,
      stages: prev?.stages || [
        { name: 'INGEST', status: 'running' },
        { name: 'ANALYZE', status: 'pending' },
        { name: 'TRANSLATE', status: 'pending' },
        { name: 'DUB', status: 'pending' },
        { name: 'PRODUCE', status: 'pending' },
        { name: 'PUBLISH', status: 'pending' },
      ]
    }));
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
    if (!validateProjectBeforeAction()) return;
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
    if (!validateProjectBeforeAction()) return;
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
    if (!validateProjectBeforeAction()) return;
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
    if (!validateProjectBeforeAction()) return;
    setLoadingWorkflowAction('retry');
    try {
      await videoTranslatorApi.retryStage(activeProjectId, stageName);
      await fetchWorkflowStatus(activeProjectId);
    } catch (err) {
      alert(`Không thể thử lại stage ${stageName}: ` + formatApiError(err, 'Lỗi hệ thống'));
    } finally {
      setLoadingWorkflowAction(null);
    }
  };

  // Initial Job ID effect
  useEffect(() => {
    if (initialJobId) {
      videoTranslatorApi.getJob(initialJobId).then(res => {
        if (res.success && res.data) {
          setJob(res.data);
          if (res.data.segments) setSegments(res.data.segments);
          fetchWorkflowStatus(res.data.project_id || res.data.id);
        }
      }).catch(err => console.error('Failed to load initial job:', err));
    }
  }, [initialJobId]);


  // Log Modal state
  const [showLogModal, setShowLogModal] = useState(false);
  const [logsContent, setLogsContent] = useState('');
  const [isFetchingLogs, setIsFetchingLogs] = useState(false);
  const [copySuccess, setCopySuccess] = useState('');

  // Polling ref & Timestamps
  const pollingRef = useRef(null);
  const [lastPollTime, setLastPollTime] = useState(null);
  const [lastApiResponseTime, setLastApiResponseTime] = useState(null);

  // Fetch voices when provider or language changes
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

  // Single Source of Truth Polling Effect
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
      console.log(`[JOB POLL] Job ID: ${activeJobId} | Request time: ${nowStr}`);

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

            console.log(`[JOB POLL RESPONSE] Job: ${newJob.id} | Status: ${newJob.status} | Stage: ${newJob.stage} | Overall: ${newJob.overall_progress_pct}% | StagePct: ${newJob.stage_progress_pct}% | Heartbeat: ${newJob.heartbeat?.active} | FFmpeg: ${newJob.process?.status} | Segments: ${newJob.segments?.length || 0}`);

            // Stale response check: reject if request is older than latest received
            if (reqTimestamp < lastPollTimestampRef.current) {
              console.warn('[JOB POLL] Ignoring stale response');
              return;
            }
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
        .catch(err => {
          console.error('[JOB POLL ERROR]', err);
        });
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
    const url = err.config?.url ? err.config.url + '\n' : '';
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
    return `${status}${method}${url}Lỗi: ${detailStr}`;
  };

  const fetchLogs = async (jobId) => {
    const targetId = jobId || activeJobId;
    if (!targetId) {
      setLogsContent(
        pipelineError
          ? `⚠️ Chưa có Job ID được gán (Khởi tạo Job thất bại).\n\n[Chi Tiết Lỗi Request/Pipeline]:\n${pipelineError}`
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
      setLogsContent(
        `Không thể tải log từ server cho Job ID (${targetId}):\n${errFormatted}\n\n[Chi Tiết Lỗi Pipeline Hiển Thị]:\n${pipelineError || job?.error_message || 'N/A'}`
      );
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

      // Immediately set job state so activeJobId and project_id are populated before startJob completes
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

  const handleCancelJob = async () => {
    if (!activeJobId) return;
    try {
      await videoTranslatorApi.cancelJob(activeJobId);
      const res = await videoTranslatorApi.getJob(activeJobId);
      if (res.success) {
        const normalized = {
          ...res.data,
          id: res.data.id || res.data.job_id,
        };
        setJob(normalized);
      }
    } catch (err) {
      alert('Không thể hủy job: ' + formatApiError(err, 'Lỗi hệ thống'));
    }
  };

  const handleRetryJob = async () => {
    setIsProcessing(true);
    setPipelineError(null);

    // If workflow execution is present for active project, delegate smart retry to stage retry from current/failed stage
    if (activeProjectId && activeProjectId !== 'default_project' && workflowStatusData) {
      const targetStage = workflowStatusData.current_stage || 'INGEST';
      setLoadingWorkflowAction('retry');
      try {
        await videoTranslatorApi.retryStage(activeProjectId, targetStage);
        await fetchWorkflowStatus(activeProjectId);
        if (activeJobId) {
          const res = await videoTranslatorApi.getJob(activeJobId);
          if (res.success && res.data) {
            setJob({ ...res.data, id: res.data.id || res.data.job_id });
          }
        }
        return;
      } catch (err) {
        setPipelineError(`Không thể Smart Retry workflow từ stage ${targetStage}: ` + formatApiError(err, 'Lỗi hệ thống'));
      } finally {
        setLoadingWorkflowAction(null);
        setIsProcessing(false);
      }
      return;
    }

    if (!activeJobId) return;
    try {
      await videoTranslatorApi.retryJob(activeJobId);
      const res = await videoTranslatorApi.getJob(activeJobId);
      if (res.success && res.data) {
        const normalized = {
          ...res.data,
          id: res.data.id || res.data.job_id,
        };
        setJob(normalized);
      }
    } catch (err) {
      setPipelineError('Không thể thử lại job: ' + formatApiError(err, 'Lỗi hệ thống'));
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (sec) => {
    if (!sec || isNaN(sec)) return '00:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const getHeartbeatBadge = (currentJob) => {
    if (!currentJob) return null;
    const status = currentJob.status;
    const heartbeat = currentJob.heartbeat || {};
    const ageSec = heartbeat.age_seconds ?? 999;

    if (status === 'failed') {
      return (
        <span style={{ color: '#f87171', fontSize: '13px', fontWeight: 'bold' }}>
          🔴 Job thất bại (FAILED)
        </span>
      );
    }
    if (status === 'completed') {
      return (
        <span style={{ color: '#4ade80', fontSize: '13px', fontWeight: 'bold' }}>
          🟢 Hoàn thành (COMPLETED)
        </span>
      );
    }
    if (status === 'cancelled') {
      return (
        <span style={{ color: '#94a3b8', fontSize: '13px', fontWeight: 'bold' }}>
          ⚪ Đã hủy bởi người dùng (CANCELLED)
        </span>
      );
    }
    if (status === 'segment_editing') {
      return (
        <span style={{ color: '#6ee7b7', fontSize: '13px', fontWeight: 'bold' }}>
          🟢 Phase 1 Hoàn Thành (Đang chờ bạn xác nhận phân đoạn)
        </span>
      );
    }
    if (status === 'stalled') {
      return (
        <span style={{ color: '#fb923c', fontSize: '13px', fontWeight: 'bold' }}>
          🟠 Process có thể đã bị treo (STALLED)
        </span>
      );
    }

    if (heartbeat.active && ageSec <= 15) {
      return (
        <span style={{ color: '#4ade80', fontSize: '13px', fontWeight: 'bold' }}>
          🟢 Worker đang hoạt động (Cập nhật {Math.round(ageSec)}s trước)
        </span>
      );
    }
    if (ageSec <= 45) {
      return (
        <span style={{ color: '#facc15', fontSize: '13px', fontWeight: 'bold' }}>
          🟡 Đang xử lý / Chờ server... (Cập nhật {Math.round(ageSec)}s trước)
        </span>
      );
    }
    return (
      <span style={{ color: '#94a3b8', fontSize: '13px', fontWeight: 'bold' }}>
        ⚪ Worker đã dừng (Dừng heartbeat)
      </span>
    );
  };

  return (
    <div className="video-translator-container" style={{ padding: '24px', maxWidth: '1100px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px', color: '#818cf8' }}>
        🎬 Video Translator – Dịch & Lồng tiếng Video
      </h1>
      <p style={{ color: '#94a3b8', marginBottom: '24px' }}>
        Tự động dịch giọng nói trong video từ URL Internet hoặc file Upload với cơ chế real-time tracking, heartbeat và FFmpeg process log.
      </p>

      {/* Project Selector Bar */}
      <div style={{ background: '#1e1b4b', border: '1px solid #4338ca', borderRadius: '12px', padding: '16px 24px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '15px', fontWeight: 'bold', color: '#fff' }}>📁 Dự án hiện tại:</span>
          <select
            value={selectedProjectId || ''}
            onChange={(e) => handleProjectSelectAttempt(e.target.value || null)}
            style={{ minWidth: '280px', padding: '10px 14px', borderRadius: '8px', background: '#0f1117', color: '#fff', border: '1px solid #4338ca', fontSize: '14px', fontWeight: '500' }}
          >
            <option value="">-- Chưa chọn dự án (Bấm để chọn) --</option>
            {projectsList.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title} (ID: {p.id})
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={() => setShowCreateProjectModal(true)}
          style={{ background: '#4f46e5', color: '#fff', border: 'none', padding: '10px 18px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}
        >
          ➕ Tạo dự án mới
        </button>
      </div>

      {/* Dirty Settings Indicator Bar */}
      {isSettingsDirty && selectedProjectId && (
        <div style={{ background: '#1e3a8a', border: '1px solid #3b82f6', borderRadius: '10px', padding: '14px 20px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#fff', flexWrap: 'wrap', gap: '12px' }}>
          <span style={{ color: '#93c5fd', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px' }}>
            ⚠️ Bạn có thay đổi chưa lưu cho dự án này.
          </span>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={handleSaveSettingsToProject}
              disabled={isSavingSettings}
              style={{ background: '#2563eb', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' }}
            >
              {isSavingSettings ? 'Đang lưu DB...' : '💾 Lưu cấu hình dự án'}
            </button>
            <button
              onClick={handleDiscardChanges}
              style={{ background: '#475569', color: '#f8fafc', border: 'none', padding: '8px 16px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' }}
            >
              ↩️ Hủy thay đổi
            </button>
          </div>
        </div>
      )}

      {/* Switch Project Guard Modal */}
      {showSwitchGuardModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.75)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '14px', padding: '28px', maxWidth: '480px', width: '90%', color: '#fff' }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '18px', color: '#f59e0b' }}>⚠️ Có thay đổi cấu hình chưa lưu</h3>
            <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '20px', lineHeight: '1.5' }}>
              Bạn vừa thay đổi cấu hình của dự án hiện tại nhưng chưa bấm <strong>Lưu cấu hình</strong>. Bạn muốn làm gì trước khi chuyển sang dự án mới?
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <button
                onClick={async () => {
                  await handleSaveSettingsToProject();
                  setSelectedProjectId(pendingSwitchProjectId);
                  setShowSwitchGuardModal(false);
                }}
                style={{ background: '#2563eb', color: '#fff', border: 'none', padding: '10px 16px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', fontSize: '14px' }}
              >
                💾 Lưu thay đổi & Chuyển dự án
              </button>
              <button
                onClick={() => {
                  handleDiscardChanges();
                  setSelectedProjectId(pendingSwitchProjectId);
                  setShowSwitchGuardModal(false);
                }}
                style={{ background: '#475569', color: '#fff', border: 'none', padding: '10px 16px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', fontSize: '14px' }}
              >
                🗑️ Bỏ qua thay đổi & Chuyển dự án
              </button>
              <button
                onClick={() => setShowSwitchGuardModal(false)}
                style={{ background: 'transparent', color: '#94a3b8', border: '1px solid #475569', padding: '10px 16px', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' }}
              >
                ❌ Hủy (Ở lại dự án này)
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Visual 6-Stage Workflow Timeline */}
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
        onStart={handleOpenPreflightOrPromptProject}
        onPause={handlePauseWorkflow}
        onResume={handleResumeWorkflow}
        onCancel={handleCancelWorkflow}
        onRetryStage={handleRetryStage}
        loadingAction={loadingWorkflowAction}
      />

      {/* Error Message Card - Displayed directly below Workflow Timeline */}
      {(pipelineError || (job && job.status === 'failed') || (workflowStatusData && workflowStatusData.status === 'failed')) && (
        <div style={{ marginBottom: '24px', padding: '20px', background: '#7f1d1d', border: '1px solid #ef4444', borderRadius: '12px', color: '#fee2e2' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', color: '#fca5a5' }}>
              ❌ Xử Lý Thất Bại (Job / Workflow Failed)
            </h4>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={handleOpenLogs}
                style={{ padding: '6px 12px', borderRadius: '6px', background: '#451a03', color: '#fde68a', border: '1px solid #d97706', cursor: 'pointer', fontWeight: '600', fontSize: '12px' }}
              >
                📜 Xem Log Chi Tiết
              </button>
              <button
                onClick={handleRetryJob}
                style={{ padding: '6px 12px', borderRadius: '6px', background: '#d97706', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '12px' }}
              >
                🔄 Smart Retry
              </button>
            </div>
          </div>
          <div style={{ fontSize: '14px', fontFamily: 'monospace', background: '#450a0a', padding: '12px', borderRadius: '6px', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {job?.error_message || workflowStatusData?.error_message || pipelineError || 'Xảy ra lỗi không xác định trong pipeline.'}
          </div>
        </div>
      )}

      {/* Real-time Tracking & Progress Panel - Displayed directly below Workflow Timeline */}
      {job && (
        <div className="card" style={{ background: '#0f172a', border: `1px solid ${job.status === 'failed' ? '#ef4444' : '#3b82f6'}`, borderRadius: '12px', padding: '24px', color: '#fff', marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: job.status === 'failed' ? '#fca5a5' : '#60a5fa', margin: 0 }}>
              📊 Tiến Trình Xử Lý Pipeline (Job: {job.id || job.job_id})
            </h3>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={handleOpenLogs}
                style={{
                  padding: '6px 14px',
                  borderRadius: '6px',
                  background: '#334155',
                  color: '#fff',
                  border: 'none',
                  cursor: 'pointer',
                  fontWeight: '600',
                  fontSize: '13px',
                }}
              >
                📜 Xem Log Chi Tiết
              </button>

              {['extracting_audio', 'stt', 'translating', 'generating_tts', 'syncing_audio', 'rendering'].includes(job.status) && (
                <button
                  onClick={handleCancelJob}
                  style={{
                    padding: '6px 14px',
                    borderRadius: '6px',
                    background: '#991b1b',
                    color: '#fff',
                    border: 'none',
                    cursor: 'pointer',
                    fontWeight: '600',
                    fontSize: '13px',
                  }}
                >
                  ❌ Hủy Xử Lý
                </button>
              )}

              {(job.status === 'failed' || job.status === 'stalled') && (
                <button
                  onClick={handleRetryJob}
                  style={{
                    padding: '6px 14px',
                    borderRadius: '6px',
                    background: '#d97706',
                    color: '#fff',
                    border: 'none',
                    cursor: 'pointer',
                    fontWeight: '600',
                    fontSize: '13px',
                  }}
                >
                  🔄 Smart Retry
                </button>
              )}
            </div>
          </div>

          {/* Heartbeat Status Badge */}
          <div style={{ marginBottom: '16px', padding: '10px 14px', background: '#1e293b', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>{getHeartbeatBadge(job)}</div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>
              Stage: <strong>{job.stage || 'QUEUED'}</strong> | Status: <strong>{(job.status || '').toUpperCase()}</strong>
            </div>
          </div>

          {/* Overall Progress Bar */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
              <span>Tiến trình Tổng thể:</span>
              <span style={{ fontWeight: 'bold', color: job.status === 'failed' ? '#fca5a5' : '#60a5fa' }}>
                {job.overall_progress_pct}%
              </span>
            </div>
            <div style={{ background: '#1e293b', borderRadius: '8px', height: '14px', width: '100%', overflow: 'hidden' }}>
              <div
                style={{
                  width: `${job.overall_progress_pct}%`,
                  height: '100%',
                  background: job.status === 'failed' ? '#ef4444' : 'linear-gradient(90deg, #3b82f6, #8b5cf6)',
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
          </div>

          {/* Stage Detail Stats */}
          <div style={{ background: '#1e293b', borderRadius: '8px', padding: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', fontSize: '13px' }}>
            <div>
              <span style={{ color: '#94a3b8' }}>Bước hiện tại:</span>
              <div style={{ fontWeight: 'bold', color: job.status === 'failed' ? '#fca5a5' : '#e2e8f0', marginTop: '2px' }}>
                {job.current_step}
              </div>
            </div>

            <div>
              <span style={{ color: '#94a3b8' }}>Tiến trình Stage ({job.stage}):</span>
              <div style={{ fontWeight: 'bold', color: job.status === 'failed' ? '#ef4444' : '#a7f3d0', marginTop: '2px' }}>
                {job.stage_progress_pct}%
              </div>
            </div>

            <div>
              <span style={{ color: '#94a3b8' }}>FFmpeg Process Status:</span>
              <div style={{ fontWeight: 'bold', color: job.process?.status === 'RUNNING' ? '#60a5fa' : (job.process?.status === 'COMPLETED' ? '#4ade80' : (job.process?.status === 'FAILED' ? '#ef4444' : '#94a3b8')), marginTop: '2px' }}>
                {job.process?.status === 'RUNNING' ? `⚡ RUNNING (PID: ${job.process.pid})` : (job.process?.status === 'COMPLETED' ? '✅ COMPLETED' : (job.process?.status || 'IDLE'))}
              </div>
            </div>

            {job.ffmpeg_stats && job.status !== 'failed' && (
              <>
                <div>
                  <span style={{ color: '#94a3b8' }}>Đã xử lý (FFmpeg):</span>
                  <div style={{ fontWeight: 'bold', color: '#facc15', marginTop: '2px' }}>
                    {formatTime(job.ffmpeg_stats.processed_seconds)} / {formatTime(job.ffmpeg_stats.total_duration)}
                  </div>
                </div>
                <div>
                  <span style={{ color: '#94a3b8' }}>Tốc độ & FPS:</span>
                  <div style={{ fontWeight: 'bold', color: '#e2e8f0', marginTop: '2px' }}>
                    Speed: {job.ffmpeg_stats.speed} | FPS: {job.ffmpeg_stats.fps}
                  </div>
                </div>
              </>
            )}

            {job.stage === 'GENERATING_TTS' && (
              <div>
                <span style={{ color: '#94a3b8' }}>Phân đoạn TTS:</span>
                <div style={{ fontWeight: 'bold', color: '#c084fc', marginTop: '2px' }}>
                  {job.completed_segments_count} / {job.total_segments_count} Phân đoạn
                </div>
              </div>
            )}
          </div>

          {/* DEBUG JOB STATE PANEL (Dev Mode Single Source of Truth) */}
          <details open style={{ marginTop: '20px', padding: '14px 18px', background: '#020617', border: '1px solid #1e293b', borderRadius: '10px', fontSize: '12px', fontFamily: 'monospace', color: '#38bdf8' }}>
            <summary style={{ cursor: 'pointer', fontWeight: 'bold', color: '#facc15', fontSize: '14px' }}>🐞 DEBUG JOB STATE (Single Source of Truth)</summary>
            <div style={{ marginTop: '12px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '10px' }}>
              <div>Job ID: <strong style={{ color: '#fff' }}>{job.id || job.job_id}</strong></div>
              <div>Backend Status: <strong style={{ color: '#a7f3d0' }}>{job.status}</strong></div>
              <div>Backend Stage: <strong style={{ color: '#60a5fa' }}>{job.stage}</strong></div>
              <div>Overall Progress: <strong style={{ color: '#facc15' }}>{job.overall_progress_pct}%</strong></div>
              <div>Stage Progress: <strong style={{ color: '#facc15' }}>{job.stage_progress_pct}%</strong></div>
              <div>Heartbeat Active: <strong style={{ color: job.heartbeat?.active ? '#4ade80' : '#f87171' }}>{job.heartbeat?.active ? 'ACTIVE (TRUE)' : 'INACTIVE (FALSE)'}</strong> ({job.heartbeat?.age_seconds ?? 'N/A'}s)</div>
              <div>FFmpeg Status: <strong style={{ color: job.process?.status === 'COMPLETED' ? '#4ade80' : '#60a5fa' }}>{job.process?.status || 'IDLE'}</strong> (PID: {job.process?.pid || 'N/A'})</div>
              <div>STT Status: <strong style={{ color: job.stt?.status === 'COMPLETED' ? '#4ade80' : '#60a5fa' }}>{job.stt?.status || 'PENDING'}</strong> ({job.stt?.provider || 'gemini'})</div>
              <div>Detected Language: <strong style={{ color: '#fbbf24' }}>{job.detected_language || 'Auto'}</strong></div>
              <div>Translation Status: <strong style={{ color: job.translation?.status === 'COMPLETED' ? '#4ade80' : '#60a5fa' }}>{job.translation?.status || 'PENDING'}</strong></div>
              <div>Segments Loaded: <strong style={{ color: '#c084fc' }}>{segments.length} / {job.total_segments_count || segments.length}</strong></div>
              <div>Last Backend Update: <strong style={{ color: '#cbd5e1' }}>{job.updated_at ? new Date(job.updated_at).toLocaleTimeString('vi-VN') : 'N/A'}</strong></div>
              <div>Last Frontend Poll: <strong style={{ color: '#cbd5e1' }}>{lastPollTime || 'N/A'}</strong></div>
              <div>API Response Time: <strong style={{ color: '#cbd5e1' }}>{lastApiResponseTime || 'N/A'}</strong></div>
            </div>
          </details>
        </div>
      )}

      {/* Collapsible Card: Input Selection & Configuration Options */}
      <CollapsibleCard title="⚙️ Cấu hình Nhập Video, Dịch & Lồng Tiếng" icon="⚙️" defaultOpen={true}>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
          <button
            onClick={() => setInputMode('url')}
            style={{
              flex: 1,
              padding: '12px',
              borderRadius: '8px',
              border: inputMode === 'url' ? '2px solid #818cf8' : '1px solid #4338ca',
              background: inputMode === 'url' ? '#312e81' : '#1e1b4b',
              color: '#fff',
              fontWeight: 'bold',
              cursor: 'pointer',
            }}
          >
            🔗 Dán Link/URL Video
          </button>
          <button
            onClick={() => setInputMode('upload')}
            style={{
              flex: 1,
              padding: '12px',
              borderRadius: '8px',
              border: inputMode === 'upload' ? '2px solid #818cf8' : '1px solid #4338ca',
              background: inputMode === 'upload' ? '#312e81' : '#1e1b4b',
              color: '#fff',
              fontWeight: 'bold',
              cursor: 'pointer',
            }}
          >
            📁 Upload File từ Máy
          </button>
        </div>

        {inputMode === 'url' ? (
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: '#cbd5e1' }}>
              Nhập Đường Dẫn Video (Direct MP4, YouTube, Bilibili, TikTok...):
            </label>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                placeholder="https://example.com/video.mp4"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                style={{
                  flex: 1,
                  padding: '12px',
                  borderRadius: '6px',
                  border: '1px solid #475569',
                  background: '#0f172a',
                  color: '#fff',
                }}
              />
              <button
                onClick={handleCheckUrl}
                disabled={isCheckingUrl || !videoUrl}
                style={{
                  padding: '12px 20px',
                  borderRadius: '6px',
                  background: '#4f46e5',
                  color: '#fff',
                  border: 'none',
                  fontWeight: 'bold',
                  cursor: isCheckingUrl ? 'not-allowed' : 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                }}
              >
                {isCheckingUrl ? <><ButtonSpinner /> Đang kiểm tra...</> : '🔍 Kiểm tra URL'}
              </button>
            </div>
            {checkError && (
              <div style={{ color: '#ef4444', fontSize: '13px', marginTop: '8px' }}>
                {checkError}
              </div>
            )}
            {urlMetadata && (
              <div style={{ marginTop: '12px', padding: '12px', background: '#0f172a', borderRadius: '6px', fontSize: '13px', border: '1px solid #334155' }}>
                <div style={{ color: '#4ade80', fontWeight: 'bold', marginBottom: '4px' }}>✓ Metadata Hợp Lệ</div>
                <div><strong>Tiêu đề:</strong> {urlMetadata.title}</div>
                <div><strong>Thời lượng:</strong> {formatTime(urlMetadata.duration)} ({urlMetadata.duration}s)</div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: '#cbd5e1' }}>
              Chọn File Video (MP4, MOV, MKV, AVI):
            </label>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => setUploadFile(e.target.files[0] || null)}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '6px',
                border: '1px solid #475569',
                background: '#0f172a',
                color: '#fff',
              }}
            />
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '20px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '13px', marginBottom: '6px', color: '#94a3b8' }}>LLM / Script Provider:</label>
            <select
              value={llmProviderId}
              onChange={(e) => setLlmProviderId(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569' }}
            >
              <option value="gemini">✨ Google Gemini AI Studio (Mặc định)</option>
              <option value="openai">🤖 OpenAI ChatGPT</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', marginBottom: '6px', color: '#94a3b8' }}>Ngôn ngữ đích (Target):</label>
            <select
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569' }}
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
            <label style={{ display: 'block', fontSize: '13px', marginBottom: '6px', color: '#94a3b8' }}>TTS Provider:</label>
            <select
              value={audioProviderId}
              onChange={(e) => setAudioProviderId(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569' }}
            >
              <option value="edge_tts">Edge TTS (Miễn phí / Tốc độ cao)</option>
              <option value="elevenlabs">ElevenLabs (Chất lượng cao)</option>
              <option value="google_tts">Google Cloud TTS</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', marginBottom: '6px', color: '#94a3b8' }}>Giọng đọc (Voice):</label>
            <select
              value={voiceId}
              onChange={(e) => setVoiceId(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569' }}
            >
              {voices.map(v => (
                <option key={v.id} value={v.id}>{v.name} ({v.gender})</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '13px', marginBottom: '6px', color: '#94a3b8' }}>Âm thanh gốc (Original Audio):</label>
            <select
              value={originalAudioMode}
              onChange={(e) => setOriginalAudioMode(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f172a', color: '#fff', border: '1px solid #475569' }}
            >
              <option value="mute">Tắt hoàn toàn tiếng gốc (Mute)</option>
              <option value="duck">Giảm âm lượng gốc (Background Ducking 20%)</option>
              <option value="keep">Giữ âm thanh gốc trộn cùng tiếng đọc</option>
            </select>
          </div>
        </div>

        {/* Watermark Branding Section */}
        <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid #334155' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '15px', fontWeight: 'bold', color: '#818cf8', display: 'flex', alignItems: 'center', gap: '8px' }}>
              🏷️ Gắn Logo / Watermark Tự Động
            </span>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px', color: '#e2e8f0' }}>
              <input
                type="checkbox"
                checked={watermarkEnabled}
                onChange={(e) => setWatermarkEnabled(e.target.checked)}
                style={{ width: '18px', height: '18px', accentColor: '#6366f1', cursor: 'pointer' }}
              />
              Bật Watermark
            </label>
          </div>

          {watermarkEnabled && (
            <div style={{ background: '#0f172a', borderRadius: '8px', padding: '16px', border: '1px solid #334155' }}>
              <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', color: '#cbd5e1', fontSize: '13px' }}>
                  <input
                    type="radio"
                    name="wm_type"
                    value="image"
                    checked={watermarkType === 'image'}
                    onChange={() => setWatermarkType('image')}
                    style={{ accentColor: '#6366f1' }}
                  />
                  🖼️ Logo Ảnh (PNG/JPG/WEBP)
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', color: '#cbd5e1', fontSize: '13px' }}>
                  <input
                    type="radio"
                    name="wm_type"
                    value="text"
                    checked={watermarkType === 'text'}
                    onChange={() => setWatermarkType('text')}
                    style={{ accentColor: '#6366f1' }}
                  />
                  🔤 Watermark Chữ (Text)
                </label>
              </div>

              {watermarkType === 'image' ? (
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '13px', color: '#94a3b8', marginBottom: '6px' }}>
                    Upload File Logo (Khuyên dùng PNG nền trong suốt):
                  </label>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <input
                      type="file"
                      accept="image/png,image/jpeg,image/webp"
                      onChange={handleLogoUpload}
                      disabled={isUploadingLogo}
                      style={{ background: '#1e293b', padding: '8px', borderRadius: '6px', color: '#fff', border: '1px solid #475569', flex: 1 }}
                    />
                    {isUploadingLogo && <span style={{ color: '#818cf8', fontSize: '13px' }}><ButtonSpinner /> Đang tải...</span>}
                  </div>
                  {watermarkImagePreview && (
                    <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <img src={watermarkImagePreview} alt="Logo Preview" style={{ maxHeight: '48px', maxWidth: '120px', objectFit: 'contain', background: '#334155', padding: '4px', borderRadius: '4px' }} />
                      <span style={{ color: '#4ade80', fontSize: '12px' }}>✓ Logo đã chọn thành công</span>
                    </div>
                  )}
                </div>
              ) : (
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '13px', color: '#94a3b8', marginBottom: '6px' }}>Nội dung Text Watermark:</label>
                  <input
                    type="text"
                    value={watermarkText}
                    onChange={(e) => setWatermarkText(e.target.value)}
                    placeholder="© AutoTransAI - Bản quyền thuộc về channel"
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#1e293b', border: '1px solid #475569', color: '#fff' }}
                  />
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Vị trí Watermark:</label>
                  <select
                    value={watermarkPosition}
                    onChange={(e) => setWatermarkPosition(e.target.value)}
                    style={{ width: '100%', padding: '8px', borderRadius: '6px', background: '#1e293b', color: '#fff', border: '1px solid #475569' }}
                  >
                    <option value="bottom_right">↘️ Góc Dưới Phải (Bottom Right)</option>
                    <option value="bottom_left">↙️ Góc Dưới Trái (Bottom Left)</option>
                    <option value="top_right">↗️ Góc Trên Phải (Top Right)</option>
                    <option value="top_left">↖️ Góc Trên Trái (Top Left)</option>
                    <option value="center">⏹️ Chính Giữa (Center)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>
                    Tỷ lệ Kích thước ({Math.round(watermarkScale * 100)}% rộng video):
                  </label>
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
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>
                    Độ Trong Suốt ({Math.round(watermarkOpacity * 100)}%):
                  </label>
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

                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>
                    Khoảng Cách Mép ({watermarkMargin}px):
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="50"
                    step="5"
                    value={watermarkMargin}
                    onChange={(e) => setWatermarkMargin(parseInt(e.target.value, 10))}
                    style={{ width: '100%', accentColor: '#818cf8' }}
                  />
                </div>
              </div>

              {watermarkValidationError && (
                <div style={{ color: '#ef4444', fontSize: '13px', marginTop: '12px', fontWeight: 'bold' }}>
                  {watermarkValidationError}
                </div>
              )}
            </div>
          )}
        </div>

        <button
          onClick={handleOpenPreflightOrPromptProject}
          disabled={isProcessing}
          style={{
            marginTop: '20px',
            width: '100%',
            padding: '14px',
            borderRadius: '8px',
            background: 'linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%)',
            color: '#fff',
            fontWeight: 'bold',
            fontSize: '16px',
            border: 'none',
            cursor: isProcessing ? 'not-allowed' : 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
          }}
        >
          {isProcessing ? <><ButtonSpinner /> ⚡ Đang xử lý Pipeline...</> : '🚀 Bắt đầu Nhập & Dịch Video'}
        </button>
      </CollapsibleCard>

      {/* Collapsible Card: Project Glossary Manager */}
      <CollapsibleCard title="📖 Quản Lý Thuật Ngữ Dự Án (Glossary & Terminology Memory)" icon="📖" defaultOpen={false}>
        <ProjectGlossaryManager projectId={activeProjectId} />
      </CollapsibleCard>

      {/* Collapsible Card: AI Auto Thumbnail Panel */}
      <CollapsibleCard title="🖼️ Tạo Thumbnail AI Tự Động" icon="🖼️" defaultOpen={false}>
        <AIThumbnailPanel
          jobId={job?.id || job?.job_id}
          assetId={job?.asset_id}
          initialThumbnailUrl={job?.thumbnail_url}
        />
      </CollapsibleCard>

      {/* Segment Editor when phase 1 completes */}
      {job && (job.status === 'segment_editing' || job.status === 'completed' || segments.length > 0) && (
        <div className="card" style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '24px', color: '#fff', marginBottom: '24px' }}>
          <div style={{ marginBottom: '20px', padding: '16px 20px', background: '#064e3b', border: '1px solid #10b981', borderRadius: '10px', color: '#a7f3d0' }}>
            <h4 style={{ margin: '0 0 6px 0', fontSize: '16px', fontWeight: 'bold', color: '#6ee7b7' }}>
              🟢 Phase 1 Hoàn Thành – Đã Trích Xuất & Dịch Phân Đoạn!
            </h4>
            <p style={{ margin: 0, fontSize: '13px' }}>
              Hệ thống đã nhận diện giọng nói và dịch thành công <strong>{segments.length}</strong> phân đoạn. Vui lòng xem lại và chỉnh sửa bản dịch dưới đây trước khi xác nhận render video lồng tiếng.
            </p>
          </div>

          <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '12px' }}>📝 Xem lại & Chỉnh sửa Văn Bản Dịch</h3>
          <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '20px' }}>
            Bạn có thể chỉnh sửa câu từ dịch của từng mốc thời gian trước khi tiến hành tạo giọng đọc TTS và Render video.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {segments.map((seg) => (
              <div key={seg.id} style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: '#818cf8', fontWeight: 'bold', fontSize: '13px' }}>
                  <span>Phân đoạn #{seg.number}</span>
                  <span>⏱ {formatTime(seg.start_time)} → {formatTime(seg.end_time)}</span>
                </div>
                <div style={{ fontSize: '13px', color: '#cbd5e1', marginBottom: '8px', fontStyle: 'italic' }}>
                  Gốc ({job.detected_language || 'Auto'}): "{seg.original_text}"
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Bản dịch ({targetLanguage.toUpperCase()}):</label>
                  <textarea
                    rows={2}
                    value={seg.translated_text}
                    onChange={(e) => handleSegmentTextChange(seg.id, e.target.value)}
                    style={{
                      width: '100%',
                      padding: '10px',
                      borderRadius: '6px',
                      background: '#1e293b',
                      color: '#fff',
                      border: '1px solid #475569',
                      fontSize: '14px',
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
                marginTop: '20px',
                width: '100%',
                padding: '14px',
                borderRadius: '8px',
                background: 'linear-gradient(90deg, #10b981 0%, #059669 100%)',
                color: '#fff',
                fontWeight: 'bold',
                fontSize: '16px',
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
        <div className="card" style={{ background: '#064e3b', border: '1px solid #10b981', borderRadius: '12px', padding: '24px', color: '#fff' }}>
          <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#6ee7b7', marginBottom: '16px' }}>🎉 Video Lồng Tiếng Đã Hoàn Thành!</h3>
          <div style={{ width: '100%', borderRadius: '8px', overflow: 'hidden', marginBottom: '16px', background: '#000' }}>
            <video
              controls
              style={{ width: '100%', maxHeight: '500px' }}
              src={job.output_url || `/media/${job.output_video_path.replace(/^.*[\\\/]data[\\\/]/, '')}`}
            />
          </div>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <a
              href={job.output_url || `/media/${job.output_video_path.replace(/^.*[\\\/]data[\\\/]/, '')}`}
              download="final_translated_video.mp4"
              style={{
                display: 'inline-block',
                padding: '12px 24px',
                borderRadius: '8px',
                background: '#10b981',
                color: '#fff',
                fontWeight: 'bold',
                textDecoration: 'none',
              }}
            >
              📥 Tải Video Lồng Tiếng (MP4)
            </a>
            <button
              onClick={() => setShowYouTubeModal(true)}
              style={{
                padding: '12px 24px',
                borderRadius: '8px',
                background: '#f43f5e',
                color: '#fff',
                fontWeight: 'bold',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              🔴 Tự Động SEO & Đăng Bài YouTube
            </button>
          </div>

          {/* AI QC Scorecard */}
          <AIQCScorecard jobId={job.id} />

          {/* Video Editing & Branding Automation Studio */}
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
        <div
          style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '20px',
          }}
        >
          <div
            style={{
              background: '#090d16',
              border: '1px solid #3b82f6',
              borderRadius: '12px',
              width: '100%',
              maxWidth: '850px',
              maxHeight: '80vh',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
            }}
          >
            <div style={{ padding: '16px 20px', borderBottom: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', color: '#60a5fa' }}>
                📜 Job Execution Logs ({job?.id || job?.job_id})
              </h3>
              <button
                onClick={() => setShowLogModal(false)}
                style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '20px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: '16px', flex: 1, overflowY: 'auto', background: '#020617', fontFamily: 'monospace', fontSize: '12px', color: '#38bdf8', whiteSpace: 'pre-wrap' }}>
              {isFetchingLogs ? 'Đang tải log...' : logsContent}
            </div>

            <div style={{ padding: '12px 20px', borderTop: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                {copySuccess && <span style={{ color: '#4ade80', fontSize: '13px' }}>✓ {copySuccess}</span>}
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                {job?.error_message && (
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(job.error_message);
                      setCopySuccess('Đã sao chép câu thông báo lỗi');
                      setTimeout(() => setCopySuccess(''), 2000);
                    }}
                    style={{ padding: '8px 16px', borderRadius: '6px', background: '#7f1d1d', color: '#fca5a5', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '13px' }}
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
                  style={{ padding: '8px 16px', borderRadius: '6px', background: '#334155', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '13px' }}
                >
                  📋 Sao Chép Full Log
                </button>
                <button
                  onClick={() => fetchLogs(job?.id || job?.job_id)}
                  style={{ padding: '8px 16px', borderRadius: '6px', background: '#2563eb', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '13px' }}
                >
                  🔄 Làm Mới
                </button>
                <button
                  onClick={() => setShowLogModal(false)}
                  style={{ padding: '8px 16px', borderRadius: '6px', background: '#475569', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: '600', fontSize: '13px' }}
                >
                  Đóng
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {/* Modal 1: No Project Selected Modal */}
      {showNoProjectModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999 }}>
          <div style={{ background: '#1e1b4b', border: '1px solid #4338ca', borderRadius: '14px', padding: '28px', maxWidth: '480px', width: '90%', color: '#fff', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)' }}>
            <h2 style={{ margin: '0 0 12px 0', fontSize: '20px', fontWeight: 'bold', color: '#fbbf24' }}>
              ⚠️ Chưa chọn dự án
            </h2>
            <p style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: '1.5', margin: '0 0 20px 0' }}>
              Để bắt đầu dịch video và lưu trữ subtitle, audio & thumbnail, vui lòng chọn một dự án có sẵn hoặc tạo dự án mới.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <button
                onClick={() => {
                  setShowNoProjectModal(false);
                  setShowCreateProjectModal(true);
                }}
                style={{ background: '#4f46e5', color: '#fff', border: 'none', padding: '12px', borderRadius: '8px', fontWeight: 'bold', fontSize: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
              >
                ➕ Tạo dự án mới ngay
              </button>

              {projectsList.length > 0 && (
                <div style={{ marginTop: '4px' }}>
                  <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Hoặc chọn dự án có sẵn:</label>
                  <select
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#0f1117', color: '#fff', border: '1px solid #4338ca', fontSize: '14px' }}
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
                style={{ background: '#374151', color: '#94a3b8', border: 'none', padding: '10px', borderRadius: '8px', fontSize: '13px', cursor: 'pointer', marginTop: '4px' }}
              >
                Hủy bỏ
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal 2: Create Project Modal */}
      {showCreateProjectModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999 }}>
          <div style={{ background: '#1e1b4b', border: '1px solid #4338ca', borderRadius: '14px', padding: '28px', maxWidth: '500px', width: '90%', color: '#fff', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)' }}>
            <h2 style={{ margin: '0 0 16px 0', fontSize: '20px', fontWeight: 'bold', color: '#818cf8' }}>
              📁 Tạo Dự Án Mới
            </h2>
            <form onSubmit={handleCreateProjectSubmit}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '13px', color: '#cbd5e1', marginBottom: '6px', fontWeight: '500' }}>
                  Tên dự án <span style={{ color: '#ef4444' }}>*</span>
                </label>
                <input
                  type="text"
                  placeholder="Ví dụ: Dịch phim hoạt hình Trung Quốc"
                  value={newProjectTitle}
                  onChange={(e) => setNewProjectTitle(e.target.value)}
                  style={{ width: '100%', padding: '10px 14px', borderRadius: '6px', background: '#0f1117', color: '#fff', border: '1px solid #4338ca', fontSize: '14px' }}
                  required
                  autoFocus
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '13px', color: '#cbd5e1', marginBottom: '6px', fontWeight: '500' }}>
                  Mô tả dự án (Tùy chọn)
                </label>
                <textarea
                  placeholder="Ghi chú thể loại, tone màu hoặc phong cách dịch..."
                  value={newProjectDescription}
                  onChange={(e) => setNewProjectDescription(e.target.value)}
                  style={{ width: '100%', padding: '10px 14px', borderRadius: '6px', background: '#0f1117', color: '#fff', border: '1px solid #4338ca', fontSize: '13px', minHeight: '80px', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button
                  type="button"
                  onClick={() => setShowCreateProjectModal(false)}
                  style={{ background: '#374151', color: '#cbd5e1', border: 'none', padding: '10px 16px', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' }}
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={isCreatingProject}
                  style={{ background: '#4f46e5', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '14px' }}
                >
                  {isCreatingProject ? <ButtonSpinner text="Đang tạo..." /> : '🚀 Tạo dự án & Bắt đầu'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 3: Pre-flight Check Results Modal */}
      {showPreflightModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999 }}>
          <div style={{ background: '#1e1b4b', border: '1px solid #4338ca', borderRadius: '14px', padding: '28px', maxWidth: '640px', width: '90%', color: '#fff', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 'bold', color: '#818cf8', display: 'flex', alignItems: 'center', gap: '8px' }}>
                📋 WORKFLOW PRE-FLIGHT CHECK
              </h2>
              <button onClick={() => setShowPreflightModal(false)} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '24px', cursor: 'pointer' }}>×</button>
            </div>

            {isPreflighting ? (
              <div style={{ padding: '32px 0', textAlign: 'center' }}>
                <LoadingSpinner size="lg" />
                <p style={{ marginTop: '16px', color: '#94a3b8', fontSize: '14px' }}>Đang thực hiện kiểm tra tiền điều kiện hệ thống & AI Providers...</p>
              </div>
            ) : preflightResult ? (
              <div>
                <div style={{ padding: '12px 16px', borderRadius: '8px', background: preflightResult.can_start ? '#065f4633' : '#991b1b33', border: `1px solid ${preflightResult.can_start ? '#059669' : '#dc2626'}`, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '20px' }}>{preflightResult.can_start ? '✅' : '❌'}</span>
                  <div>
                    <div style={{ fontWeight: 'bold', color: preflightResult.can_start ? '#34d399' : '#f87171', fontSize: '15px' }}>
                      {preflightResult.can_start ? 'READY TO START — Tất cả kiểm tra bắt buộc đã vượt qua' : 'CRITICAL FAILURE — Kiểm tra bắt buộc thất bại'}
                    </div>
                    <div style={{ fontSize: '12px', color: '#cbd5e1', marginTop: '2px' }}>
                      {preflightResult.can_start ? 'Hệ thống sẵn sàng khởi chạy Unified 6-Stage Workflow.' : 'Vui lòng khắc phục các lỗi màu đỏ trước khi tiếp tục.'}
                    </div>
                  </div>
                </div>

                <div style={{ maxHeight: '300px', overflowY: 'auto', paddingRight: '4px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {preflightResult.checks.map((chk, idx) => (
                    <div key={idx} style={{ padding: '10px 14px', borderRadius: '6px', background: '#0f1117', border: '1px solid #2a2f3d', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                        <span style={{ fontSize: '16px' }}>{chk.passed ? '✓' : (chk.category === 'optional' ? '⚠️' : '❌')}</span>
                        <div>
                          <div style={{ fontWeight: '600', fontSize: '13px', color: chk.passed ? '#e2e8f0' : (chk.category === 'optional' ? '#fbbf24' : '#f87171') }}>
                            {chk.description}
                          </div>
                          {chk.error_message && (
                            <div style={{ fontSize: '12px', color: chk.category === 'optional' ? '#fcd34d' : '#fca5a5', marginTop: '4px', lineHeight: '1.4' }}>
                              {chk.error_message}
                            </div>
                          )}
                        </div>
                      </div>
                      <span style={{ fontSize: '11px', fontWeight: 'bold', padding: '3px 8px', borderRadius: '4px', background: chk.passed ? '#065f46' : (chk.category === 'optional' ? '#78350f' : '#7f1d1d'), color: chk.passed ? '#a7f3d0' : (chk.category === 'optional' ? '#fef3c7' : '#fecaca'), whiteSpace: 'nowrap' }}>
                        {chk.passed ? 'PASS' : (chk.category === 'optional' ? 'WARNING' : 'FAILED')}
                      </span>
                    </div>
                  ))}
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px', paddingTop: '14px', borderTop: '1px solid #334155' }}>
                  <button onClick={() => setShowPreflightModal(false)} style={{ background: '#374151', color: '#cbd5e1', border: 'none', padding: '10px 18px', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' }}>
                    Đóng
                  </button>
                  {preflightResult.can_start ? (
                    <button
                      onClick={executeStartWorkflowAfterPreflight}
                      disabled={loadingWorkflowAction === 'start'}
                      style={{ background: 'linear-gradient(90deg, #059669 0%, #10b981 100%)', color: '#fff', border: 'none', padding: '10px 22px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '14px' }}
                    >
                      {loadingWorkflowAction === 'start' ? <ButtonSpinner text="Đang khởi chạy..." /> : '🚀 Bắt đầu Workflow ngay'}
                    </button>
                  ) : (
                    <button
                      onClick={() => runPreflightCheck()}
                      style={{ background: '#d97706', color: '#fff', border: 'none', padding: '10px 18px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px' }}
                    >
                      🔄 Thử lại kiểm tra (Retry Check)
                    </button>
                  )}
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}
