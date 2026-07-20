const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  private token = localStorage.getItem('cryptanium_token');
  private url(path: string) { return `${API_BASE_URL}${path}`; }
  setToken(token: string) { this.token = token; localStorage.setItem('cryptanium_token', token); }
  clearToken() { this.token = null; localStorage.removeItem('cryptanium_token'); }
  async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const response = await fetch(this.url(path), { ...init, headers: { 'Content-Type': 'application/json', ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}), ...init.headers } });
    if (!response.ok) { if (response.status === 401) this.clearToken(); const body = await response.json().catch(() => ({})); throw new Error(body.detail || `Request failed (${response.status})`); }
    return response.json();
  }
  login(code: string, state?: string) { return this.request<{access_token: string}>(`/auth/callback?code=${encodeURIComponent(code)}${state ? `&state=${encodeURIComponent(state)}` : ''}`); }
  getCurrentUser() { return this.request('/auth/me'); }
  getRepositories() { return this.request('/repositories'); }
  syncRepositories() { return this.request('/repositories/sync', { method: 'POST' }); }
  getScans() { return this.request('/scans'); }
  createScan(repository_id: string | number) { return this.request('/scan', { method: 'POST', body: JSON.stringify({ repository_id: String(repository_id) }) }); }
  getReports() { return this.request('/reports'); }
  downloadReport(id: string | number) { return this.url(`/reports/${id}/pdf`); }
}

export const apiClient = new APIClient();
export default apiClient;
