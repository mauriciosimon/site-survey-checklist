import axios from 'axios';

export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
};

export const adminApi = {
  getUsers: () => api.get('/admin/users'),
  getChecklists: (userId = null) =>
    api.get('/admin/checklists', { params: { user_id: userId || undefined } }),
};

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
