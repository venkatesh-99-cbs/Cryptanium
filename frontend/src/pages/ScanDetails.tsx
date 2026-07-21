import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSecurity } from '../context/SecurityContext';
import { apiClient } from '../services/api';

interface AIAnalysis {
  executive_summary: string;
  risk_level: string;
  key_concerns: string[];
  recommendations: Array<{
    priority: number;
    title: string;
    finding_type: string;
    action: string;
    severity: string;
  }>;
}

const ScanDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { scans } = useSecurity();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<'summary' | 'findings' | 'ai'>('findings');
  const [filterText, setFilterText] = useState('');
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);

  // Find the scan by ID
  const scan = scans.find(s => String(s.scan_id) === String(id));

  // Load AI analysis when Summary/AI tab is active
  useEffect(() => {
    if ((activeTab === 'ai' || activeTab === 'summary') && scan && !aiAnalysis && !aiLoading) {
      void loadAIAnalysis();
    }
  }, [activeTab, scan]);

  const loadAIAnalysis = async () => {
    if (!scan) return;
    setAiLoading(true);
    setAiError(null);
    try {
      // Try fetching existing AI summary first
      const data = await apiClient.getAISummary(scan.scan_id);
      setAiAnalysis(data as unknown as AIAnalysis);
    } catch {
      // Generate fresh AI analysis
      try {
        const data = await apiClient.analyzeScan(scan.scan_id);
        setAiAnalysis(data as unknown as AIAnalysis);
      } catch (err) {
        setAiError(err instanceof Error ? err.message : 'Failed to generate AI analysis');
      }
    } finally {
      setAiLoading(false);
    }
  };

  if (!scan) {
    return (
      <div className="flex items-center justify-center h-64 text-on-surface-variant">
        <div className="text-center">
          <span className="material-symbols-outlined text-[48px] block mb-md opacity-40">search_off</span>
          <p className="font-bold">Scan not found</p>
          <p className="text-sm opacity-60">Scan ID: {id}</p>
          <button onClick={() => navigate('/scans')} className="mt-md text-primary hover:underline">
            Back to Scans
          </button>
        </div>
      </div>
    );
  }

  const findings = (scan as any).findings || [];
  const filteredFindings = findings.filter((f: any) =>
    (f.description || '').toLowerCase().includes(filterText.toLowerCase()) ||
    (f.tool || '').toLowerCase().includes(filterText.toLowerCase()) ||
    (f.severity || '').toLowerCase().includes(filterText.toLowerCase())
  );

  const getSeverityClass = (sev: string) => {
    switch (sev?.toLowerCase()) {
      case 'critical': return 'severity-critical';
      case 'high': return 'severity-high';
      case 'medium': return 'severity-medium';
      default: return 'severity-low';
    }
  };

  const score = scan.trust_score || 0;
  const scoreColor = score >= 80 ? 'text-secondary' : score >= 60 ? 'text-tertiary' : 'text-error';
  const scoreBorderColor = score >= 80
    ? 'border-secondary/20 bg-secondary/10'
    : score >= 60 ? 'border-tertiary/20 bg-tertiary/10'
    : 'border-error/20 bg-error/10';

  const critCount = findings.filter((f: any) => f.severity?.toLowerCase() === 'critical').length;
  const highCount = findings.filter((f: any) => f.severity?.toLowerCase() === 'high').length;
  const medCount = findings.filter((f: any) => f.severity?.toLowerCase() === 'medium').length;
  const lowCount = findings.filter((f: any) => f.severity?.toLowerCase() === 'low').length;

  const riskColors: Record<string, string> = {
    Critical: 'text-error bg-error/10 border-error/20',
    High: 'text-tertiary bg-tertiary/10 border-tertiary/20',
    Moderate: 'text-[#ffcc00] bg-[#ffcc00]/10 border-[#ffcc00]/20',
    Low: 'text-secondary bg-secondary/10 border-secondary/20',
    Unknown: 'text-outline bg-surface-container border-outline-variant',
  };

  return (
    <div className="flex-1">
      {/* Breadcrumbs */}
      <div className="flex items-center text-on-surface-variant font-label-caps gap-xs uppercase tracking-widest text-[10px] mb-xl">
        <button onClick={() => navigate('/scans')} className="hover:text-primary transition-colors">Scans</button>
        <span className="material-symbols-outlined text-[14px]">chevron_right</span>
        <span>{scan.repository_name}</span>
        <span className="material-symbols-outlined text-[14px]">chevron_right</span>
        <span className="text-primary">Scan Details</span>
      </div>

      {/* Header */}
      <div className="flex justify-between items-start mb-xl flex-wrap gap-lg">
        <div className="flex items-center gap-lg">
          <div className="w-16 h-16 rounded-xl bg-surface-container-highest flex items-center justify-center border border-outline-variant">
            <span className="material-symbols-outlined text-[40px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
              account_tree
            </span>
          </div>
          <div>
            <h1 className="text-headline-lg font-headline-lg text-on-background flex items-center gap-sm flex-wrap">
              {scan.repository_name}
              <span className="bg-surface-container text-outline-variant text-[10px] px-2 py-0.5 rounded border border-outline-variant font-label-caps uppercase">
                {scan.status}
              </span>
            </h1>
            <div className="flex items-center gap-md mt-sm text-on-surface-variant">
              <div className="flex items-center gap-xs">
                <span className="material-symbols-outlined text-[16px]">schedule</span>
                <span className="text-sm">
                  {scan.completed_at ? new Date(scan.completed_at).toLocaleString() : 'In progress'}
                </span>
              </div>
              <div className="w-1 h-1 rounded-full bg-outline-variant" />
              <div className="flex items-center gap-xs">
                <span className="material-symbols-outlined text-[16px]">bug_report</span>
                <span className="text-sm">{scan.findings_count} findings</span>
              </div>
            </div>
          </div>
        </div>

        {/* Trust Score */}
        <div className="flex flex-col items-end">
          <div className={`flex items-center gap-sm border px-4 py-2 rounded-xl ${scoreBorderColor}`}>
            <div className="flex flex-col items-end">
              <span className={`font-label-caps text-[10px] ${scoreColor}`}>Trust Score</span>
              <span className={`text-headline-md font-headline-md font-bold ${scoreColor}`}>
                {score > 0 ? `${score}/100` : '--'}
              </span>
            </div>
            <div className="w-10 h-10 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90">
                <circle className="text-surface-container-highest" cx="20" cy="20" fill="transparent" r="18" stroke="currentColor" strokeWidth="3" />
                <circle className={scoreColor} cx="20" cy="20" fill="transparent" r="18" stroke="currentColor"
                  strokeDasharray="113.1"
                  strokeDashoffset={score > 0 ? 113.1 - (score / 100) * 113.1 : 113.1}
                  strokeWidth="3"
                />
              </svg>
            </div>
          </div>
          <span className={`mt-2 text-[11px] font-label-caps ${scoreColor}`}>
            {score >= 80 ? 'Healthy' : score >= 60 ? 'Fair' : score > 0 ? 'Critical' : 'Pending'}
          </span>
        </div>
      </div>

      {/* Tabs & Finding Counters */}
      <div className="flex items-center justify-between border-b border-outline-variant mb-lg flex-wrap gap-sm">
        <div className="flex gap-xl">
          {(['findings', 'ai', 'summary'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-4 px-2 font-body-md font-bold border-b-2 transition-all capitalize ${
                activeTab === tab ? 'text-primary border-primary' : 'text-on-surface-variant border-transparent hover:text-on-surface'
              }`}
            >
              {tab === 'ai' ? 'AI Analysis' : tab}
            </button>
          ))}
        </div>
        <div className="flex gap-sm mb-2">
          {[
            { label: 'Total', value: scan.findings_count, icon: 'bug_report', color: 'text-primary' },
            { label: 'Critical', value: critCount, dot: 'bg-error' },
            { label: 'High', value: highCount, dot: 'bg-tertiary' },
            { label: 'Medium', value: medCount, dot: 'bg-[#ffcc00]' },
            { label: 'Low', value: lowCount, dot: 'bg-secondary' },
          ].map(item => (
            <div key={item.label} className="bg-surface-container px-3 py-1.5 rounded-lg border border-outline-variant flex items-center gap-sm">
              {item.icon
                ? <span className={`material-symbols-outlined ${item.color} text-[18px]`}>{item.icon}</span>
                : <span className={`w-2 h-2 rounded-full ${item.dot}`} />
              }
              <span className="text-on-background font-bold text-sm">{item.value}</span>
              <span className="text-outline text-[11px] font-label-caps">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── AI Analysis Tab ── */}
      {activeTab === 'ai' && (
        <div className="space-y-lg">
          {aiLoading && (
            <div className="flex flex-col items-center justify-center py-xl text-on-surface-variant">
              <div className="w-12 h-12 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center mb-lg animate-pulse">
                <span className="material-symbols-outlined text-[28px] text-primary">smart_toy</span>
              </div>
              <p className="font-bold">Generating AI Analysis...</p>
              <p className="text-sm opacity-60 mt-1">Using nvidia/nemotron-4-340b-instruct via OpenRouter</p>
            </div>
          )}

          {aiError && (
            <div className="glass-card rounded-xl p-lg border-l-4 border-error">
              <div className="flex items-start gap-md">
                <span className="material-symbols-outlined text-error text-[28px]">error</span>
                <div>
                  <p className="font-bold text-error">AI Analysis Failed</p>
                  <p className="text-sm text-on-surface-variant mt-1">{aiError}</p>
                  <p className="text-xs text-on-surface-variant mt-2 opacity-60">
                    Ensure OPENROUTER_API_KEY is set in your .env file.
                  </p>
                  <button
                    onClick={loadAIAnalysis}
                    className="mt-md text-primary text-sm hover:underline flex items-center gap-xs"
                  >
                    <span className="material-symbols-outlined text-[14px]">refresh</span> Retry
                  </button>
                </div>
              </div>
            </div>
          )}

          {aiAnalysis && !aiLoading && (
            <>
              {/* Executive Summary */}
              <div className="glass-card rounded-xl p-lg">
                <div className="flex items-center justify-between mb-md">
                  <h3 className="font-headline-md font-semibold flex items-center gap-sm">
                    <span className="material-symbols-outlined text-primary text-[22px]">summarize</span>
                    Executive Summary
                  </h3>
                  <span className={`text-[11px] font-bold px-3 py-1 rounded-full border ${riskColors[aiAnalysis.risk_level] || riskColors.Unknown}`}>
                    {aiAnalysis.risk_level} Risk
                  </span>
                </div>
                <p className="text-on-surface text-sm leading-relaxed">{aiAnalysis.executive_summary}</p>

                {aiAnalysis.key_concerns.length > 0 && (
                  <div className="mt-lg">
                    <p className="text-[11px] font-label-caps text-on-surface-variant mb-sm uppercase tracking-wider">Key Concerns</p>
                    <ul className="space-y-sm">
                      {aiAnalysis.key_concerns.map((concern, i) => (
                        <li key={i} className="flex items-start gap-sm text-sm text-on-surface">
                          <span className="material-symbols-outlined text-error text-[16px] mt-0.5 shrink-0">warning</span>
                          {concern}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Recommendations */}
              {aiAnalysis.recommendations.length > 0 && (
                <div className="glass-card rounded-xl overflow-hidden">
                  <div className="p-lg border-b border-outline-variant">
                    <h3 className="font-headline-md font-semibold flex items-center gap-sm">
                      <span className="material-symbols-outlined text-primary text-[22px]">checklist</span>
                      Prioritized Recommendations ({aiAnalysis.recommendations.length})
                    </h3>
                  </div>
                  <div className="divide-y divide-outline-variant/30">
                    {aiAnalysis.recommendations.map((rec, i) => (
                      <div key={i} className="p-lg flex gap-lg hover:bg-surface-container/30 transition-colors">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 font-bold text-sm ${
                          rec.severity === 'Critical' ? 'bg-error/10 text-error border border-error/20' :
                          rec.severity === 'High' ? 'bg-tertiary/10 text-tertiary border border-tertiary/20' :
                          'bg-primary/10 text-primary border border-primary/20'
                        }`}>
                          {rec.priority}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-md flex-wrap">
                            <div>
                              <p className="font-bold text-sm text-on-background">{rec.title}</p>
                              <p className="text-[11px] font-label-caps text-outline mt-0.5">{rec.finding_type}</p>
                            </div>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded border shrink-0 ${
                              rec.severity === 'Critical' ? 'bg-error/10 text-error border-error/20' :
                              rec.severity === 'High' ? 'bg-tertiary/10 text-tertiary border-tertiary/20' :
                              rec.severity === 'Medium' ? 'bg-[#ffcc00]/10 text-[#ffcc00] border-[#ffcc00]/20' :
                              'bg-secondary/10 text-secondary border-secondary/20'
                            }`}>
                              {rec.severity}
                            </span>
                          </div>
                          <p className="text-sm text-on-surface-variant mt-sm leading-relaxed">{rec.action}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {!aiAnalysis && !aiLoading && !aiError && (
            <div className="glass-card rounded-xl p-xl text-center">
              <span className="material-symbols-outlined text-[48px] text-primary opacity-40 block mb-md">smart_toy</span>
              <p className="font-bold text-on-background">AI Analysis Not Generated Yet</p>
              <p className="text-sm text-on-surface-variant mt-sm">Click below to run AI analysis on this scan's findings.</p>
              <button
                onClick={loadAIAnalysis}
                className="mt-lg px-6 py-2 bg-primary text-on-primary rounded-lg font-bold text-sm hover:opacity-90 transition-opacity"
              >
                Generate AI Analysis
              </button>
            </div>
          )}
        </div>
      )}

      {/* ── Summary Tab ── */}
      {activeTab === 'summary' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">
          {[
            { title: 'Total Findings', score: scan.findings_count, icon: 'bug_report', color: 'text-primary', isCount: true },
            { title: 'Critical', score: critCount, icon: 'dangerous', color: 'text-error', isCount: true },
            { title: 'High', score: highCount, icon: 'warning', color: 'text-tertiary', isCount: true },
            { title: 'Medium', score: medCount, icon: 'crisis_alert', color: 'text-[#ffcc00]', isCount: true },
            { title: 'Low', score: lowCount, icon: 'info', color: 'text-secondary', isCount: true },
            { title: 'Trust Score', score: score, icon: 'verified_user', color: scoreColor, isCount: false },
          ].map(card => (
            <div key={card.title} className="glass-card rounded-xl p-lg">
              <div className="flex items-center justify-between mb-md">
                <span className={`material-symbols-outlined ${card.color} text-[28px]`}>{card.icon}</span>
                <span className={`font-bold text-xl ${card.color}`}>
                  {card.isCount ? card.score : `${card.score}/100`}
                </span>
              </div>
              <h4 className="font-bold text-on-background mb-sm">{card.title}</h4>
              {!card.isCount && (
                <div className="w-full bg-surface-container-highest h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${card.score >= 80 ? 'bg-secondary' : card.score >= 60 ? 'bg-tertiary' : 'bg-error'}`}
                    style={{ width: `${card.score}%` }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── Findings Tab ── */}
      {activeTab === 'findings' && (
        <div className="glass-card rounded-xl overflow-hidden">
          <div className="p-md bg-surface-container-high/50 border-b border-outline-variant flex justify-between items-center">
            <div className="flex items-center gap-md">
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">search</span>
                <input
                  className="bg-background border border-outline-variant rounded-lg pl-10 pr-4 py-1.5 text-body-md w-64 focus:border-primary outline-none transition-all"
                  placeholder="Filter findings..."
                  type="text"
                  value={filterText}
                  onChange={e => setFilterText(e.target.value)}
                />
              </div>
            </div>
            <span className="text-sm text-on-surface-variant">{filteredFindings.length} findings shown</span>
          </div>

          {findings.length === 0 ? (
            <div className="py-xl text-center text-on-surface-variant">
              <span className="material-symbols-outlined text-[48px] block mb-md opacity-30">check_circle</span>
              <p className="font-bold">No findings for this scan</p>
              <p className="text-sm opacity-60">This repository appears clean, or findings were not stored.</p>
            </div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-surface-container-low/50 text-outline-variant font-label-caps text-[11px] uppercase tracking-wider">
                  <th className="py-4 px-6 border-b border-outline-variant font-semibold">Finding</th>
                  <th className="py-4 px-6 border-b border-outline-variant font-semibold">Severity</th>
                  <th className="py-4 px-6 border-b border-outline-variant font-semibold">Tool</th>
                  <th className="py-4 px-6 border-b border-outline-variant font-semibold">File</th>
                  <th className="py-4 px-6 border-b border-outline-variant font-semibold text-right">Line</th>
                </tr>
              </thead>
              <tbody className="text-body-md divide-y divide-outline-variant/30">
                {(filteredFindings.length > 0 ? filteredFindings : findings).map((finding: any, idx: number) => (
                  <tr key={finding.id || idx} className="hover:bg-surface-container/50 transition-colors group">
                    <td className="py-4 px-6">
                      <div className="flex flex-col">
                        <span className={`font-bold text-sm ${
                          finding.severity?.toLowerCase() === 'critical' ? 'text-error' :
                          finding.severity?.toLowerCase() === 'high' ? 'text-tertiary' :
                          finding.severity?.toLowerCase() === 'medium' ? 'text-[#ffcc00]' : 'text-secondary'
                        }`}>
                          {finding.description || finding.title || 'Security Finding'}
                        </span>
                        {finding.rule_id && (
                          <span className="text-outline text-[11px] mt-0.5 font-code-sm">{finding.rule_id}</span>
                        )}
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-tight ${getSeverityClass(finding.severity)}`}>
                        {finding.severity || 'Unknown'}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-sm">
                        <span className="material-symbols-outlined text-[16px] text-outline">
                          {finding.tool?.toLowerCase().includes('git') ? 'key' :
                           finding.tool?.toLowerCase().includes('sem') ? 'search' :
                           finding.tool?.toLowerCase().includes('ban') ? 'security' : 'inventory_2'}
                        </span>
                        <span className="text-on-surface-variant text-sm">{finding.tool || '—'}</span>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <code className="font-code-sm text-primary text-[12px] bg-primary/5 px-2 py-0.5 rounded">
                        {finding.file_path ? finding.file_path.split('/').pop() : '—'}
                      </code>
                    </td>
                    <td className="py-4 px-6 text-right font-code-sm text-outline">
                      {finding.line_number || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
};

export default ScanDetails;
