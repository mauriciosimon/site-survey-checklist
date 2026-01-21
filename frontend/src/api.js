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

export const workspaceApi = {
  getAll: (filters = {}) =>
    api.get('/workspaces', {
      params: {
        is_active: filters.is_active,
        search: filters.search || undefined,
        skip: filters.skip || undefined,
        limit: filters.limit || undefined,
      },
    }),

  getById: (id) =>
    api.get(`/workspaces/${id}`),

  create: (data) =>
    api.post('/workspaces', data),

  update: (id, data) =>
    api.put(`/workspaces/${id}`, data),

  delete: (id) =>
    api.delete(`/workspaces/${id}`),
};

export const checklistApi = {
  getAll: (filters = {}) =>
    api.get('/checklists', {
      params: {
        workspace_id: filters.workspace_id || undefined,
        search: filters.search || undefined,
      },
    }),

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

export const leadApi = {
  getAll: (filters = {}) =>
    api.get('/leads', {
      params: {
        workspace_id: filters.workspace_id || undefined,
        status: filters.status || undefined,
        priority: filters.priority || undefined,
        source: filters.source || undefined,
        search: filters.search || undefined,
        skip: filters.skip || undefined,
        limit: filters.limit || undefined,
      },
    }),

  getById: (id) =>
    api.get(`/leads/${id}`),

  create: (data) =>
    api.post('/leads', data),

  update: (id, data) =>
    api.put(`/leads/${id}`, data),

  delete: (id) =>
    api.delete(`/leads/${id}`),
};

export const dealApi = {
  getAll: (filters = {}) =>
    api.get('/deals', {
      params: {
        workspace_id: filters.workspace_id || undefined,
        stage: filters.stage || undefined,
        status: filters.status || undefined,
        grade: filters.grade || undefined,
        deal_type: filters.deal_type || undefined,
        search: filters.search || undefined,
        skip: filters.skip || undefined,
        limit: filters.limit || undefined,
      },
    }),

  getById: (id) =>
    api.get(`/deals/${id}`),

  create: (data) =>
    api.post('/deals', data),

  update: (id, data) =>
    api.put(`/deals/${id}`, data),

  delete: (id) =>
    api.delete(`/deals/${id}`),
};

export const accountApi = {
  getAll: (filters = {}) =>
    api.get('/accounts', {
      params: {
        workspace_id: filters.workspace_id || undefined,
        status: filters.status || undefined,
        label: filters.label || undefined,
        industry: filters.industry || undefined,
        search: filters.search || undefined,
        skip: filters.skip || undefined,
        limit: filters.limit || undefined,
      },
    }),

  getById: (id) =>
    api.get(`/accounts/${id}`),

  create: (data) =>
    api.post('/accounts', data),

  update: (id, data) =>
    api.put(`/accounts/${id}`, data),

  delete: (id) =>
    api.delete(`/accounts/${id}`),
};

export const contactApi = {
  getAll: (filters = {}) =>
    api.get('/contacts', {
      params: {
        workspace_id: filters.workspace_id || undefined,
        contact_type: filters.contact_type || undefined,
        account_id: filters.account_id || undefined,
        icp_fit: filters.icp_fit || undefined,
        outreach_stage: filters.outreach_stage || undefined,
        search: filters.search || undefined,
        skip: filters.skip || undefined,
        limit: filters.limit || undefined,
      },
    }),

  getById: (id) =>
    api.get(`/contacts/${id}`),

  create: (data) =>
    api.post('/contacts', data),

  update: (id, data) =>
    api.put(`/contacts/${id}`, data),

  delete: (id) =>
    api.delete(`/contacts/${id}`),
};

export const taskApi = {
  getAll: (filters = {}) =>
    api.get('/tasks', {
      params: {
        workspace_id: filters.workspace_id || undefined,
        status: filters.status || undefined,
        priority: filters.priority || undefined,
        task_type: filters.task_type || undefined,
        owner_id: filters.owner_id || undefined,
        due_date_from: filters.due_date_from || undefined,
        due_date_to: filters.due_date_to || undefined,
        deal_id: filters.deal_id || undefined,
        lead_id: filters.lead_id || undefined,
        account_id: filters.account_id || undefined,
        search: filters.search || undefined,
        skip: filters.skip || undefined,
        limit: filters.limit || undefined,
      },
    }),

  getById: (id) =>
    api.get(`/tasks/${id}`),

  create: (data) =>
    api.post('/tasks', data),

  update: (id, data) =>
    api.put(`/tasks/${id}`, data),

  delete: (id) =>
    api.delete(`/tasks/${id}`),
};

export default api;
