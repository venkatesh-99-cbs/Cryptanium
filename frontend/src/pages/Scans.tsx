import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSecurity } from '../context/SecurityContext';

const Scans: React.FC = () => {
  const { scans, repositories, isScanning, triggerScan } = useSecurity();
  const navigate = useNavigate();
  const [search, setSearch] = useState('');

  const filteredScans = scans.filter(s => s.repoName.toLowerCase().includes(search.toLowerCase()));

  const getScoreColor = (score: number) => score >= 80 ? 'text-secondary' : score >= 60 ? 'text-tertiary' : 'text-error';
  const getScoreBarColor = (score: number) => score >= 80 ? 'bg-secondary' : score >= 60 ? 'bg-tertiary' : 'bg-error';

  return (
    <div className="flex-1">
      {/* Page Header */}
      <div className="mb-xl flex flex-col md:flex-row md:items-end justify-between gap-md">
        <div>
          <h2 className="text-headline-lg font-headline-lg font-semibold text-on-surface mb-xs">Historical Scans</h2>
          <p className="text-on-surface-variant font-body-lg">Monitor the security health and scan history of all your active repositories.</p>
        </div>
        <div className="flex items-center gap-md bg-surface-container-low border border-outline-variant p-1 rounded-lg">
          <div className="flex items-center px-md gap-sm border-r border-outline-variant">
            <span className="material-symbols-outlined text-outline text-[20px]">search</span>
            <input
              className="bg-transparent border-none focus:ring-0 text-body-md text-on-surface w-48 placeholder:text-outline outline-none"
              placeholder="Search repository..."
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <button className="flex items-center gap-xs px-md py-2 text-on-surface-variant hover:text-on-surface transition-colors">
            <span className="material-symbols-outlined text-[18px]">filter_list</span>
            <span className="font-label-caps">Filters</span>
          </button>
        </div>
      </div>

      {/* Active Scan Banner */}
      {isScanning && (
        <div className="mb-lg glass-card rounded-xl p-md border-l-4 border-primary flex items-center gap-md">
          <span className="material-symbols-outlined text-primary animate-spin">refresh</span>
          <div>
            <p className="font-bold text-on-background text-sm">Scan in Progress</p>
            <p className="text-xs text-on-surface-variant">Running security analysis across all configured tools...</p>
          </div>
          <div className="ml-auto">
            <div className="w-32 h-1.5 bg-surface-container-highest rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full animate-pulse w-2/3" />
            </div>
          </div>
        </div>
      )}

      {/* Scans Data Table */}
      <div className="glass-card rounded-xl overflow-hidden shadow-2xl border border-outline-variant/50">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-surface-container-high border-b border-outline-variant">
              <th className="px-lg py-4 font-label-caps text-outline uppercase tracking-widest text-[11px]">Repository</th>
              <th className="px-lg py-4 font-label-caps text-outline uppercase tracking-widest text-[11px]">Branch</th>
              <th className="px-lg py-4 font-label-caps text-outline uppercase tracking-widest text-[11px]">Status</th>
              <th className="px-lg py-4 font-label-caps text-outline uppercase tracking-widest text-[11px]">Trust Score</th>
              <th className="px-lg py-4 font-label-caps text-outline uppercase tracking-widest text-[11px]">Scanned At</th>
              <th className="px-lg py-4 font-label-caps text-outline uppercase tracking-widest text-[11px] text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/30">
            {filteredScans.map(scan => (
              <tr key={scan.id} className="hover:bg-surface-container-highest/30 transition-colors duration-150 group">
                <td className="px-lg py-md">
                  <div className="flex items-center gap-md">
                    <div className="w-8 h-8 rounded bg-surface-container flex items-center justify-center border border-outline-variant/50">
                      <span className="material-symbols-outlined text-primary text-[20px]">
                        {repositories.find(r => r.id === scan.repoId)?.icon || 'terminal'}
                      </span>
                    </div>
                    <div>
                      <p className="font-body-md font-bold text-on-surface group-hover:text-primary transition-colors">{scan.repoName}</p>
                      <p className="text-[12px] text-outline font-code-sm">github.com/alex/{scan.repoName}</p>
                    </div>
                  </div>
                </td>
                <td className="px-lg py-md">
                  <span className="font-code-sm text-on-surface-variant bg-surface-container-highest px-2 py-1 rounded">{scan.branch}</span>
                </td>
                <td className="px-lg py-md">
                  <span className={`px-3 py-1 border text-[11px] font-bold rounded-full flex items-center gap-1 w-fit ${
                    scan.status === 'COMPLETED' ? 'bg-secondary/10 border-secondary/20 text-secondary' :
                    scan.status === 'RUNNING' ? 'bg-primary/10 border-primary/20 text-primary' :
                    'bg-error/10 border-error/20 text-error'
                  }`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      scan.status === 'COMPLETED' ? 'bg-secondary' :
                      scan.status === 'RUNNING' ? 'bg-primary animate-pulse' : 'bg-error'
                    }`} />
                    {scan.status}
                  </span>
                </td>
                <td className="px-lg py-md">
                  <div className="flex items-center gap-sm">
                    <div className="w-16 h-1 rounded-full overflow-hidden bg-surface-container-highest">
                      <div className={`h-full ${getScoreBarColor(scan.trustScore)}`} style={{ width: `${scan.trustScore}%` }} />
                    </div>
                    <span className={`font-bold font-code-sm text-sm ${getScoreColor(scan.trustScore)}`}>{scan.trustScore}/100</span>
                  </div>
                </td>
                <td className="px-lg py-md text-on-surface-variant font-body-md">{scan.scannedAt}</td>
                <td className="px-lg py-md text-right">
                  <button
                    onClick={() => navigate(`/scans/${scan.repoId}`)}
                    className="text-primary hover:text-white font-label-caps text-[12px] border border-primary/30 hover:border-primary hover:bg-primary px-4 py-1.5 rounded transition-all neon-glow"
                  >
                    SCAN DETAILS
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredScans.length === 0 && (
          <div className="py-xl text-center text-on-surface-variant">
            <span className="material-symbols-outlined text-[48px] opacity-40 block mb-md">data_exploration</span>
            <p>No scans found matching your search.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Scans;
