<<<<<<< HEAD
import React, { createContext, useContext, useState, useEffect } from 'react';

// Type Definitions
export interface Repository {
  id: string;
  name: string;
  url: string;
  language: string;
  addedTime: string;
  lastScanTime: string;
  trustScore: number;
  isPrivate: boolean;
  status: 'COMPLETED' | 'RUNNING' | 'FAILED' | 'IDLE';
  branch: string;
  icon: string;
  findingsCount: {
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
=======
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiClient } from '../services/api';

// Type Definitions
export interface Repository {
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
>>>>>>> 4c943d647601efa36cd1137173b4fede05ccd9b1
}

export interface Finding {
  id: string;
<<<<<<< HEAD
  repoId: string;
  repoName: string;
  title: string;
  description: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  status: 'Open' | 'Fixed' | 'Ignored';
  tool: string;
  filePath: string;
  line: number;
  codeSnippet: string;
  fixCodeSnippet: string;
  details: string;
  category: 'Vulnerabilities' | 'Secrets' | 'Dependencies' | 'Code Quality';
  date: string;
  detectedAt: string;
  remediation: string;
}

export interface Scan {
  id: string;
  repoId: string;
  repoName: string;
  branch: string;
  status: 'COMPLETED' | 'RUNNING' | 'FAILED';
  trustScore: number;
  scannedAt: string;
}

export interface Report {
  id: string;
  repoId: string;
  repoName: string;
  format: 'PDF' | 'JSON' | 'CSV';
  generatedAt: string;
  size: string;
  trustScore: number;
  status: 'HEALTHY' | 'AT_RISK' | 'CRITICAL';
  findings: { critical: number; high: number; medium: number; low: number };
  summary?: string;
=======
  severity: string;
  description: string;
  file_path: string;
  line_number: number;
  rule_id: string;
  tool?: string;
}

export interface Scan {
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
  id: number;
  scan_id: number;
  report_type: string;
  report_path?: string;
  generated_at: string;
  download_url: string;
>>>>>>> 4c943d647601efa36cd1137173b4fede05ccd9b1
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

<<<<<<< HEAD
interface SecurityContextType {
  user: { name: string; email: string; avatar: string };
=======
interface User {
  id?: number;
  username: string;
  email?: string;
  avatar_url?: string;
}

interface SecurityContextType {
  user: User | null;
>>>>>>> 4c943d647601efa36cd1137173b4fede05ccd9b1
  repositories: Repository[];
  findings: Finding[];
  scans: Scan[];
  reports: Report[];
  chatMessages: ChatMessage[];
  isScanning: boolean;
  activeScanRepo: string | null;
<<<<<<< HEAD
  addRepository: (name: string, url: string, isPrivate: boolean, language: string) => void;
  triggerScan: (repoId: string) => void;
  sendChatMessage: (text: string) => void;
  exportReport: (repoName: string, format: 'PDF' | 'JSON' | 'CSV') => void;
  generateReport: (repoId: string) => Promise<void>;
  isAuthenticated: boolean;
  login: () => Promise<void>;
  logout: () => void;
=======
  isLoading: boolean;
  error: string | null;
  loadRepositories: () => Promise<void>;
  loadScans: () => Promise<void>;
  loadReports: () => Promise<void>;
  loadDashboard: () => Promise<void>;
  addRepository: (url: string) => Promise<void>;
  triggerScan: (repositoryId: number) => Promise<void>;
  sendChatMessage: (text: string) => void;
  exportReport: (repoName: string, format: 'PDF' | 'JSON' | 'CSV') => void;
  generateReport: (scanId: number) => Promise<void>;
  isAuthenticated: boolean;
  login: (code: string) => Promise<void>;
  logout: () => void;
  syncRepositories: () => Promise<void>;
>>>>>>> 4c943d647601efa36cd1137173b4fede05ccd9b1
}

const SecurityContext = createContext<SecurityContextType | undefined>(undefined);

<<<<<<< HEAD
// Initial Mock Data
const initialRepos: Repository[] = [
  {
    id: 'repo-1',
    name: 'payment-service',
    url: 'github.com/alex/payment-service',
    language: 'Python',
    addedTime: '2 hours ago',
    lastScanTime: '2 hours ago',
    trustScore: 82,
    isPrivate: true,
    status: 'COMPLETED',
    branch: 'main',
    icon: 'terminal',
    findingsCount: { total: 128, critical: 17, high: 31, medium: 45, low: 35 }
  },
  {
    id: 'repo-2',
    name: 'ecommerce-web',
    url: 'github.com/alex/ecommerce-web',
    language: 'JavaScript',
    addedTime: '5 hours ago',
    lastScanTime: '5 hours ago',
    trustScore: 68,
    isPrivate: false,
    status: 'COMPLETED',
    branch: 'main',
    icon: 'shopping_cart',
    findingsCount: { total: 242, critical: 5, high: 62, medium: 110, low: 65 }
  },
  {
    id: 'repo-3',
    name: 'user-auth-api',
    url: 'github.com/alex/user-auth-api',
    language: 'Python',
    addedTime: '1 day ago',
    lastScanTime: '1 day ago',
    trustScore: 90,
    isPrivate: true,
    status: 'COMPLETED',
    branch: 'main',
    icon: 'shield_person',
    findingsCount: { total: 42, critical: 0, high: 8, medium: 14, low: 20 }
  },
  {
    id: 'repo-4',
    name: 'machine-learning-app',
    url: 'github.com/alex/ml-app',
    language: 'Python',
    addedTime: '2 days ago',
    lastScanTime: '2 days ago',
    trustScore: 74,
    isPrivate: true,
    status: 'COMPLETED',
    branch: 'main',
    icon: 'psychology',
    findingsCount: { total: 98, critical: 2, high: 18, medium: 44, low: 34 }
  },
  {
    id: 'repo-5',
    name: 'devops-infra',
    url: 'github.com/alex/devops-infra',
    language: 'YAML',
    addedTime: '3 days ago',
    lastScanTime: '3 days ago',
    trustScore: 88,
    isPrivate: true,
    status: 'COMPLETED',
    branch: 'main',
    icon: 'settings_ethernet',
    findingsCount: { total: 15, critical: 0, high: 3, medium: 8, low: 4 }
  }
];

const initialFindings: Finding[] = [
  {
    id: 'find-1',
    repoId: 'repo-1',
    repoName: 'payment-service',
    title: 'Hardcoded AWS Secret Detected',
    description: 'Potentially exposed cloud credentials in source code configuration.',
    severity: 'Critical',
    status: 'Open',
    tool: 'Gitleaks',
    filePath: 'src/config/aws_client.js',
    line: 24,
    codeSnippet: `23 | // Initialize AWS config\n24 | const AWS_SECRET_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE";\n25 | const client = new AWS.Client({ secret: AWS_SECRET_ACCESS_KEY });`,
    fixCodeSnippet: `// Load from environment variables instead\nconst AWS_SECRET_ACCESS_KEY = process.env.AWS_SECRET_ACCESS_KEY;\nconst client = new AWS.Client({ secret: AWS_SECRET_ACCESS_KEY });`,
    details: 'Gitleaks detected a high-entropy string matching typical AWS secret signatures.',
    category: 'Secrets',
    date: '2 hours ago',
    detectedAt: 'May 20, 2024',
    remediation: 'Remove the hardcoded secret and load it from environment variables or a secrets manager like AWS Secrets Manager or HashiCorp Vault.'
  },
  {
    id: 'find-2',
    repoId: 'repo-1',
    repoName: 'payment-service',
    title: 'SQL Injection Vulnerability',
    description: 'User input directly used in DB query without sanitization or preparation.',
    severity: 'High',
    status: 'Open',
    tool: 'Semgrep',
    filePath: 'api/controllers/user.controller.py',
    line: 142,
    codeSnippet: `141 | userId = request.params.get('userId')\n142 | query = f"SELECT * FROM users WHERE id = '{userId}'"\n143 | cursor.execute(query)`,
    fixCodeSnippet: `userId = request.params.get('userId')\nquery = "SELECT * FROM users WHERE id = %s"\ncursor.execute(query, (userId,))`,
    details: 'Semgrep rule python.sqlalchemy.security.audit.raw-sql-concat-injection.',
    category: 'Vulnerabilities',
    date: '2 hours ago',
    detectedAt: 'May 20, 2024',
    remediation: 'Use parameterized queries (prepared statements) instead of string concatenation. Never concatenate user input directly into SQL.'
  },
  {
    id: 'find-3',
    repoId: 'repo-1',
    repoName: 'payment-service',
    title: 'Insecure Use of Subprocess',
    description: 'Shell=True used in external command execution which enables command injection.',
    severity: 'High',
    status: 'Ignored',
    tool: 'Bandit',
    filePath: 'scripts/deploy_runner.py',
    line: 88,
    codeSnippet: `87 | deploy_cmd = f"ansible-playbook -i hosts {target_playbook}"\n88 | subprocess.call(deploy_cmd, shell=True)\n89 | print("Deployed successfully!")`,
    fixCodeSnippet: `deploy_cmd = ["ansible-playbook", "-i", "hosts", target_playbook]\nsubprocess.call(deploy_cmd, shell=False)`,
    details: 'Bandit scan category B602. Spawning subprocesses using shell=True is dangerous.',
    category: 'Vulnerabilities',
    date: '2 hours ago',
    detectedAt: 'May 20, 2024',
    remediation: 'Pass commands as a list with shell=False to prevent shell injection attacks.'
  },
  {
    id: 'find-4',
    repoId: 'repo-2',
    repoName: 'ecommerce-web',
    title: 'Outdated Dependency: lodash',
    description: 'Lodash versions < 4.17.21 contain a critical prototype pollution flaw.',
    severity: 'Medium',
    status: 'Fixed',
    tool: 'npm audit',
    filePath: 'package-lock.json',
    line: 1,
    codeSnippet: `"lodash": {\n  "version": "4.17.15"\n}`,
    fixCodeSnippet: `"lodash": "^4.17.21"`,
    details: 'CVE-2023-45133 prototype pollution in lodash.',
    category: 'Dependencies',
    date: '5 hours ago',
    detectedAt: 'May 20, 2024',
    remediation: 'Run npm update lodash or upgrade the dependency to version ^4.17.21 in package.json.'
  },
  {
    id: 'find-5',
    repoId: 'repo-2',
    repoName: 'ecommerce-web',
    title: 'Insecure JWT Verification Algorithm',
    description: 'JWT verification configured to accept "none" algorithm.',
    severity: 'Critical',
    status: 'Open',
    tool: 'Semgrep',
    filePath: 'src/auth/jwt.js',
    line: 45,
    codeSnippet: `44 | const verifyOptions = { algorithms: ['HS256', 'none'] };\n45 | const payload = jwt.verify(token, SECRET_KEY, verifyOptions);`,
    fixCodeSnippet: `const verifyOptions = { algorithms: ['HS256'] };\nconst payload = jwt.verify(token, SECRET_KEY, verifyOptions);`,
    details: 'Allowing the "none" algorithm enables users to bypass signature verification.',
    category: 'Vulnerabilities',
    date: '5 hours ago',
    detectedAt: 'May 20, 2024',
    remediation: 'Remove "none" from the accepted algorithms list. Only allow explicitly trusted algorithms like HS256 or RS256.'
  },
  {
    id: 'find-6',
    repoId: 'repo-4',
    repoName: 'machine-learning-app',
    title: 'Deserialization of Untrusted Data',
    description: 'Unpickling user-uploaded files without validation.',
    severity: 'High',
    status: 'Open',
    tool: 'Bandit',
    filePath: 'app/models/predictor.py',
    line: 12,
    codeSnippet: `11 | model_file = request.files['model'].stream\n12 | model = pickle.load(model_file)\n13 | return model.predict(data)`,
    fixCodeSnippet: `// Use safe file formats like ONNX or Protocol Buffers`,
    details: 'Pickle deserialization allows execution of arbitrary bytecode.',
    category: 'Vulnerabilities',
    date: '2 days ago',
    detectedAt: 'May 18, 2024',
    remediation: 'Avoid using pickle for deserialization of user-supplied data. Use safer alternatives like JSON, ONNX, or Protocol Buffers with signature verification.'
  }
];

const initialScans: Scan[] = [
  { id: 'scan-1', repoId: 'repo-1', repoName: 'payment-service', branch: 'main', status: 'COMPLETED', trustScore: 82, scannedAt: '2 hours ago' },
  { id: 'scan-2', repoId: 'repo-2', repoName: 'ecommerce-web', branch: 'main', status: 'COMPLETED', trustScore: 68, scannedAt: '5 hours ago' },
  { id: 'scan-3', repoId: 'repo-3', repoName: 'user-auth-api', branch: 'main', status: 'COMPLETED', trustScore: 90, scannedAt: '1 day ago' },
  { id: 'scan-4', repoId: 'repo-4', repoName: 'machine-learning-app', branch: 'main', status: 'COMPLETED', trustScore: 74, scannedAt: '2 days ago' },
  { id: 'scan-5', repoId: 'repo-5', repoName: 'devops-infra', branch: 'main', status: 'COMPLETED', trustScore: 88, scannedAt: '3 days ago' }
];

const initialReports: Report[] = [
  { id: 'rep-1', repoId: 'repo-1', repoName: 'payment-service', format: 'PDF', generatedAt: 'May 20, 2024 10:30 AM', size: '1.2 MB', trustScore: 82, status: 'AT_RISK', findings: { critical: 17, high: 31, medium: 45, low: 35 }, summary: 'The payment-service has notable security risks including hardcoded credentials and SQL injection vulnerabilities. Immediate action is required on the critical findings.' },
  { id: 'rep-2', repoId: 'repo-3', repoName: 'user-auth-api', format: 'PDF', generatedAt: 'May 19, 2024 04:20 PM', size: '1.1 MB', trustScore: 90, status: 'HEALTHY', findings: { critical: 0, high: 8, medium: 14, low: 20 }, summary: 'The user-auth-api is in excellent health with no critical vulnerabilities. Minor improvements recommended for some medium and low severity findings.' },
  { id: 'rep-3', repoId: 'repo-5', repoName: 'devops-infra', format: 'CSV', generatedAt: 'May 17, 2024 09:45 AM', size: '2.4 MB', trustScore: 88, status: 'HEALTHY', findings: { critical: 0, high: 3, medium: 8, low: 4 }, summary: 'The devops-infra repository shows good security practices. A few infrastructure-level hardening recommendations have been flagged for review.' }
];

export const SecurityProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [repositories, setRepositories] = useState<Repository[]>(initialRepos);
  const [findings, setFindings] = useState<Finding[]>(initialFindings);
  const [scans, setScans] = useState<Scan[]>(initialScans);
  const [reports, setReports] = useState<Report[]>(initialReports);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [activeScanRepo, setActiveScanRepo] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('cryptanium_auth') === 'true';
  });

  const user = {
    name: 'Alex Developer',
    email: 'alex@example.com',
    avatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&q=80&w=200'
  };

  useEffect(() => {
    if (chatMessages.length === 0) {
      setChatMessages([
        {
          id: 'msg-init',
          sender: 'ai',
          text: `Hello Alex. I've completed a deep scan of the payment-service repository.\n\nI detected a critical security flaw in your authentication flow. In auth.service.js, user input is being directly concatenated into a database query. This makes the system vulnerable to a SQL Injection attack.`,
          codeSnippet: {
            title: 'Vulnerable Code Segment',
            code: `44 | const query = \`SELECT * FROM users WHERE id = '\${userId}'\`;\n45 | const result = await db.execute(query);`
          },
          timestamp: '2 hours ago'
        }
      ]);
    }
  }, []);

  const login = async () => {
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        setIsAuthenticated(true);
        localStorage.setItem('cryptanium_auth', 'true');
        resolve();
      }, 1500);
    });
  };

  const logout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('cryptanium_auth');
  };

  const addRepository = (name: string, url: string, isPrivate: boolean, language: string) => {
    const newRepoId = `repo-${Date.now()}`;
    const newRepo: Repository = {
      id: newRepoId,
      name,
      url,
      language,
      addedTime: 'Just now',
      lastScanTime: 'Never',
      trustScore: 100,
      isPrivate,
      status: 'IDLE',
      branch: 'main',
      icon: 'terminal',
      findingsCount: { total: 0, critical: 0, high: 0, medium: 0, low: 0 }
    };

    setRepositories((prev) => [newRepo, ...prev]);

    // Automatically trigger scan after adding
    setTimeout(() => {
      triggerScan(newRepoId);
    }, 500);
  };

  const triggerScan = (repoId: string) => {
    setIsScanning(true);
    setActiveScanRepo(repoId);

    setRepositories((prev) =>
      prev.map((r) => (r.id === repoId ? { ...r, status: 'RUNNING', lastScanTime: 'Scanning...' } : r))
    );

    // Add running scan
    const newScanId = `scan-${Date.now()}`;
    const targetRepo = repositories.find((r) => r.id === repoId);
    const newScan: Scan = {
      id: newScanId,
      repoId,
      repoName: targetRepo ? targetRepo.name : 'Unknown',
      branch: 'main',
      status: 'RUNNING',
      trustScore: 100,
      scannedAt: 'Just now'
    };
    setScans((prev) => [newScan, ...prev]);

    // Simulate scan execution
    setTimeout(() => {
      // Complete Scan
      const simulatedScore = Math.floor(Math.random() * 25) + 70; // 70 to 95
      const critical = Math.random() > 0.6 ? 1 : 0;
      const high = Math.floor(Math.random() * 3);
      const medium = Math.floor(Math.random() * 8) + 2;
      const low = Math.floor(Math.random() * 12) + 5;
      const total = critical + high + medium + low;

      setRepositories((prev) =>
        prev.map((r) =>
          r.id === repoId
            ? {
                ...r,
                status: 'COMPLETED',
                trustScore: simulatedScore,
                lastScanTime: 'Just now',
                findingsCount: { total, critical, high, medium, low }
              }
            : r
        )
      );

      setScans((prev) =>
        prev.map((s) =>
          s.id === newScanId
            ? {
                ...s,
                status: 'COMPLETED',
                trustScore: simulatedScore,
                scannedAt: 'Just now'
              }
            : s
        )
      );

      // Add a mock finding for this scan
      if (total > 0) {
        const repoObj = repositories.find((r) => r.id === repoId) || targetRepo;
        const newFinding: Finding = {
          id: `find-new-${Date.now()}`,
          repoId,
          repoName: repoObj ? repoObj.name : 'Unknown',
          title: critical > 0 ? 'Hardcoded Credential Exposing Secret' : 'Outdated Module Dependency',
          description: critical > 0 ? 'Exposed credentials detected in setup file.' : 'Vulnerable component dependency detected.',
          severity: critical > 0 ? 'Critical' : high > 0 ? 'High' : 'Medium',
          tool: critical > 0 ? 'Gitleaks' : 'npm audit',
          filePath: repoObj?.language === 'JavaScript' ? 'src/index.js' : 'app/config.py',
          line: 12,
          codeSnippet: `11 | // Setup configurations\n12 | const API_KEY = "sk-live-28492019348123";\n13 | const config = { key: API_KEY };`,
          fixCodeSnippet: `// Setup configurations\nconst API_KEY = process.env.API_KEY;\nconst config = { key: API_KEY };`,
          details: 'Automatic scanner alerts. Secrets should be securely managed.',
          category: critical > 0 ? 'Secrets' : 'Dependencies',
          date: 'Just now'
        };
        setFindings((prev) => [newFinding, ...prev]);
      }

      setIsScanning(false);
      setActiveScanRepo(null);
    }, 4000); // 4 seconds simulated scan duration
  };

  const sendChatMessage = (text: string) => {
=======
export const SecurityProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [scans, setScans] = useState<Scan[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [activeScanRepo, setActiveScanRepo] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem('cryptanium_token');
  });

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
      setIsLoading(true);
      const data = await apiClient.getRepositories();
      setRepositories(data || []);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load repositories';
      setError(message);
      console.error('Error loading repositories:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load scans
  const loadScans = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getScans();
      setScans(data || []);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load scans';
      setError(message);
      console.error('Error loading scans:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load reports
  const loadReports = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.getReports();
      setReports(data || []);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load reports';
      setError(message);
      console.error('Error loading reports:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load dashboard
  const loadDashboard = useCallback(async () => {
    try {
      setIsLoading(true);
      await Promise.all([loadRepositories(), loadScans(), loadReports()]);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load dashboard';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [loadRepositories, loadScans, loadReports]);

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

  // Add repository (stub for future implementation)
  const addRepository = useCallback(async (url: string) => {
    console.log('Adding repository:', url);
    await loadRepositories();
  }, [loadRepositories]);

  // Trigger scan
  const triggerScan = useCallback(async (repositoryId: number) => {
    try {
      setIsScanning(true);
      setActiveScanRepo(String(repositoryId));
      const scanResult = await apiClient.createScan(repositoryId);
      setScans(prev => [scanResult, ...prev]);
      await loadScans();
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to trigger scan';
      setError(message);
      console.error('Error triggering scan:', err);
    } finally {
      setIsScanning(false);
      setActiveScanRepo(null);
    }
  }, [loadScans]);

  // Send chat message (AI Assistant)
  const sendChatMessage = useCallback((text: string) => {
>>>>>>> 4c943d647601efa36cd1137173b4fede05ccd9b1
    if (!text.trim()) return;

    const userMsg: ChatMessage = {
      id: `msg-user-${Date.now()}`,
      sender: 'user',
      text,
<<<<<<< HEAD
      timestamp: 'Just now'
    };

    setChatMessages((prev) => [...prev, userMsg]);

    // Simulate AI response
    setTimeout(() => {
      let aiText = `I've analyzed your question. Regarding this repository, security configurations are healthy. Let me know if you would like me to audit any other specific controllers.`;
      let codeSnippet = undefined;

      const lowerText = text.toLowerCase();
      if (lowerText.includes('sql') || lowerText.includes('secure') || lowerText.includes('fix')) {
        aiText = `Certainly. To mitigate SQL injection, you should always use parameterized queries (also known as prepared statements). Here is the recommended fix using standard PostgreSQL placeholders:`;
        codeSnippet = {
          title: 'Recommended Fix',
          code: `44 | const text = 'SELECT * FROM users WHERE id = $1';\n45 | const values = [userId];\n46 | const result = await db.query(text, values);`,
          isFix: true
        };
      } else if (lowerText.includes('secret') || lowerText.includes('aws')) {
        aiText = `To fix the hardcoded AWS secret, you should remove the raw credentials from your code and load them from environment variables instead. Let's write a safe environment configuration:`;
        codeSnippet = {
          title: 'Secure Credentials Loading',
          code: `const AWS_SECRET_ACCESS_KEY = process.env.AWS_SECRET_ACCESS_KEY;\nconst client = new AWS.Client({ secret: AWS_SECRET_ACCESS_KEY });`,
          isFix: true
        };
      }

      const aiMsg: ChatMessage = {
        id: `msg-ai-${Date.now()}`,
        sender: 'ai',
        text: aiText,
        codeSnippet,
        timestamp: 'Just now'
      };

      setChatMessages((prev) => [...prev, aiMsg]);
    }, 1500);
  };

  const generateReport = async (repoId: string): Promise<void> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const repo = repositories.find(r => r.id === repoId);
        if (!repo) { resolve(); return; }
        const score = repo.trustScore;
        const status: Report['status'] = score >= 80 ? 'HEALTHY' : score >= 60 ? 'AT_RISK' : 'CRITICAL';
        const newReport: Report = {
          id: `rep-${Date.now()}`,
          repoId,
          repoName: repo.name,
          format: 'PDF',
          generatedAt: new Date().toLocaleString(),
          size: '1.1 MB',
          trustScore: score,
          status,
          findings: repo.findingsCount,
          summary: `Security analysis complete for ${repo.name}. Trust score: ${score}/100. ${repo.findingsCount.critical} critical issue(s) require immediate attention.`
        };
        setReports(prev => [newReport, ...prev.filter(r => r.repoId !== repoId)]);
        resolve();
      }, 2000);
    });
  };

  const exportReport = (repoName: string, format: 'PDF' | 'JSON' | 'CSV') => {
    // Simulate generation loading state, then trigger mock browser download
    const filename = `${repoName}_security_report.${format.toLowerCase()}`;
    const blobContent = format === 'JSON' 
      ? JSON.stringify({ repository: repoName, trustScore: 82, scanDate: new Date().toISOString(), findings: [] }, null, 2)
      : `Cryptanium Security Report for ${repoName}\nGenerated At: ${new Date().toLocaleString()}\nTrust Score: 82/100\n`;
=======
      timestamp: new Date().toLocaleTimeString(),
    };

    setChatMessages(prev => [...prev, userMsg]);

    // Simulate AI response
    setTimeout(() => {
      const aiMsg: ChatMessage = {
        id: `msg-ai-${Date.now()}`,
        sender: 'ai',
        text: 'I am the Cryptanium AI Assistant. I can help you understand your security findings and provide remediation guidance. Please ask me about any vulnerabilities in your scans.',
        timestamp: new Date().toLocaleTimeString(),
      };
      setChatMessages(prev => [...prev, aiMsg]);
    }, 1000);
  }, []);

  // Export report
  const exportReport = useCallback((repoName: string, format: 'PDF' | 'JSON' | 'CSV') => {
    const filename = `${repoName}_security_report.${format.toLowerCase()}`;
    const blobContent = format === 'JSON' 
      ? JSON.stringify({ repository: repoName, trustScore: 85, scanDate: new Date().toISOString() }, null, 2)
      : `Cryptanium Security Report for ${repoName}\nGenerated At: ${new Date().toLocaleString()}\n`;
>>>>>>> 4c943d647601efa36cd1137173b4fede05ccd9b1
    
    const blob = new Blob([blobContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
<<<<<<< HEAD

    // Add to reports list
    const newReport: Report = {
      id: `rep-${Date.now()}`,
      repoName,
      format,
      generatedAt: new Date().toLocaleString(),
      size: format === 'JSON' ? '12 KB' : '1.1 MB'
    };
    setReports((prev) => [newReport, ...prev]);
  };
=======
  }, []);

  // Generate report
  const generateReport = useCallback(async (scanId: number) => {
    try {
      setIsLoading(true);
      await apiClient.downloadReport(scanId);
      await loadReports();
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to generate report';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [loadReports]);

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
>>>>>>> 4c943d647601efa36cd1137173b4fede05ccd9b1

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
<<<<<<< HEAD
=======
        isLoading,
        error,
        loadRepositories,
        loadScans,
        loadReports,
        loadDashboard,
>>>>>>> 4c943d647601efa36cd1137173b4fede05ccd9b1
        addRepository,
        triggerScan,
        sendChatMessage,
        exportReport,
        generateReport,
        isAuthenticated,
        login,
<<<<<<< HEAD
        logout
=======
        logout,
        syncRepositories,
>>>>>>> 4c943d647601efa36cd1137173b4fede05ccd9b1
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
