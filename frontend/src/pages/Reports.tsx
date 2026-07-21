import React, { useState } from 'react';
import { useSecurity } from '../context/SecurityContext';
import { apiClient } from '../services/api';

const Reports: React.FC = () => {
  const { reports, generateReport, repositories } = useSecurity();
  const [generatingFor, setGeneratingFor] = useState<string | number | null>(null);
  const [selectedReport, setSelectedReport] = useState<typeof reports[0] | null>(null);

  const handleGenerate = async (repoId: string | number) => {
    setGeneratingFor(repoId);
    await generateReport(repoId);
    setGeneratingFor(null);
  };

  const handleDownload = (reportId: number, format: 'pdf' | 'json') => {
    const url = format === 'pdf' ? apiClient.downloadPdfReport(reportId) : apiClient.downloadJsonReport(reportId);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${reportId}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'HEALTHY': return 'text-secondary border-secondary/30 bg-secondary/10';
      case 'AT_RISK': return 'text-tertiary border-tertiary/30 bg-tertiary/10';
      case 'CRITICAL': return 'text-error border-error/30 bg-error/10';
      default: return 'text-outline border-outline-variant';
    }
  };

  return (
    <div className="flex-1">
      {/* Header */}
      <div className="mb-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-md">
        <div>
          <h2 className="text-headline-md font-headline-md font-bold text-on-background">Security Reports</h2>
          <p className="text-on-surface-variant text-sm mt-1">Generate and download comprehensive security reports for stakeholders.</p>
        </div>
        <button
          onClick={() => repositories[0] && handleGenerate(repositories[0].id)}
          className="flex items-center gap-sm bg-[#7B61FF] text-white px-xl py-md rounded-lg font-bold shadow-[0_0_15px_rgba(123,97,255,0.3)] hover:shadow-[0_0_20px_rgba(123,97,255,0.5)] transition-all"
        >
          <span className="material-symbols-outlined">add</span> Generate Report
        </button>
      </div>

      {/* Report Grid + Detail */}
      <div className="flex flex-col lg:flex-row gap-gutter">
        {/* Left: Reports List */}
        <div className="flex-1">
          {/* Summary Stats */}
          <div className="grid grid-cols-3 gap-md mb-xl">
            {[
              { label: 'Total Reports', value: reports.length, icon: 'summarize', color: 'text-primary' },
              { label: 'This Month', value: reports.length, icon: 'calendar_today', color: 'text-secondary' },
              { label: 'Critical Issues', value: reports.filter(r => r.status === 'CRITICAL').length, icon: 'dangerous', color: 'text-error' }
            ].map(stat => (
              <div key={stat.label} className="glass-card p-md rounded-xl flex flex-col gap-xs">
                <div className="flex justify-between items-start">
                  <span className="font-label-caps text-[11px] text-on-surface-variant uppercase">{stat.label}</span>
                  <span className={`material-symbols-outlined ${stat.color} text-[20px]`}>{stat.icon}</span>
                </div>
                <span className={`font-bold text-3xl ${stat.color}`}>{stat.value}</span>
              </div>
            ))}
          </div>

          {/* Reports Cards */}
          <div className="flex flex-col gap-md">
            {reports.map(report => (
              <div
                key={report.id}
                className={`glass-card rounded-xl p-lg cursor-pointer transition-all neon-glow ${selectedReport?.id === report.id ? 'border border-primary/40 bg-primary/5' : ''}`}
                onClick={() => setSelectedReport(report)}
              >
                <div className="flex justify-between items-start mb-md">
                  <div className="flex items-center gap-md">
                    <div className="w-10 h-10 rounded-lg bg-surface-container-highest flex items-center justify-center border border-outline-variant">
                      <span className="material-symbols-outlined text-primary text-[24px]">description</span>
                    </div>
                    <div>
                      <h3 className="font-bold text-on-background">{report.repoName} Security Report</h3>
                      <p className="text-sm text-on-surface-variant">{report.generatedAt}</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-[10px] font-bold border ${getStatusClass(report.status)}`}>
                    {report.status}
                  </span>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-4 gap-md text-center">
                  <div className="bg-surface-container-high/40 rounded-lg p-sm border border-outline-variant/20">
                    <div className="text-xl font-bold text-secondary">{report.trustScore}</div>
                    <div className="text-[10px] text-on-surface-variant font-label-caps">TRUST SCORE</div>
                  </div>
                  <div className="bg-surface-container-high/40 rounded-lg p-sm border border-outline-variant/20">
                    <div className="text-xl font-bold text-error">{report.findings.critical}</div>
                    <div className="text-[10px] text-on-surface-variant font-label-caps">CRITICAL</div>
                  </div>
                  <div className="bg-surface-container-high/40 rounded-lg p-sm border border-outline-variant/20">
                    <div className="text-xl font-bold text-tertiary">{report.findings.high}</div>
                    <div className="text-[10px] text-on-surface-variant font-label-caps">HIGH</div>
                  </div>
                  <div className="bg-surface-container-high/40 rounded-lg p-sm border border-outline-variant/20">
                    <div className="text-xl font-bold text-[#ffcc00]">{report.findings.medium}</div>
                    <div className="text-[10px] text-on-surface-variant font-label-caps">MEDIUM</div>
                  </div>
                </div>

                <div className="flex items-center justify-between mt-md pt-md border-t border-outline-variant/30">
                  <div className="flex items-center gap-sm text-on-surface-variant text-sm">
                    <span className="material-symbols-outlined text-[18px]">folder_open</span>
                    {report.repoName}
                  </div>
                  <div className="flex gap-sm">
                    <button
                      onClick={(event) => { event.stopPropagation(); handleDownload(report.id, 'pdf'); }}
                      className="text-primary hover:underline flex items-center gap-1 text-sm font-bold"
                    >
                      <span className="material-symbols-outlined text-[16px]">download</span> PDF
                    </button>
                    <button
                      onClick={(event) => { event.stopPropagation(); handleDownload(report.id, 'json'); }}
                      className="text-on-surface-variant hover:text-primary text-sm flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined text-[16px]">download</span> JSON
                    </button>
                  </div>
                </div>
              </div>
            ))}

            {/* Generate for repos */}
            {repositories.filter(r => !reports.find(rp => rp.repoId === r.id)).map(repo => (
              <div key={repo.id} className="glass-card rounded-xl p-lg border border-dashed border-outline-variant/50 flex items-center justify-between opacity-60">
                <div className="flex items-center gap-md">
                  <div className="w-10 h-10 rounded-lg bg-surface-container flex items-center justify-center">
                    <span className="material-symbols-outlined text-outline">{repo.icon}</span>
                  </div>
                  <div>
                    <h3 className="font-bold text-on-surface-variant">{repo.name}</h3>
                    <p className="text-sm text-on-surface-variant/60">No report generated yet</p>
                  </div>
                </div>
                <button
                  onClick={() => handleGenerate(repo.id)}
                  disabled={generatingFor === repo.id}
                  className="flex items-center gap-xs px-md py-sm border border-outline-variant text-on-surface-variant rounded-lg text-sm hover:text-primary hover:border-primary transition-all"
                >
                  {generatingFor === repo.id ? (
                    <><span className="material-symbols-outlined animate-spin text-[18px]">refresh</span> Generating...</>
                  ) : (
                    <><span className="material-symbols-outlined text-[18px]">add</span> Generate</>
                  )}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Report Detail */}
        {selectedReport && (
          <div className="w-full lg:w-[380px] glass-card rounded-xl overflow-hidden flex flex-col">
            <div className="p-lg border-b border-outline-variant flex justify-between items-center">
              <h3 className="font-bold text-on-background">Report Summary</h3>
              <button onClick={() => setSelectedReport(null)} className="text-outline hover:text-on-surface transition-colors">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            <div className="flex-1 overflow-y-auto custom-scrollbar p-lg space-y-lg">
              <div className="flex items-center justify-center">
                <div className="relative w-28 h-28">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" fill="transparent" r="40" stroke="rgba(255,255,255,0.05)" strokeWidth="10" />
                    <circle cx="50" cy="50" fill="transparent" r="40" stroke={selectedReport.trustScore >= 80 ? '#40e56c' : selectedReport.trustScore >= 60 ? '#ffb950' : '#ff5959'}
                      strokeDasharray={251.2}
                      strokeDashoffset={251.2 - (selectedReport.trustScore / 100) * 251.2}
                      strokeWidth="10"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="font-bold text-3xl text-on-background">{selectedReport.trustScore}</span>
                    <span className="text-[10px] text-on-surface-variant">Trust Score</span>
                  </div>
                </div>
              </div>

              <div className="space-y-sm">
                {[
                  { label: 'Repository', value: selectedReport.repoName, icon: 'folder_open' },
                  { label: 'Status', value: selectedReport.status, icon: 'analytics' },
                  { label: 'Generated', value: selectedReport.generatedAt, icon: 'schedule' },
                  { label: 'Findings Total', value: selectedReport.findings.critical + selectedReport.findings.high + selectedReport.findings.medium + selectedReport.findings.low, icon: 'bug_report' },
                ].map(item => (
                  <div key={item.label} className="flex items-center justify-between text-sm border-b border-outline-variant/20 pb-sm">
                    <div className="flex items-center gap-sm text-on-surface-variant">
                      <span className="material-symbols-outlined text-[16px]">{item.icon}</span>
                      {item.label}
                    </div>
                    <span className="text-on-background font-medium">{item.value}</span>
                  </div>
                ))}
              </div>

              <div>
                <h4 className="font-label-caps text-[11px] uppercase tracking-wider text-on-surface-variant mb-sm">AI Summary</h4>
                <p className="text-on-surface-variant text-sm leading-relaxed">{selectedReport.summary || 'This repository has demonstrated overall good security posture with a trust score indicating healthy practices. However, attention is needed for the critical and high severity findings which should be addressed promptly.'}</p>
              </div>
            </div>
            <div className="p-md border-t border-outline-variant flex gap-sm">
              <button className="flex-1 py-2 bg-[#7B61FF] text-white rounded-lg font-bold text-sm hover:bg-opacity-90 transition-all flex items-center justify-center gap-xs">
                <span className="material-symbols-outlined text-[18px]">download</span> Download PDF
              </button>
              <button className="flex-1 py-2 border border-outline-variant text-on-surface-variant rounded-lg font-bold text-sm hover:bg-surface-container transition-all flex items-center justify-center gap-xs">
                <span className="material-symbols-outlined text-[18px]">share</span> Share
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Reports;
