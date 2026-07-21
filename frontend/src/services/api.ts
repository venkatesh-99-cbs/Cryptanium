const API_BASE_URL = import.meta.env.VITE_API_URL || window.location.origin;

class APIClient {
  private token = localStorage.getItem('cryptanium_token');

  private url(path: string) {
    return `${API_BASE_URL}${path}`;
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('cryptanium_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('cryptanium_token');
  }

  async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const response = await fetch(this.url(path), {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
        ...init.headers,
      },
    });

    if (!response.ok) {
      if (response.status === 401) this.clearToken();
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || `Request failed (${response.status})`);
    }

    // Handle 204 No Content
    if (response.status === 204) return undefined as unknown as T;
    return response.json();
  }

  // Auth
  login(code: string, state?: string) {
    return this.request<{ access_token: string; user: any }>(
      `/auth/callback?code=${encodeURIComponent(code)}${state ? `&state=${encodeURIComponent(state)}` : ''}`
    );
  }
  getCurrentUser() { return this.request<any>('/auth/me'); }

  // Repositories
  getRepositories() { return this.request<any[]>('/repositories'); }
  syncRepositories() { return this.request('/repositories/sync', { method: 'POST' }); }
  addRepository(payload: Record<string, unknown>) {
    return this.request('/repositories', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // Scans
  getScans() { return this.request<any[]>('/scans'); }
  getScanById(id: number | string) { return this.request(`/scans/${id}`); }
  createScan(repository_id: string | number) {
    return this.request('/scan', {
      method: 'POST',
      body: JSON.stringify({ repository_id: String(repository_id) }),
    });
  }
  createScanByName(repository_name: string) {
    return this.request('/scan', {
      method: 'POST',
      body: JSON.stringify({ repository_name }),
    });
  }

  // Reports
  getReports() { return this.request<any[]>('/reports'); }
  generateReport(id: string | number) { return this.request(`/reports/${id}/json`); }
  downloadPdfReport(id: string | number) { return this.url(`/reports/${id}/pdf`); }
  downloadJsonReport(id: string | number) { return this.url(`/reports/${id}/json`); }

  // AI Assistant
  aiChat(message: string, scan_id?: number | null) {
    return this.request<{ response: string; model: string }>('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ message, scan_id: scan_id ?? null }),
    });
  }

  analyzeScan(scan_id: number) {
    return this.request<{
      scan_id: number;
      executive_summary: string;
      risk_level: string;
      key_concerns: string[];
      recommendations: Record<string, unknown>[];
    }>(`/ai/analyze/${scan_id}`, { method: 'POST' });
  }

  getAISummary(scan_id: number) {
    return this.request<{
      scan_id: number;
      executive_summary: string;
      risk_level: string;
      key_concerns: string[];
      recommendations: Record<string, unknown>[];
    }>(`/ai/summary/${scan_id}`);
  }
}

export const apiClient = new APIClient();
export default apiClient;
