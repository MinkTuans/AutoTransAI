import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;

export const projectsApi = {
  list: () => api.get('/projects').then(res => res.data),
  get: (id) => api.get(`/projects/${id}`).then(res => res.data),
  create: (data) => api.post('/projects', data).then(res => res.data),
  delete: (id) => api.delete(`/projects/${id}`).then(res => res.data),
  estimate: (id) => api.post(`/projects/${id}/estimate`).then(res => res.data),
  configure: (id, config) => api.post(`/projects/${id}/configure`, config).then(res => res.data),
  precheck: (id) => api.post(`/projects/${id}/precheck`).then(res => res.data),
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
};

export const systemApi = {
  health: () => api.get('/system/health').then(res => res.data),
  interrupted: () => api.get('/system/interrupted').then(res => res.data),
};
