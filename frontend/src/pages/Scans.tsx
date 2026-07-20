import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSecurity } from '../context/SecurityContext';

const Scans: React.FC = () => {
  const { scans, isScanning, loadScans, isLoading } = useSecurity();
  const navigate = useNavigate();
  const [search, setSearch] = useState('');

  useEffect(() => {
    void loadScans();
  }, []);

  const filteredScans = scans.filter(s =>
    (s.repository_name || '').toLowerCase().includes(search.toLowerCase())
  );

  const getScoreColor = (score: number) =>
    score >= 80 ? 'text-secondary' : score >= 60 ? 'text-tertiary' : score > 0 ? 'text-error' : 'text-on-surface-variant';
  const getScoreBarColor = (score: number) =>
    score >= 80 ? 'bg-secondary' : score >= 60 ? 'bg-tertiary' : score > 0 ? 'bg-error' : 'bg-outline-variant';

  const getStatusStyle = (status: string) => {
    const s = status?.toLowerCase();
    if (s === 'completed' || s === 'success') return 'bg-secondary/10 border-secondary/20 text-secondary';
    if (s === 'in_progress' || s === 'running') return 'bg-primary/10 border-primary/20 text-primary';
    if (s === 'pending') return 'bg-outline/10 border-outline-variant text-outline';
    return 'bg-error/10 border-error/20 text-error';
  };

  const getStatusDot = (status: string) => {
    const s = status?.toLowerCase();
    if (s === 'completed' || s === 'success') return 'bg-secondary';
    if (s === 'in_progress' || s === 'running') return 'bg-primary animate-pulse';
    if (s === 'pending') return 'bg-outline';
    return 'bg-error';
  };

  return (
    <div className="flex-1">
      {/* Page Header */}
      <div className="mb-xl flex flex-col md:flex-row md:items-end justify-between gap-md">
        <div>
          <h2 className="text-headline-lg font-headline-lg font-semibold text-on-surface mb-xs">Security Scans</h2>
          <p className="text-on-surface-variant font-body-lg">
            {isLoading ? 'Loading scan history...' : `${scans.length} scan${scans.length !== 1 ? 's' : ''} total`}
          </p>
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
          <button
            onClick={() => void loadScans()}
            disabled={isLoading}
            className="flex items-center gap-xs px-md py-2 text-on-surface-variant hover:text-on-surface transition-colors disabled:opacity-40"
          >
            <span className={`material-symbols-outlined text-[18px] ${isLoading ? 'animate-spin' : ''}`}>refresh</span>
          </button>
        </div>
      </div>

      {/* Active Scan Banner */}
      {isScanning && (
        <div className="mb-lg glass-card rounded-xl p-md border-l-4 border-primary flex items-center gap-md">
          <span className="material-symbols-outlined text-primary animate-spin">refresh</span>
          <div>
            <p className="font-bold text-on-background text-sm">Scan in Progress</p>
            <p className="text-xs text-on-surface-variant">Running security analysis — this may take a few minutes...</p>
          </div>
          <div className="ml-auto">
            <div className="w-32 h-1.5 bg-surface-container-highest rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full animate-pulse w-2/3" />
            </div>
          </div>
        </div>
      )}

      {/* Scans Table */}
      <div className="glass-card rounded-xl overflow-hidden shadow-2xl border border-outline-variant/50">
        {scans.length === 0 && !isLoading ? (
          <div className="py-xl text-center text-on-surface-variant">
            <span className="material-symbols-outlined text-[64px] opacity-30 block mb-md">history</span>
            <p className="font-bold text-on-background text-lg">No Scans Yet</p>
            <p className="text-sm mt-2 opacity-60">
              Go to Repositories and click the scan button to start your first security scan.
            </p>
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-surface-container-high border-b border-outline-variant">
                <th className="px-lg py-4 font-label-caps text-outline uppercase tracking-widest text-[11px]">Repository</th>
                <th className="px-lg py-4 font-label-caps text-outline uppercase tracking-widest text-[11px]">Status</th>
                <th className="px-lg py-4 font-label-caps text-outline uppercase tracking-widest text-[11px]">Trust Score</th>
                <th className="px-lg py-4 font-label-caps text-outline uppercase tracking-widest text-[11px]">Findings</th>
                <th className="px-lg py-4 font-label-caps text-outline uppercase tracking-widest text-[11px]">Scanned At</th>
                <th className="px-lg py-4 font-label-caps text-outline uppercase tracking-widest text-[11px] text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/30">
              {filteredScans.map(scan => (
                <tr
                  key={scan.scan_id}
                  className="hover:bg-surface-container-highest/30 transition-colors duration-150 group cursor-pointer"
                  onClick={() => navigate(`/scans/${scan.scan_id}`)}
                >
                  <td className="px-lg py-md">
                    <div className="flex items-center gap-md">
                      <div className="w-8 h-8 rounded bg-surface-container flex items-center justify-center border border-outline-variant/50">
                        <span className="material-symbols-outlined text-primary text-[20px]">source</span>
                      </div>
                      <div>
                        <p className="font-body-md font-bold text-on-surface group-hover:text-primary transition-colors">
                          {scan.repository_name || '—'}
                        </p>
                        <p className="text-[12px] text-outline font-code-sm">
                          ID: {scan.scan_id}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-lg py-md">
                    <span className={`px-3 py-1 border text-[11px] font-bold rounded-full flex items-center gap-1 w-fit ${getStatusStyle(scan.status)}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${getStatusDot(scan.status)}`} />
                      {scan.status?.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-lg py-md">
                    <div className="flex items-center gap-sm">
                      <div className="w-16 h-1 rounded-full overflow-hidden bg-surface-container-highest">
                        <div
                          className={`h-full ${getScoreBarColor(scan.trust_score)}`}
                          style={{ width: `${scan.trust_score || 0}%` }}
                        />
                      </div>
                      <span className={`font-bold font-code-sm text-sm ${getScoreColor(scan.trust_score)}`}>
                        {scan.trust_score > 0 ? `${scan.trust_score}/100` : '—'}
                      </span>
                    </div>
                  </td>
                  <td className="px-lg py-md">
                    <span className={`font-bold text-sm ${
                      scan.findings_count === 0 ? 'text-secondary' :
                      scan.findings_count > 20 ? 'text-error' : 'text-tertiary'
                    }`}>
                      {scan.findings_count}
                    </span>
                    <span className="text-outline text-[11px] ml-1">found</span>
                  </td>
                  <td className="px-lg py-md text-on-surface-variant font-body-md text-sm">
                    {scan.created_at ? new Date(scan.created_at).toLocaleString() : '—'}
                  </td>
                  <td className="px-lg py-md text-right">
                    <button
                      onClick={(e) => { e.stopPropagation(); navigate(`/scans/${scan.scan_id}`); }}
                      className="text-primary hover:text-white font-label-caps text-[12px] border border-primary/30 hover:border-primary hover:bg-primary px-4 py-1.5 rounded transition-all"
                    >
                      VIEW
                    </button>
                  </td>
                </tr>
              ))}
              {filteredScans.length === 0 && scans.length > 0 && (
                <tr>
                  <td colSpan={6} className="py-xl text-center text-on-surface-variant">
                    <span className="material-symbols-outlined text-[48px] opacity-40 block mb-md">search_off</span>
                    <p>No scans match your search.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Scans;
