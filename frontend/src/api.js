import axios from 'axios';

export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checklistApi = {
  getAll: (search = '') =>
    api.get('/checklists', { params: { search: search || undefined } }),

  getById: (id) =>
    api.get(`/checklists/${id}`),

  create: (data) =>
    api.post('/checklists', data),

  update: (id, data) =>
    api.put(`/checklists/${id}`, data),

  delete: (id) =>
    api.delete(`/checklists/${id}`),

  uploadPhoto: (id, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/checklists/${id}/photos`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export default api;
