/**
 * Cryptanium Frontend API Client
 * 
 * Centralized HTTP client for all backend communications.
 * - Handles authentication (JWT tokens)
 * - Provides typed responses
 * - Manages error handling
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  headers?: Record<string, string>;
  body?: unknown;
  params?: Record<string, string | number | boolean>;
}

class APIClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
    this.loadToken();
  }

  private loadToken(): void {
    this.token = localStorage.getItem("cryptanium_token");
  }

  setToken(token: string): void {
    this.token = token;
    localStorage.setItem("cryptanium_token", token);
  }

  clearToken(): void {
    this.token = null;
    localStorage.removeItem("cryptanium_token");
  }

  private buildURL(endpoint: string, params?: Record<string, string | number | boolean>): string {
    const url = new URL(`${this.baseURL}${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }
    return url.toString();
  }

  private buildHeaders(options?: RequestOptions): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...options?.headers,
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    return headers;
  }

  async request<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    const url = this.buildURL(endpoint, options?.params);
    const headers = this.buildHeaders(options);

    const fetchOptions: RequestInit = {
      method: options?.method || "GET",
      headers,
    };

    if (options?.body && options.method !== "GET") {
      fetchOptions.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, fetchOptions);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : "Network error");
    }
  }

  // === Authentication ===

  async login(code: string, state?: string) {
    return this.request("/auth/callback", {
      method: "GET",
      params: { code, ...(state && { state }) },
    });
  }

  async getCurrentUser() {
    return this.request("/auth/me");
  }

  async logout() {
    return this.request("/auth/logout", { method: "POST" });
  }

  async refreshToken() {
    return this.request("/auth/refresh", { method: "POST" });
  }

  // === Repositories ===

  async getRepositories(token?: string) {
    return this.request<any[]>("/repositories", {
      headers: token ? { "x-github-token": token } : undefined,
    });
  }

  async getRepository(id: number) {
    return this.request(`/repositories/${id}`);
  }

  async syncRepositories() {
    return this.request("/repositories/sync", { method: "POST" });
  }

  async deleteRepository(id: number) {
    return this.request(`/repositories/${id}`, { method: "DELETE" });
  }

  // === Scans ===

  async getScans() {
    return this.request<any[]>("/scans");
  }

  async getScan(id: number) {
    return this.request(`/scans/${id}`);
  }

  async createScan(repositoryId: number) {
    return this.request("/scan", {
      method: "POST",
      body: { repository_id: repositoryId },
    });
  }

  async startScan(id: number) {
    return this.request(`/scans/${id}/start`, { method: "POST" });
  }

  async cancelScan(id: number) {
    return this.request(`/scans/${id}/cancel`, { method: "POST" });
  }

  // === Reports ===

  async getReports() {
    return this.request<any[]>("/reports");
  }

  async getReport(id: number) {
    return this.request(`/reports/${id}`);
  }

  async downloadReport(id: number) {
    return this.request(`/reports/download/${id}`);
  }

  // === Dashboard ===

  async getDashboard() {
    return this.request("/dashboard");
  }

  // === Health ===

  async checkHealth() {
    return this.request("/health");
  }
}

export const apiClient = new APIClient();
export default apiClient;
