import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('cryptanium_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('cryptanium_token');
      // Redirect to login if unauthenticated
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Repositories
  getRepositories: () => apiClient.get('/repositories'),
  getRepository: (id: string | number) => apiClient.get(`/repositories/${id}`),
  createRepository: (data: { name: string; clone_url: string; default_branch?: string }) => apiClient.post('/repositories', data),
  triggerScan: (repositoryId: string | number) => apiClient.post('/scan', { repository_id: String(repositoryId) }),
  deleteRepository: (id: string | number) => apiClient.delete(`/repositories/${id}`),

  // Scans
  getScans: () => apiClient.get('/scans'),
  getScan: (id: string | number) => apiClient.get(`/scans/${id}`),
  getScanSummary: (id: string | number) => apiClient.get(`/scans/${id}/summary`),
  getScanRecommendations: (id: string | number) => apiClient.get(`/scans/${id}/recommendations`),

  // Reports
  getReports: () => apiClient.get('/reports'),
  getReportPdfUrl: (id: string | number) => `${API_BASE_URL}/reports/${id}/pdf`,
  getReportJsonUrl: (id: string | number) => `${API_BASE_URL}/reports/${id}/json`,

  // Auth
  getCurrentUser: () => apiClient.get('/auth/me'),
  loginDemo: () => apiClient.post('/auth/demo-login'),
};
