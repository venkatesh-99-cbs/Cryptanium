import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useSecurity } from '../context/SecurityContext';

const TrustGauge: React.FC<{ score: number; size?: number }> = ({ score, size = 192 }) => {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? '#40e56c' : score >= 60 ? '#ffb950' : '#ffb4ab';

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg className="gauge-svg w-full h-full" viewBox="0 0 100 100">
        <circle className="text-surface-container-highest" cx="50" cy="50" fill="transparent" r={radius} stroke="currentColor" strokeWidth="8" />
        <circle cx="50" cy="50" fill="transparent" r={radius} stroke={color} strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" strokeWidth="8" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-[36px] font-bold text-on-background leading-none">{score}</span>
        <span className="text-on-surface-variant font-label-caps text-[10px] uppercase mt-1">/100</span>
      </div>
      <div className="absolute bottom-0 bg-secondary/10 text-secondary border border-secondary/20 px-3 py-0.5 rounded-full text-xs font-bold">
        {score >= 80 ? 'Good' : score >= 60 ? 'Fair' : 'Critical'}
      </div>
    </div>
  );
};

const EmptyGauge: React.FC<{ size?: number }> = ({ size = 192 }) => (
  <div className="relative flex items-center justify-center opacity-40" style={{ width: size, height: size }}>
    <svg className="w-full h-full" viewBox="0 0 100 100">
      <circle className="text-surface-container-highest" cx="50" cy="50" fill="transparent" r={40} stroke="currentColor" strokeWidth="8" />
    </svg>
    <div className="absolute inset-0 flex flex-col items-center justify-center">
      <span className="text-[28px] font-bold text-on-surface-variant leading-none">--</span>
      <span className="text-on-surface-variant font-label-caps text-[10px] uppercase mt-1">/100</span>
    </div>
  </div>
);

const Dashboard: React.FC = () => {
  const { repositories, findings, scans, isScanning, activeScanRepo, triggerScan, isLoading } = useSecurity();
  const navigate = useNavigate();

  const hasData = scans.length > 0;
  const completedScans = scans.filter(s => s.trust_score && s.trust_score > 0);
  const avgScore = completedScans.length
    ? Math.round(completedScans.reduce((a, s) => a + (s.trust_score || 0), 0) / completedScans.length)
    : 0;

  const totalFindings = findings.length;
  const criticalFindings = findings.filter(f => f.severity === 'Critical' || f.severity === 'critical').length;
  const highFindings = findings.filter(f => f.severity === 'High' || f.severity === 'high').length;
  const medFindings = findings.filter(f => f.severity === 'Medium' || f.severity === 'medium').length;
  const lowFindings = findings.filter(f => f.severity === 'Low' || f.severity === 'low').length;

  return (
    <div className="flex-1">
      {/* Page Title */}
      <div className="mb-xl">
        <h2 className="text-headline-md font-headline-md font-bold text-on-background">Overview</h2>
        <p className="text-xs text-on-surface-variant mt-1">
          {isLoading
            ? 'Loading security data...'
            : hasData
            ? "Here's what's happening with your repositories."
            : 'Run your first scan to see security insights here.'}
        </p>
      </div>

      {/* Bento Grid */}
      <div className="grid grid-cols-12 gap-gutter">

        {/* Trust Score Gauge — 6 col */}
        <div className="col-span-12 lg:col-span-6 glass-card rounded-xl p-lg flex flex-col justify-between">
          <div className="flex justify-between items-start mb-md">
            <h3 className="text-headline-md font-headline-md font-semibold">Repository Trust Score</h3>
            <span className="material-symbols-outlined text-primary text-[20px]">info</span>
          </div>
          <div className="flex flex-col md:flex-row items-center gap-xl">
            {avgScore > 0 ? <TrustGauge score={avgScore} /> : <EmptyGauge />}
            <div className="flex-1 w-full space-y-4">
              {isLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3, 4].map(i => (
                    <div key={i} className="flex items-center justify-between">
                      <div className="h-3 w-20 bg-surface-container-highest rounded animate-pulse" />
                      <div className="h-1.5 w-2/3 bg-surface-container-highest rounded-full animate-pulse" />
                    </div>
                  ))}
                </div>
              ) : !hasData ? (
                <div className="text-center text-on-surface-variant py-4">
                  <span className="material-symbols-outlined text-[32px] block mb-2 opacity-30">bar_chart</span>
                  <p className="text-sm">No scan data yet</p>
                  <p className="text-xs opacity-60">Run a scan to see scores</p>
                </div>
              ) : (
                [
                  { label: 'Critical', val: criticalFindings, max: Math.max(totalFindings, 1), color: 'bg-error' },
                  { label: 'High', val: highFindings, max: Math.max(totalFindings, 1), color: 'bg-tertiary' },
                  { label: 'Medium', val: medFindings, max: Math.max(totalFindings, 1), color: 'bg-[#ffcc00]' },
                  { label: 'Low', val: lowFindings, max: Math.max(totalFindings, 1), color: 'bg-secondary' },
                ].map(item => (
                  <div key={item.label} className="flex items-center justify-between">
                    <span className="text-on-surface-variant text-sm">{item.label}</span>
                    <div className="w-2/3 flex items-center gap-sm">
                      <div className="flex-1 bg-surface-container-highest h-1.5 rounded-full overflow-hidden">
                        <div className={`${item.color} h-full rounded-full transition-all duration-700`} style={{ width: `${(item.val / item.max) * 100}%` }} />
                      </div>
                      <span className="font-code-sm text-[12px] w-12 text-right text-on-surface-variant">{item.val}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Active Scan Status — 6 col */}
        <div className="col-span-12 lg:col-span-6 glass-card rounded-xl p-lg flex flex-col">
          <div className="flex justify-between items-start mb-lg">
            <h3 className="text-headline-md font-headline-md font-semibold">Live Scan Activity</h3>
            {isScanning && (
              <span className="px-2 py-0.5 bg-secondary/10 border border-secondary/20 text-secondary text-[10px] font-bold rounded-full flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse" /> SCANNING
              </span>
            )}
          </div>
          <div className="flex-1 space-y-md overflow-y-auto custom-scrollbar pr-1">
            {repositories.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-32 text-on-surface-variant">
                <span className="material-symbols-outlined text-[40px] block mb-2 opacity-30">folder_off</span>
                <p className="text-sm">No repositories connected</p>
                <p className="text-xs opacity-60">Login with GitHub to see your repositories</p>
              </div>
            ) : (
              repositories.slice(0, 4).map(repo => (
                <div key={repo.id} className="flex items-center justify-between p-sm bg-surface-container-high/40 rounded-lg border border-outline-variant/20 hover:border-primary/20 transition-all group">
                  <div className="flex items-center gap-md">
                    <div className="w-8 h-8 rounded bg-surface-container flex items-center justify-center border border-outline-variant/50">
                      <span className="material-symbols-outlined text-primary text-[18px]">source</span>
                    </div>
                    <div>
                      <p className="font-bold text-sm text-on-background group-hover:text-primary transition-colors">{repo.name}</p>
                      <p className="text-[11px] text-outline font-code-sm">{repo.default_branch}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-md">
                    {activeScanRepo === String(repo.id) ? (
                      <span className="flex items-center gap-1 text-secondary text-[11px] font-bold">
                        <span className="material-symbols-outlined text-[14px] animate-spin">refresh</span> Scanning...
                      </span>
                    ) : (
                      <span className="font-bold text-sm text-on-surface-variant">--</span>
                    )}
                    <button
                      onClick={() => triggerScan(repo.id)}
                      disabled={isScanning}
                      className="text-on-surface-variant hover:text-primary transition-colors disabled:opacity-40"
                      title="Scan repository"
                    >
                      <span className="material-symbols-outlined text-[18px]">play_arrow</span>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Stats Row — 4 cols each */}
        {[
          { label: 'Total Findings', value: totalFindings, icon: 'assessment', color: 'text-primary', borderColor: '' },
          { label: 'Critical', value: criticalFindings, icon: 'dangerous', color: 'text-error', borderColor: 'border-l-4 border-error' },
          { label: 'High', value: highFindings, icon: 'warning', color: 'text-tertiary', borderColor: 'border-l-4 border-tertiary' },
          { label: 'Scans Run', value: scans.length, icon: 'radar', color: 'text-secondary', borderColor: '' },
        ].map(stat => (
          <div key={stat.label} className={`col-span-12 sm:col-span-6 lg:col-span-3 glass-card p-lg rounded-xl flex flex-col gap-sm ${stat.borderColor}`}>
            <div className="flex justify-between items-center text-on-surface-variant">
              <span className="font-label-caps text-[11px] uppercase tracking-wider">{stat.label}</span>
              <span className={`material-symbols-outlined ${stat.color} text-[22px]`}>{stat.icon}</span>
            </div>
            <div className="text-[40px] font-bold text-on-background leading-none">
              {isLoading ? <span className="text-[24px] opacity-40 animate-pulse">...</span> : stat.value}
            </div>
            <div className="text-xs text-on-surface-variant">
              {stat.label === 'Critical' ? 'Requires immediate action'
                : stat.label === 'Total Findings' ? 'Across all scans'
                : stat.label === 'High' ? 'Address promptly'
                : 'Total scans executed'}
            </div>
          </div>
        ))}

        {/* Recent Scans Table — 8 col */}
        <div className="col-span-12 lg:col-span-8 glass-card rounded-xl overflow-hidden">
          <div className="p-lg border-b border-outline-variant flex justify-between items-center">
            <h3 className="font-headline-md font-semibold">Recent Scans</h3>
            <button onClick={() => navigate('/scans')} className="text-primary text-sm font-label-caps hover:underline flex items-center gap-1">
              View All <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
            </button>
          </div>
          {scans.length === 0 ? (
            <div className="py-xl text-center text-on-surface-variant">
              <span className="material-symbols-outlined text-[48px] block mb-md opacity-30">history</span>
              <p className="font-bold">No scans yet</p>
              <p className="text-sm opacity-60">Start a scan from the Repositories page</p>
            </div>
          ) : (
            <table className="w-full text-left">
              <thead>
                <tr className="bg-surface-container-low/50 text-outline font-label-caps text-[11px] uppercase tracking-wider border-b border-outline-variant">
                  <th className="py-3 px-lg">Repository</th>
                  <th className="py-3 px-lg">Status</th>
                  <th className="py-3 px-lg">Score</th>
                  <th className="py-3 px-lg">Scanned</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30">
                {scans.slice(0, 5).map(scan => (
                  <tr key={scan.scan_id} className="hover:bg-surface-container/50 transition-colors cursor-pointer" onClick={() => navigate(`/scans/${scan.scan_id}`)}>
                    <td className="py-3 px-lg font-bold text-sm text-on-background hover:text-primary transition-colors">{scan.repository_name}</td>
                    <td className="py-3 px-lg">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold flex items-center gap-1 w-fit ${
                        scan.status === 'completed' || scan.status === 'success' ? 'bg-secondary/10 text-secondary border border-secondary/20' :
                        scan.status === 'in_progress' || scan.status === 'running' ? 'bg-primary/10 text-primary border border-primary/20' :
                        scan.status === 'pending' ? 'bg-outline/10 text-outline border border-outline/20' :
                        'bg-error/10 text-error border border-error/20'
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          scan.status === 'completed' || scan.status === 'success' ? 'bg-secondary' :
                          scan.status === 'in_progress' || scan.status === 'running' ? 'bg-primary animate-pulse' :
                          scan.status === 'pending' ? 'bg-outline' : 'bg-error'
                        }`} />
                        {scan.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 px-lg">
                      {scan.trust_score > 0 ? (
                        <span className={`font-bold text-sm font-code-sm ${scan.trust_score >= 80 ? 'text-secondary' : scan.trust_score >= 60 ? 'text-tertiary' : 'text-error'}`}>
                          {scan.trust_score}/100
                        </span>
                      ) : (
                        <span className="text-on-surface-variant text-sm">--</span>
                      )}
                    </td>
                    <td className="py-3 px-lg text-on-surface-variant text-sm">
                      {scan.created_at ? new Date(scan.created_at).toLocaleString() : '--'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Finding Distribution — 4 col */}
        <div className="col-span-12 lg:col-span-4 glass-card rounded-xl p-lg flex flex-col gap-md">
          <h3 className="font-headline-md font-semibold">Finding Distribution</h3>
          {totalFindings === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-on-surface-variant py-4">
              <span className="material-symbols-outlined text-[40px] block mb-2 opacity-30">donut_large</span>
              <p className="text-sm">No findings data</p>
              <p className="text-xs opacity-60">Complete a scan to see distribution</p>
            </div>
          ) : (
            <div className="flex-1 space-y-sm">
              {[
                { label: 'Critical', val: criticalFindings, total: totalFindings, color: 'bg-error', textColor: 'text-error' },
                { label: 'High', val: highFindings, total: totalFindings, color: 'bg-tertiary', textColor: 'text-tertiary' },
                { label: 'Medium', val: medFindings, total: totalFindings, color: 'bg-[#ffcc00]', textColor: 'text-[#ffcc00]' },
                { label: 'Low', val: lowFindings, total: totalFindings, color: 'bg-secondary', textColor: 'text-secondary' },
              ].map(item => (
                <div key={item.label}>
                  <div className="flex justify-between items-center mb-1">
                    <span className={`font-label-caps text-[11px] ${item.textColor}`}>{item.label}</span>
                    <span className="font-code-sm text-[12px] text-on-surface-variant">{item.val}</span>
                  </div>
                  <div className="w-full bg-surface-container-highest h-1.5 rounded-full overflow-hidden">
                    <div className={`${item.color} h-full rounded-full transition-all duration-700`} style={{ width: item.total > 0 ? `${(item.val / item.total) * 100}%` : '0%' }} />
                  </div>
                </div>
              ))}
            </div>
          )}
          <button onClick={() => navigate('/findings')} className="w-full mt-auto py-2 border border-outline-variant rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-all text-sm font-bold text-center">
            View All Findings
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
