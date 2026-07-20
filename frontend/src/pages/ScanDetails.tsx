import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSecurity } from '../context/SecurityContext';

const ScanDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { repositories, findings, scans } = useSecurity();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'summary' | 'findings'>('findings');
  const [filterText, setFilterText] = useState('');

  const repo = repositories.find(r => r.id === id) || repositories[0];
  const scan = scans.find(s => s.repoId === id) || scans[0];
  const repoFindings = findings.filter(f => f.repoId === (repo?.id ?? id));
  const filteredFindings = repoFindings.filter(f =>
    f.title.toLowerCase().includes(filterText.toLowerCase()) ||
    f.tool.toLowerCase().includes(filterText.toLowerCase())
  );

  if (!repo) {
    return (
      <div className="flex items-center justify-center h-64 text-on-surface-variant">
        <div className="text-center">
          <span className="material-symbols-outlined text-[48px] block mb-md opacity-40">search_off</span>
          <p>Repository not found.</p>
          <button onClick={() => navigate('/scans')} className="mt-md text-primary hover:underline">Back to Scans</button>
        </div>
      </div>
    );
  }

  const getSeverityClass = (sev: string) => {
    switch (sev) {
      case 'Critical': return 'severity-critical';
      case 'High': return 'severity-high';
      case 'Medium': return 'severity-medium';
      default: return 'severity-low';
    }
  };

  const scoreColor = repo.trustScore >= 80 ? 'text-secondary' : repo.trustScore >= 60 ? 'text-tertiary' : 'text-error';
  const scoreBorderColor = repo.trustScore >= 80 ? 'border-secondary/20 bg-secondary/10' : repo.trustScore >= 60 ? 'border-tertiary/20 bg-tertiary/10' : 'border-error/20 bg-error/10';

  return (
    <div className="flex-1">
      {/* Breadcrumbs */}
      <div className="flex items-center text-on-surface-variant font-label-caps gap-xs uppercase tracking-widest text-[10px] mb-xl">
        <button onClick={() => navigate('/scans')} className="hover:text-primary transition-colors">Scans</button>
        <span className="material-symbols-outlined text-[14px]">chevron_right</span>
        <span>{repo.name}</span>
        <span className="material-symbols-outlined text-[14px]">chevron_right</span>
        <span className="text-primary">Scan Details</span>
      </div>

      {/* Header */}
      <div className="flex justify-between items-start mb-xl">
        <div className="flex items-center gap-lg">
          <div className="w-16 h-16 rounded-xl bg-surface-container-highest flex items-center justify-center border border-outline-variant">
            <span className="material-symbols-outlined text-[40px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>account_tree</span>
          </div>
          <div>
            <h1 className="text-headline-lg font-headline-lg text-on-background flex items-center gap-sm flex-wrap">
              {repo.name}
              <span className="bg-surface-container text-outline-variant text-[10px] px-2 py-0.5 rounded border border-outline-variant font-label-caps uppercase">
                {repo.isPrivate ? 'Private' : 'Public'}
              </span>
            </h1>
            <div className="flex items-center gap-md mt-sm text-on-surface-variant">
              <div className="flex items-center gap-xs">
                <span className="material-symbols-outlined text-[16px]">balance</span>
                <span className="font-label-caps text-sm">{repo.branch}</span>
              </div>
              <div className="w-1 h-1 rounded-full bg-outline-variant" />
              <div className="flex items-center gap-xs">
                <span className="material-symbols-outlined text-[16px]">schedule</span>
                <span className="text-sm">Scanned {repo.lastScanTime}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Trust Score Indicator */}
        <div className="flex flex-col items-end">
          <div className={`flex items-center gap-sm border px-4 py-2 rounded-xl ${scoreBorderColor}`}>
            <div className="flex flex-col items-end">
              <span className={`font-label-caps text-[10px] ${scoreColor}`}>Trust Score</span>
              <span className={`text-headline-md font-headline-md font-bold ${scoreColor}`}>{repo.trustScore}/100</span>
            </div>
            <div className="w-10 h-10 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90">
                <circle className="text-surface-container-highest" cx="20" cy="20" fill="transparent" r="18" stroke="currentColor" strokeWidth="3" />
                <circle className={scoreColor} cx="20" cy="20" fill="transparent" r="18" stroke="currentColor"
                  strokeDasharray="113.1"
                  strokeDashoffset={113.1 - (repo.trustScore / 100) * 113.1}
                  strokeWidth="3"
                />
              </svg>
            </div>
          </div>
          <span className={`mt-2 text-[11px] font-label-caps ${scoreColor}`}>
            Status: {repo.trustScore >= 80 ? 'Healthy' : repo.trustScore >= 60 ? 'Fair' : 'Critical'}
          </span>
        </div>
      </div>

      {/* Tabs & Finding Counters */}
      <div className="flex items-center justify-between border-b border-outline-variant mb-lg">
        <div className="flex gap-xl">
          {(['summary', 'findings'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-4 px-2 font-body-md font-bold border-b-2 transition-all capitalize ${activeTab === tab ? 'text-primary border-primary' : 'text-on-surface-variant border-transparent hover:text-on-surface'}`}
            >
              {tab}
            </button>
          ))}
        </div>
        <div className="flex gap-sm mb-2">
          {[
            { label: 'Total', value: repo.findingsCount.total, icon: 'bug_report', color: 'text-primary' },
            { label: 'Critical', value: repo.findingsCount.critical, dot: 'bg-error' },
            { label: 'High', value: repo.findingsCount.high, dot: 'bg-tertiary' },
            { label: 'Medium', value: repo.findingsCount.medium, dot: 'bg-[#ffcc00]' },
            { label: 'Low', value: repo.findingsCount.low, dot: 'bg-secondary' }
          ].map(item => (
            <div key={item.label} className="bg-surface-container px-3 py-1.5 rounded-lg border border-outline-variant flex items-center gap-sm">
              {item.icon ? <span className={`material-symbols-outlined ${item.color} text-[18px]`}>{item.icon}</span> : <span className={`w-2 h-2 rounded-full ${item.dot}`} />}
              <span className="text-on-background font-bold text-sm">{item.value}</span>
              <span className="text-outline text-[11px] font-label-caps">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Summary Tab */}
      {activeTab === 'summary' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">
          {[
            { title: 'Security', score: 85, icon: 'security', color: 'text-secondary' },
            { title: 'Dependency Health', score: 80, icon: 'inventory_2', color: 'text-primary' },
            { title: 'Secrets Detection', score: 78, icon: 'key', color: 'text-tertiary' },
            { title: 'Code Quality', score: 72, icon: 'code', color: 'text-on-surface-variant' },
            { title: 'Attack Surface', score: 88, icon: 'radar', color: 'text-secondary' },
            { title: 'Compliance', score: 91, icon: 'verified', color: 'text-secondary' }
          ].map(card => (
            <div key={card.title} className="glass-card rounded-xl p-lg">
              <div className="flex items-center justify-between mb-md">
                <span className={`material-symbols-outlined ${card.color} text-[28px]`}>{card.icon}</span>
                <span className={`font-bold text-xl ${card.color}`}>{card.score}/100</span>
              </div>
              <h4 className="font-bold text-on-background mb-sm">{card.title}</h4>
              <div className="w-full bg-surface-container-highest h-1.5 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${card.score >= 80 ? 'bg-secondary' : card.score >= 60 ? 'bg-tertiary' : 'bg-error'}`} style={{ width: `${card.score}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Findings Tab */}
      {activeTab === 'findings' && (
        <div className="glass-card rounded-xl overflow-hidden">
          <div className="p-md bg-surface-container-high/50 border-b border-outline-variant flex justify-between items-center">
            <div className="flex items-center gap-md">
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">search</span>
                <input
                  className="bg-background border border-outline-variant rounded-lg pl-10 pr-4 py-1.5 text-body-md w-64 focus:border-primary focus:ring-0 outline-none transition-all"
                  placeholder="Filter findings..."
                  type="text"
                  value={filterText}
                  onChange={e => setFilterText(e.target.value)}
                />
              </div>
              <button className="bg-surface-container text-on-surface-variant px-4 py-1.5 rounded-lg border border-outline-variant text-body-md flex items-center gap-xs hover:text-on-surface">
                <span className="material-symbols-outlined text-[18px]">filter_list</span> Filter
              </button>
            </div>
            <div className="flex gap-sm">
              <button className="p-1.5 rounded-lg hover:bg-surface-container-high text-on-surface-variant">
                <span className="material-symbols-outlined text-[20px]">download</span>
              </button>
              <button className="p-1.5 rounded-lg hover:bg-surface-container-high text-on-surface-variant">
                <span className="material-symbols-outlined text-[20px]">more_vert</span>
              </button>
            </div>
          </div>

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
              {(filteredFindings.length > 0 ? filteredFindings : repoFindings).map(finding => (
                <tr
                  key={finding.id}
                  className="hover:bg-surface-container/50 transition-colors cursor-pointer group"
                  onClick={() => navigate('/findings')}
                >
                  <td className="py-4 px-6">
                    <div className="flex flex-col">
                      <span className={`font-bold ${finding.severity === 'Critical' ? 'text-error' : finding.severity === 'High' ? 'text-tertiary' : finding.severity === 'Medium' ? 'text-[#ffcc00]' : 'text-secondary'}`}>
                        {finding.title}
                      </span>
                      <span className="text-outline text-[11px] mt-0.5">{finding.description}</span>
                    </div>
                  </td>
                  <td className="py-4 px-6">
                    <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-tight ${getSeverityClass(finding.severity)}`}>
                      {finding.severity}
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    <div className="flex items-center gap-sm">
                      <span className="material-symbols-outlined text-[16px] text-outline">
                        {finding.tool === 'Gitleaks' ? 'key' : finding.tool === 'Semgrep' ? 'search' : finding.tool === 'Bandit' ? 'security' : 'inventory_2'}
                      </span>
                      <span className="text-on-surface-variant">{finding.tool}</span>
                    </div>
                  </td>
                  <td className="py-4 px-6">
                    <code className="font-code-sm text-primary text-[12px] bg-primary/5 px-2 py-0.5 rounded">{finding.filePath.split('/').pop()}</code>
                  </td>
                  <td className="py-4 px-6 text-right font-code-sm text-outline">{finding.line}</td>
                </tr>
              ))}
              {repoFindings.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-xl text-center text-on-surface-variant">
                    <span className="material-symbols-outlined text-[48px] block mb-md opacity-40">check_circle</span>
                    No findings for this repository.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ScanDetails;
