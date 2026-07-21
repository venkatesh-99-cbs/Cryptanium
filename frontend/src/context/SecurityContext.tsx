import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiClient } from '../services/api';

// Type Definitions
export interface Repository {
  [key: string]: any;
  id: number;
  name: string;
  full_name: string;
  language: string;
  clone_url: string;
  default_branch: string;
  visibility: string;
  last_scan?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Finding {
  [key: string]: any;
  id: string;
  severity: string;
  description: string;
  file_path: string;
  line_number: number;
  rule_id: string;
  tool: string;
  repoId?: string | number;
}

export interface Scan {
  [key: string]: any;
  scan_id: number;
  repository_id: string | number;
  repository_name: string;
  status: string;
  trust_score: number;
  findings_count: number;
  created_at: string;
  completed_at?: string;
  started_at?: string;
}

export interface Report {
  [key: string]: any;
  id: number;
  scan_id: number;
  report_type: string;
  report_path?: string;
  generated_at: string;
  download_url: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  codeSnippet?: {
    title: string;
    code: string;
    isFix?: boolean;
  };
  timestamp: string;
}

interface User {
  [key: string]: any;
  id?: number;
  username: string;
  name?: string;
  email?: string;
  avatar_url?: string;
}

interface SecurityContextType {
  user: User | null;
  repositories: Repository[];
  findings: Finding[];
  scans: Scan[];
  reports: Report[];
  chatMessages: ChatMessage[];
  isScanning: boolean;
  activeScanRepo: string | null;
  isLoading: boolean;
  error: string | null;
  toastMessage: string | null;
  loadRepositories: () => Promise<void>;
  loadScans: () => Promise<void>;
  loadReports: () => Promise<void>;
  loadDashboard: () => Promise<void>;
  addRepository: (url: string) => Promise<void>;
  triggerScan: (repositoryId: number) => Promise<void>;
  sendChatMessage: (text: string) => void;
  exportReport: (repoName: string, format: 'PDF' | 'JSON' | 'CSV') => void;
  generateReport: (scanId: string | number) => Promise<void>;
  isAuthenticated: boolean;
  login: (code: string) => Promise<void>;
  logout: () => void;
  syncRepositories: () => Promise<void>;
}

const SecurityContext = createContext<SecurityContextType | undefined>(undefined);

export const SecurityProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [findings, setFindings] = useState<Finding[]>(() => { try { return JSON.parse(localStorage.getItem('cryptanium_findings') || '[]'); } catch { return []; } });
  const [scans, setScans] = useState<Scan[]>(() => { try { return JSON.parse(localStorage.getItem('cryptanium_scans') || '[]'); } catch { return []; } });
  const [reports, setReports] = useState<Report[]>(() => { try { return JSON.parse(localStorage.getItem('cryptanium_reports') || '[]'); } catch { return []; } });
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [activeScanRepo, setActiveScanRepo] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem('cryptanium_token');
  });

  useEffect(() => { if (scans.length) localStorage.setItem('cryptanium_scans', JSON.stringify(scans)); }, [scans]);
  useEffect(() => { if (findings.length) localStorage.setItem('cryptanium_findings', JSON.stringify(findings)); }, [findings]);
  useEffect(() => { if (reports.length) localStorage.setItem('cryptanium_reports', JSON.stringify(reports)); }, [reports]);
  useEffect(() => {
    if (!toastMessage) return;
    const timer = window.setTimeout(() => setToastMessage(null), 4200);
    return () => window.clearTimeout(timer);
  }, [toastMessage]);

  // OAuth returns the JWT in the URL fragment so it is not sent to the server.
  useEffect(() => {
    const fragment = new URLSearchParams(window.location.hash.slice(1));
    const token = fragment.get('access_token');
    if (token) {
      apiClient.setToken(token);
      window.history.replaceState({}, document.title, `${window.location.pathname}${window.location.search}`);
      setIsAuthenticated(true);
    }
  }, []);

  // Load current user on mount
  useEffect(() => {
    const loadCurrentUser = async () => {
      try {
        if (isAuthenticated) {
      const userData = await apiClient.getCurrentUser();
          setUser(userData);
        }
      } catch (err) {
        console.error('Failed to load current user:', err);
        localStorage.removeItem('cryptanium_token');
        setIsAuthenticated(false);
      }
    };
    loadCurrentUser();
  }, [isAuthenticated]);

  // Load repositories
  const loadRepositories = useCallback(async () => {
    try {
      const data = await apiClient.getRepositories();
      setRepositories((data || []) as Repository[]);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load repositories';
      setError(message);
      console.error('Error loading repositories:', err);
    }
  }, []);

  // Load scans
  const loadScans = useCallback(async () => {
    try {
      const data = await apiClient.getScans();
      const loadedScans = (data || []) as Scan[];
      setScans(loadedScans);
      // Findings are persisted inside each scan response. Restore them on every
      // refresh so Overview and Findings remain accurate after navigation.
      const restoredFindings = loadedScans.flatMap((scan: any) =>
        (scan.findings || []).map((finding: any, index: number) => ({
          ...finding,
          id: finding.id || `${scan.scan_id}-${index}`,
          repoId: scan.repository_id,
          repoName: scan.repository_name,
          status: finding.status || 'Open',
          detectedAt: finding.detectedAt || scan.created_at,
        }))
      );
      setFindings(restoredFindings);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load scans';
      setError(message);
      console.error('Error loading scans:', err);
    }
  }, []);

  // Load reports
  const notifyUser = useCallback((title: string, body: string) => {
    if (typeof window === 'undefined') return;
    if ('Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(title, { body });
      } else if (Notification.permission === 'default') {
        Notification.requestPermission().catch(() => undefined);
      }
    }
  }, []);

  const loadReports = useCallback(async () => {
    try {
      const data = await apiClient.getReports();
      const normalizedReports = (data || []).map((report: any) => {
        const scan = scans.find((item) => String(item.scan_id) === String(report.scan_id));
        const repo = repositories.find((item) => String(item.id) === String(scan?.repository_id));
        const findings = {
          critical: scan?.critical_severity_count || 0,
          high: scan?.high_severity_count || 0,
          medium: scan?.medium_severity_count || 0,
          low: scan?.low_severity_count || 0,
        };
        const status = scan?.status ? scan.status.toUpperCase() : 'COMPLETED';
        return {
          ...report,
          repoId: scan?.repository_id ?? null,
          repoName: repo?.full_name || repo?.name || scan?.repository_name || `Repository ${report.scan_id}`,
          status: status === 'COMPLETED' ? 'HEALTHY' : status,
          trustScore: scan?.trust_score ?? 0,
          generatedAt: report.generated_at ? new Date(report.generated_at).toLocaleString() : 'Pending',
          findings,
          summary: scan?.ai_summary || '',
        } as Report;
      });
      setReports(normalizedReports);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load reports';
      setError(message);
      console.error('Error loading reports:', err);
    }
  }, [repositories, scans]);

  // Load dashboard
  const loadDashboard = useCallback(async () => {
    try {
      setIsLoading(true);
      await loadRepositories();
      await loadScans();
      await loadReports();
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load dashboard';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [loadRepositories, loadScans, loadReports]);

  useEffect(() => {
    if (isAuthenticated) void loadDashboard();
    // Run once per authenticated session. Including loadDashboard here causes
    // a dependency loop because it is recreated when repositories/scans load.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  // Sync repositories from GitHub
  const syncRepositories = useCallback(async () => {
    try {
      setIsLoading(true);
      await apiClient.syncRepositories();
      await loadRepositories();
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to sync repositories';
      setError(message);
      console.error('Error syncing repositories:', err);
    } finally {
      setIsLoading(false);
    }
  }, [loadRepositories]);

  // Add repository by URL or full_name and persist it locally for scanning
  const addRepository = useCallback(async (url: string) => {
    try {
      setIsLoading(true);
      const trimmed = url.trim();
      if (!trimmed) throw new Error('Repository URL is required');

      const ownerRepo = trimmed.replace(/^https?:\/\/github\.com\//i, '').replace(/\.git$/i, '').trim();
      const [owner, repoName] = ownerRepo.split('/').filter(Boolean);
      if (!owner || !repoName) throw new Error('Use a GitHub repository URL such as https://github.com/owner/repo');

      const repoPayload = {
        github_repo_id: `${owner}/${repoName}`,
        name: repoName,
        full_name: `${owner}/${repoName}`,
        default_branch: 'main',
        language: 'unknown',
        visibility: 'public',
        clone_url: `https://github.com/${owner}/${repoName}.git`,
      };

      await apiClient.addRepository(repoPayload);
      await loadRepositories();
      setToastMessage(`${repoName} was added successfully.`);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to add repository';
      setError(message);
      console.error('Error adding repository:', err);
    } finally {
      setIsLoading(false);
    }
  }, [loadRepositories]);

  // Trigger scan
  const triggerScan = useCallback(async (repositoryId: number) => {
    try {
      setIsScanning(true);
      setActiveScanRepo(String(repositoryId));

      // Look up the repo to get its clone URL
      const repo = repositories.find(r => String(r.id ?? r.github_repo_id ?? r.full_name) === String(repositoryId));
      let scanResult: any;

      if (repo?.clone_url) {
        scanResult = await apiClient.createScanByName(repo.clone_url);
      } else {
        scanResult = await apiClient.createScan(repositoryId);
      }

      // Extract findings if included in the scan response
      if (scanResult?.findings?.length) {
        const scanFindings = scanResult.findings.map((f: any) => ({
          ...f,
          repoId: String(repositoryId),
        }));
        setFindings(prev => [
          ...prev.filter(f => f.repoId !== String(repositoryId)),
          ...scanFindings,
        ]);
      }

      setScans(prev => [scanResult, ...prev.filter(s => s.scan_id !== scanResult.scan_id)]);
      await loadScans();
      notifyUser('Scan complete', `${repo?.full_name || 'Repository'} scan is complete and the summary is ready.`);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to trigger scan';
      setError(message);
      console.error('Error triggering scan:', err);
    } finally {
      setIsScanning(false);
      setActiveScanRepo(null);
    }
  }, [repositories, loadScans, notifyUser]);

  // Send chat message (AI Assistant) — real API call
  const sendChatMessage = useCallback((text: string) => {
    if (!text.trim()) return;

    const userMsg: ChatMessage = {
      id: `msg-user-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString(),
    };
    setChatMessages(prev => [...prev, userMsg]);

    // Call real AI endpoint
    apiClient.aiChat(text).then(result => {
      const aiMsg: ChatMessage = {
        id: `msg-ai-${Date.now()}`,
        sender: 'ai',
        text: result.response,
        timestamp: new Date().toLocaleTimeString(),
      };
      setChatMessages(prev => [...prev, aiMsg]);
    }).catch(err => {
      const aiMsg: ChatMessage = {
        id: `msg-ai-${Date.now()}`,
        sender: 'ai',
        text: `Error: ${err instanceof Error ? err.message : 'AI request failed'}`,
        timestamp: new Date().toLocaleTimeString(),
      };
      setChatMessages(prev => [...prev, aiMsg]);
    });
  }, []);

  // Export report
  const exportReport = useCallback((repoName: string, format: 'PDF' | 'JSON' | 'CSV') => {
    const filename = `${repoName}_security_report.${format.toLowerCase()}`;
    const blobContent = format === 'JSON' 
      ? JSON.stringify({ repository: repoName, trustScore: 85, scanDate: new Date().toISOString() }, null, 2)
      : `Cryptanium Security Report for ${repoName}\nGenerated At: ${new Date().toLocaleString()}\n`;
    
    const blob = new Blob([blobContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, []);

  // Generate report
  const generateReport = useCallback(async (scanId: string | number) => {
    try {
      setIsLoading(true);
      await apiClient.generateReport(scanId);
      await loadReports();
      notifyUser('Report ready', 'Your security report is ready to download.');
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to generate report';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [loadReports, notifyUser]);

  // Authentication
  const login = useCallback(async (code: string) => {
    try {
      setIsLoading(true);
      const response = await apiClient.login(code);
      if (response.access_token) {
        apiClient.setToken(response.access_token);
        setUser(response.user);
        setIsAuthenticated(true);
        setError(null);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    apiClient.clearToken();
    setUser(null);
    setIsAuthenticated(false);
    setRepositories([]);
    setScans([]);
    setReports([]);
    setChatMessages([]);
  }, []);

  return (
    <SecurityContext.Provider
      value={{
        user,
        repositories,
        findings,
        scans,
        reports,
        chatMessages,
        isScanning,
        activeScanRepo,
        isLoading,
        error,
        toastMessage,
        loadRepositories,
        loadScans,
        loadReports,
        loadDashboard,
        addRepository,
        triggerScan,
        sendChatMessage,
        exportReport,
        generateReport,
        isAuthenticated,
        login,
        logout,
        syncRepositories,
      }}
    >
      {children}
    </SecurityContext.Provider>
  );
};

export const useSecurity = () => {
  const context = useContext(SecurityContext);
  if (context === undefined) {
    throw new Error('useSecurity must be used within a SecurityProvider');
  }
  return context;
};
