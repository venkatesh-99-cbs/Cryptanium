import React, { useState } from 'react';
import { useSecurity } from '../context/SecurityContext';
import { useNavigate } from 'react-router-dom';

type SeverityFilter = 'All' | 'Critical' | 'High' | 'Medium' | 'Low';
type StatusFilter = 'All' | 'Open' | 'Fixed' | 'Ignored';

const Findings: React.FC = () => {
  const { findings } = useSecurity();
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>('All');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('All');
  const [selectedFinding, setSelectedFinding] = useState<typeof findings[0] | null>(null);

  const filtered = findings.filter(f => {
    const matchSearch = f.title.toLowerCase().includes(search.toLowerCase()) || f.tool.toLowerCase().includes(search.toLowerCase()) || f.filePath.toLowerCase().includes(search.toLowerCase());
    const matchSev = severityFilter === 'All' || f.severity === severityFilter;
    const matchStatus = statusFilter === 'All' || f.status === statusFilter;
    return matchSearch && matchSev && matchStatus;
  });

  const severityCounts = {
    Critical: findings.filter(f => f.severity === 'Critical').length,
    High: findings.filter(f => f.severity === 'High').length,
    Medium: findings.filter(f => f.severity === 'Medium').length,
    Low: findings.filter(f => f.severity === 'Low').length,
  };

  const getSeverityClass = (sev: string) => {
    switch (sev) {
      case 'Critical': return 'severity-critical';
      case 'High': return 'severity-high';
      case 'Medium': return 'severity-medium';
      default: return 'severity-low';
    }
  };

  return (
    <div className="flex-1 flex flex-col md:flex-row gap-gutter">
      {/* Main Panel */}
      <div className={`flex-1 flex flex-col ${selectedFinding ? 'hidden md:flex' : 'flex'}`}>
        {/* Page Title */}
        <div className="mb-xl">
          <h2 className="text-headline-md font-headline-md font-bold text-on-background">Security Findings</h2>
          <p className="text-on-surface-variant text-sm mt-1">All detected vulnerabilities, secrets, and dependency risks across your repositories.</p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-md mb-xl">
          {[
            { label: 'Critical', value: severityCounts.Critical, icon: 'dangerous', active: severityFilter === 'Critical', setFn: () => setSeverityFilter(severityFilter === 'Critical' ? 'All' : 'Critical'), color: 'text-error', borderHi: 'border-error/30 bg-error/5', borderNorm: 'border-outline-variant' },
            { label: 'High', value: severityCounts.High, icon: 'warning', active: severityFilter === 'High', setFn: () => setSeverityFilter(severityFilter === 'High' ? 'All' : 'High'), color: 'text-tertiary', borderHi: 'border-tertiary/30 bg-tertiary/5', borderNorm: 'border-outline-variant' },
            { label: 'Medium', value: severityCounts.Medium, icon: 'info', active: severityFilter === 'Medium', setFn: () => setSeverityFilter(severityFilter === 'Medium' ? 'All' : 'Medium'), color: 'text-[#ffcc00]', borderHi: 'border-[#ffcc00]/30 bg-[#ffcc00]/5', borderNorm: 'border-outline-variant' },
            { label: 'Low', value: severityCounts.Low, icon: 'check_circle', active: severityFilter === 'Low', setFn: () => setSeverityFilter(severityFilter === 'Low' ? 'All' : 'Low'), color: 'text-secondary', borderHi: 'border-secondary/30 bg-secondary/5', borderNorm: 'border-outline-variant' }
          ].map(item => (
            <button
              key={item.label}
              onClick={item.setFn}
              className={`glass-card rounded-xl p-md text-left border transition-all ${item.active ? item.borderHi : item.borderNorm}`}
            >
              <div className="flex justify-between items-center mb-xs">
                <span className={`material-symbols-outlined ${item.color} text-[22px]`}>{item.icon}</span>
                <span className={`font-label-caps text-[10px] uppercase ${item.color}`}>{item.label}</span>
              </div>
              <span className={`font-bold text-3xl ${item.color}`}>{item.value}</span>
            </button>
          ))}
        </div>

        {/* Toolbar */}
        <div className="flex flex-wrap gap-sm items-center mb-md">
          <div className="relative flex-1 min-w-[180px]">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">search</span>
            <input
              className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg pl-10 pr-4 py-2 text-body-md focus:border-primary focus:ring-0 outline-none transition-all"
              placeholder="Search findings..."
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <select
            className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-2 text-body-md focus:border-primary focus:ring-0 outline-none text-on-background"
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value as StatusFilter)}
          >
            <option value="All">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Fixed">Fixed</option>
            <option value="Ignored">Ignored</option>
          </select>
          <button className="ml-auto border border-outline-variant text-on-surface-variant px-4 py-2 rounded-lg font-label-caps text-[12px] hover:text-on-surface transition-colors flex items-center gap-xs">
            <span className="material-symbols-outlined text-[18px]">download</span> Export
          </button>
        </div>

        {/* Findings Table */}
        <div className="glass-card rounded-xl overflow-hidden flex-1">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-surface-container-high border-b border-outline-variant text-outline font-label-caps text-[11px] uppercase tracking-widest">
                <th className="py-3 px-lg">Finding</th>
                <th className="py-3 px-lg">Severity</th>
                <th className="py-3 px-lg">Tool</th>
                <th className="py-3 px-lg">Status</th>
                <th className="py-3 px-lg">File</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/30">
              {filtered.map(finding => (
                <tr
                  key={finding.id}
                  className={`hover:bg-surface-container/50 transition-colors cursor-pointer ${selectedFinding?.id === finding.id ? 'bg-primary/5 border-l-2 border-primary' : ''}`}
                  onClick={() => setSelectedFinding(finding)}
                >
                  <td className="py-3 px-lg">
                    <p className="font-bold text-sm text-on-background">{finding.title}</p>
                    <p className="text-outline text-[11px] mt-0.5 truncate max-w-[180px]">{finding.description}</p>
                  </td>
                  <td className="py-3 px-lg">
                    <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${getSeverityClass(finding.severity)}`}>
                      {finding.severity}
                    </span>
                  </td>
                  <td className="py-3 px-lg text-on-surface-variant text-sm">{finding.tool}</td>
                  <td className="py-3 px-lg">
                    <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold border ${
                      finding.status === 'Open' ? 'text-error border-error/30 bg-error/10' :
                      finding.status === 'Fixed' ? 'text-secondary border-secondary/30 bg-secondary/10' :
                      'text-outline border-outline-variant'
                    }`}>
                      {finding.status}
                    </span>
                  </td>
                  <td className="py-3 px-lg">
                    <code className="text-[11px] text-primary font-code-sm">{finding.filePath}</code>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-xl text-center text-on-surface-variant">
                    <span className="material-symbols-outlined text-[48px] block mb-md opacity-40">check_circle</span>
                    No findings match your criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Drawer / Side Panel */}
      {selectedFinding && (
        <div className="w-full md:w-[400px] glass-card rounded-xl overflow-hidden flex flex-col">
          <div className="p-lg border-b border-outline-variant flex justify-between items-start">
            <div className="flex-1 pr-md">
              <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold mb-sm ${getSeverityClass(selectedFinding.severity)}`}>
                {selectedFinding.severity}
              </span>
              <h3 className="font-bold text-on-background text-base leading-snug">{selectedFinding.title}</h3>
            </div>
            <button onClick={() => setSelectedFinding(null)} className="text-outline hover:text-on-surface transition-colors shrink-0">
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
          <div className="flex-1 overflow-y-auto custom-scrollbar p-lg space-y-lg">
            {/* Finding Info */}
            <div className="space-y-sm">
              {[
                { label: 'Tool', value: selectedFinding.tool, icon: 'build' },
                { label: 'Repository', value: selectedFinding.repoId, icon: 'folder_open' },
                { label: 'Status', value: selectedFinding.status, icon: 'radio_button_checked' },
                { label: 'Detected At', value: selectedFinding.detectedAt, icon: 'schedule' },
              ].map(item => (
                <div key={item.label} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-sm text-on-surface-variant">
                    <span className="material-symbols-outlined text-[16px]">{item.icon}</span>
                    {item.label}
                  </div>
                  <span className="text-on-background font-medium">{item.value}</span>
                </div>
              ))}
            </div>

            <div className="border-t border-outline-variant pt-md">
              <h4 className="font-label-caps text-[11px] uppercase tracking-wider text-on-surface-variant mb-sm">Affected File</h4>
              <div className="bg-background rounded-lg p-sm border border-outline-variant">
                <code className="text-primary font-code-sm text-sm">{selectedFinding.filePath}</code>
                <span className="text-outline ml-md">Line {selectedFinding.line}</span>
              </div>
            </div>

            <div className="border-t border-outline-variant pt-md">
              <h4 className="font-label-caps text-[11px] uppercase tracking-wider text-on-surface-variant mb-sm">Description</h4>
              <p className="text-on-surface-variant text-sm leading-relaxed">{selectedFinding.description} This vulnerability could potentially allow an attacker to gain unauthorized access to sensitive data or system resources.</p>
            </div>

            <div className="border-t border-outline-variant pt-md">
              <h4 className="font-label-caps text-[11px] uppercase tracking-wider text-on-surface-variant mb-sm">Code Context</h4>
              <div className="bg-background rounded-lg p-md border border-outline-variant font-code-sm text-xs overflow-x-auto custom-scrollbar">
                <pre className="text-[#a8b1c9]">
                  <span className="text-outline">{selectedFinding.line - 1} | </span><span className="text-on-surface-variant">{`// vulnerable code context`}</span>{'\n'}
                  <span className="text-error">{selectedFinding.line} | </span><span className="text-tertiary">{'const result = query(`SELECT * FROM users WHERE id=${userId}`)'}</span>{'\n'}
                  <span className="text-outline">{selectedFinding.line + 1} | </span><span className="text-on-surface-variant">{`return result;`}</span>
                </pre>
              </div>
            </div>

            <div className="border-t border-outline-variant pt-md">
              <h4 className="font-label-caps text-[11px] uppercase tracking-wider text-on-surface-variant mb-sm">Remediation</h4>
              <p className="text-on-surface-variant text-sm leading-relaxed">{selectedFinding.remediation}</p>
            </div>
          </div>
          <div className="p-md border-t border-outline-variant flex gap-sm">
            <button className="flex-1 py-2 bg-[#7B61FF] text-white rounded-lg font-bold text-sm hover:bg-opacity-90 transition-all flex items-center justify-center gap-xs">
              <span className="material-symbols-outlined text-[18px]">smart_toy</span> Ask AI for Fix
            </button>
            <button className="flex-1 py-2 border border-outline-variant text-on-surface-variant rounded-lg font-bold text-sm hover:bg-surface-container transition-all flex items-center justify-center gap-xs">
              <span className="material-symbols-outlined text-[18px]">check_circle</span> Mark Fixed
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Findings;
