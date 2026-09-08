import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;

export const projectsApi = {
  list: (page, pageSize = 8) => api.get('/projects', { params: page ? { page, page_size: pageSize } : {} }).then(res => res.data),
  get: (id) => api.get(`/projects/${id}`).then(res => res.data),
  create: (data) => api.post('/projects', data).then(res => res.data),
  delete: (id) => api.delete(`/projects/${id}`).then(res => res.data),
  batchDelete: (ids) => api.post('/projects/batch-delete', { ids }).then(res => res.data),
  estimate: (id) => api.post(`/projects/${id}/estimate`).then(res => res.data),
  getSettings: (id) => api.get(`/projects/${id}/settings`).then(res => res.data),
  saveSettings: (id, settings) => api.post(`/projects/${id}/settings`, settings).then(res => res.data),
  run: (id) => api.post(`/projects/${id}/run`).then(res => res.data),
  resume: (id) => api.post(`/projects/${id}/resume`).then(res => res.data),
  cancel: (id) => api.post(`/projects/${id}/cancel`).then(res => res.data),
  status: (id) => api.get(`/projects/${id}/status`).then(res => res.data),
};

export const providersApi = {
  list: () => api.get('/providers').then(res => res.data),
  configureKey: (providerId, apiKey) =>
    api.post(`/providers/${providerId}/config`, { api_key: apiKey }).then(res => res.data),
  listVoices: (providerId, language) =>
    api.get(`/providers/${providerId}/voices`, { params: { language } }).then(res => res.data),
  listKeys: (providerId) => api.get(`/providers/${providerId}/keys`).then(res => res.data),
  addKey: (providerId, apiKey, priority) =>
    api.post(`/providers/${providerId}/keys`, { api_key: apiKey, priority }).then(res => res.data),
  deleteKey: (providerId, keyId) =>
    api.delete(`/providers/${providerId}/keys/${keyId}`).then(res => res.data),
  updateKey: (providerId, keyId, data) =>
    api.put(`/providers/${providerId}/keys/${keyId}`, data).then(res => res.data),
  testKey: (providerId, keyId) =>
    api.post(`/providers/${providerId}/keys/${keyId}/test`).then(res => res.data),
  checkQuota: (providerId, keyId) =>
    api.post(`/providers/${providerId}/keys/${keyId}/quota`).then(res => res.data),
  addCustomProvider: (data) =>
    api.post('/providers', data).then(res => res.data),
};

export const settingsApi = {
  getSettings: () => api.get('/settings').then(res => res.data),
  updateSettings: (settings) => api.put('/settings', { settings }).then(res => res.data),
  getFunctions: () => api.get('/settings/functions').then(res => res.data),
  updateFunction: (functionId, data) => api.put(`/settings/functions/${functionId}`, data).then(res => res.data),
  getModels: (providerId) => api.get('/settings/models', { params: { provider_id: providerId } }).then(res => res.data),
  addModel: (data) => api.post('/settings/models', data).then(res => res.data),
  updateModel: (modelId, data) => api.put(`/settings/models/${encodeURIComponent(modelId)}`, data).then(res => res.data),
  deleteModel: (modelId) => api.delete(`/settings/models/${encodeURIComponent(modelId)}`).then(res => res.data),

  getSocialAccounts: () => api.get('/settings/social-accounts').then(res => res.data),
  addSocialAccount: (data) => api.post('/settings/social-accounts', data).then(res => res.data),
  deleteSocialAccount: (id) => api.delete(`/settings/social-accounts/${id}`).then(res => res.data),
  testStorage: (data) => api.post('/settings/storage/test', data).then(res => res.data),
};

export const systemApi = {

  health: () => api.get('/system/health').then(res => res.data),
  interrupted: () => api.get('/system/interrupted').then(res => res.data),
};

export const videoTranslatorApi = {
  checkUrl: (url) => api.post('/video-translator/check-url', { url }).then(res => res.data),
  importUrl: (url) => {
    const formData = new FormData();
    formData.append('source_type', 'url');
    formData.append('url', url);
    return api.post('/video-translator/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(res => res.data);
  },
  importUpload: (file) => {
    const formData = new FormData();
    formData.append('source_type', 'upload');
    formData.append('file', file);
    return api.post('/video-translator/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(res => res.data);
  },
  getAsset: (assetId) => api.get(`/video-translator/assets/${assetId}`).then(res => res.data),
  createJob: (data) => api.post('/video-translator/jobs', data).then(res => res.data),
  startJob: (jobId) => api.post(`/video-translator/jobs/${jobId}/start`).then(res => res.data),
  getJob: (jobId) => api.get(`/video-translator/jobs/${jobId}`).then(res => res.data),
  updateSegments: (jobId, segments) =>
    api.put(`/video-translator/jobs/${jobId}/segments`, { segments }).then(res => res.data),
  renderJob: (jobId) => api.post(`/video-translator/jobs/${jobId}/render`).then(res => res.data),
  renderFinalVideo: (jobId) => api.post(`/video-translator/jobs/${jobId}/render`).then(res => res.data),
  getLogs: (jobId) => api.get(`/video-translator/jobs/${jobId}/logs`).then(res => res.data),
  uploadWatermarkLogo: (file, projectId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (projectId) {
      formData.append('project_id', projectId);
    }
    return api.post('/video-translator/upload-watermark-logo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(res => res.data);
  },
  cancelJob: (jobId) => api.post(`/video-translator/jobs/${jobId}/cancel`).then(res => res.data),
  retryJob: (jobId) => api.post(`/video-translator/jobs/${jobId}/retry`).then(res => res.data),
  getStudioState: (jobId) => api.get(`/video-translator/jobs/${jobId}/studio-state`).then(res => res.data),
  updateStudioState: (jobId, data) => api.patch(`/video-translator/jobs/${jobId}/studio-state`, data).then(res => res.data),
  saveCheckpoint: (jobId, data) => api.post(`/video-translator/jobs/${jobId}/checkpoint`, data).then(res => res.data),
  resumeJobFromCheckpoint: (jobId) => api.post(`/video-translator/jobs/${jobId}/resume`).then(res => res.data),
  applyJobSettings: (jobId) => api.post(`/video-translator/jobs/${jobId}/apply-settings`).then(res => res.data),

  // Unified 6-Stage Workflow Engine APIs
  preflightWorkflow: (projectId, data) => api.post(`/video-translator/projects/${projectId}/workflow/preflight`, data || {}).then(res => res.data),
  getWorkflowStatus: (projectId) => api.get(`/video-translator/projects/${projectId}/workflow-status`).then(res => res.data),
  startWorkflow: (projectId, data) => api.post(`/video-translator/projects/${projectId}/workflow/start`, data || {}).then(res => res.data),
  pauseWorkflow: (projectId) => api.post(`/video-translator/projects/${projectId}/workflow/pause`).then(res => res.data),
  resumeWorkflow: (projectId) => api.post(`/video-translator/projects/${projectId}/workflow/resume`).then(res => res.data),
  cancelWorkflow: (projectId) => api.post(`/video-translator/projects/${projectId}/workflow/cancel`).then(res => res.data),
  retryStage: (projectId, stageName) => api.post(`/video-translator/projects/${projectId}/workflow/stage/${stageName}/retry`).then(res => res.data),

  // Terminology & Glossary
  getGlossary: (projectId) => api.get(`/video-translator/projects/${projectId}/glossary`).then(res => res.data),
  addGlossary: (projectId, data) => api.post(`/video-translator/projects/${projectId}/glossary`, data).then(res => res.data),
  deleteGlossary: (projectId, termId) => api.delete(`/video-translator/projects/${projectId}/glossary/${termId}`).then(res => res.data),
  getTerminologyMemory: (projectId) => api.get(`/video-translator/projects/${projectId}/terminology-memory`).then(res => res.data),
  addTerminologyMemory: (projectId, data) => api.post(`/video-translator/projects/${projectId}/terminology-memory`, data).then(res => res.data),
  deleteTerminologyMemory: (projectId, termId) => api.delete(`/video-translator/projects/${projectId}/terminology-memory/${termId}`).then(res => res.data),
};

export const videoEditorApi = {
  saveConfig: (data) => api.post('/video-editor/config', data).then(res => res.data),
  uploadLogo: (jobId, file) => {
    const formData = new FormData();
    formData.append('job_id', jobId);
    formData.append('file', file);
    return api.post('/video-editor/upload-logo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(res => res.data);
  },
  runQC: (jobId) => api.post(`/video-editor/jobs/${jobId}/run-qc`).then(res => res.data),
  generateSEO: (jobId) => api.post(`/video-editor/jobs/${jobId}/generate-seo`).then(res => res.data),
  publishYouTube: (data) => api.post('/video-editor/jobs/' + data.job_id + '/publish-youtube', data).then(res => res.data),
};

export const thumbnailApi = {
  generate: (data) => api.post('/thumbnails/generate', data).then(res => res.data),
  get: (id) => api.get(`/thumbnails/${id}`).then(res => res.data),
  getByProject: (projectId) => api.get(`/thumbnails/by-project/${projectId}`).then(res => res.data),
  getByJob: (jobId) => api.get(`/thumbnails/by-job/${jobId}`).then(res => res.data),
  regenerate: (id, data) => api.post(`/thumbnails/${id}/regenerate`, data).then(res => res.data),
  setActive: (id) => api.post(`/thumbnails/${id}/set-active`).then(res => res.data),
  delete: (id) => api.delete(`/thumbnails/${id}`).then(res => res.data),
};

export const youtubeApi = {
  getAuthUrl: () => api.get('/youtube/auth-url').then(res => res.data),
  listAccounts: () => api.get('/youtube/accounts').then(res => res.data),
  disconnectAccount: (id) => api.delete(`/youtube/accounts/${id}`).then(res => res.data),
  getUploadStatus: (uploadId) => api.get(`/youtube/upload/${uploadId}/status`).then(res => res.data),
};




