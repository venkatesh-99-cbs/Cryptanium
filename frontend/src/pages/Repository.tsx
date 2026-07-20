import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSecurity } from '../context/SecurityContext';

const Repository: React.FC = () => {
  const { repositories, triggerScan, isScanning } = useSecurity();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'recent' | 'scanned' | 'attention'>('recent');
  const [search, setSearch] = useState('');

  const selectedIds = JSON.parse(localStorage.getItem('cryptanium_selected_repositories') || '[]') as number[];
  const filteredRepos = repositories.filter(r => selectedIds.includes(r.id)).filter(r => r.name.toLowerCase().includes(search.toLowerCase()));

  const getScoreLabel = (score: number) => {
    if (score >= 85) return { label: 'OPTIMAL', color: 'text-secondary' };
    if (score >= 75) return { label: 'SECURE', color: 'text-secondary' };
    if (score >= 60) return { label: 'FAIR', color: 'text-tertiary' };
    return { label: 'CRITICAL', color: 'text-error' };
  };

  return (
    <div className="flex-1">
      {/* Page Title */}
      <div className="mb-lg flex justify-between items-center">
        <div>
          <h2 className="text-headline-md font-headline-md font-bold text-on-background">Repositories</h2>
          <p className="text-on-surface-variant text-sm mt-1">Manage and monitor your GitHub repositories across the organization.</p>
        </div>
        <span className="px-3 py-1 rounded-full bg-surface-container text-on-surface-variant text-[11px] font-label-caps border border-outline-variant">
          TOTAL: {repositories.length}
        </span>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-sm mb-lg border-b border-outline-variant pb-xs">
        {(['recent', 'scanned', 'attention'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-md py-sm transition-all font-body-md text-sm capitalize ${activeTab === tab ? 'border-b-2 border-primary text-primary font-bold' : 'text-on-surface-variant hover:text-on-surface'}`}
          >
            {tab === 'recent' ? 'Recently Added' : tab === 'scanned' ? 'Recently Scanned' : 'Needs Attention'}
          </button>
        ))}
        <div className="ml-auto relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[18px]">search</span>
          <input
            type="text"
            placeholder="Search repositories..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="bg-surface-container-lowest border border-outline-variant rounded-lg pl-10 pr-md py-2 text-sm focus:border-primary focus:ring-0 outline-none transition-all w-56"
          />
        </div>
      </div>

      {/* Repositories List */}
      <div className="flex flex-col gap-sm">
        {filteredRepos.map(repo => {
          const { label, color } = getScoreLabel(0);
          return (
            <div
              key={repo.github_repo_id || repo.full_name || `repo-${repo.id}`}
              className="glass-card p-md flex items-center justify-between rounded-xl transition-all cursor-pointer neon-glow group"
              onClick={() => navigate(`/scans/${repo.id}`)}
            >
              <div className="flex items-center gap-lg flex-1">
                <div className="w-12 h-12 bg-surface-container-highest rounded-lg flex items-center justify-center border border-outline-variant shrink-0">
                  <span className="material-symbols-outlined text-on-surface-variant">folder_managed</span>
                </div>
                <div className="flex flex-col">
                  <h3 className="text-lg font-bold text-on-background group-hover:text-primary transition-colors">{repo.name}</h3>
                  <div className="flex items-center gap-md mt-1 flex-wrap">
                    <span className="text-on-surface-variant text-sm flex items-center gap-xs">
                      <span className="material-symbols-outlined text-[16px]">code</span>{repo.language}
                    </span>
                    <span className="text-on-surface-variant text-sm flex items-center gap-xs">
                      <span className="material-symbols-outlined text-[16px]">history</span>Updated {repo.updated_at ? new Date(repo.updated_at).toLocaleDateString() : 'Not scanned'}
                    </span>
                    {repo.private && (
                      <span className="bg-surface-container text-outline-variant text-[10px] px-2 py-0.5 rounded border border-outline-variant font-label-caps uppercase">Private</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-xl">
                <div className="flex flex-col items-end">
                  <span className="text-[10px] font-label-caps text-on-surface-variant mb-1">LAST SCAN</span>
                  <span className="text-on-surface text-sm">{repo.last_scan ? new Date(repo.last_scan).toLocaleString() : 'Not scanned'}</span>
                </div>
                <div className="flex items-center gap-md min-w-[120px] justify-end">
                  <div className="flex flex-col items-end mr-sm">
                    <span className={`text-[20px] font-bold ${color}`}>0/100</span>
                    <span className={`text-[10px] font-label-caps ${color}/60`}>{label}</span>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); triggerScan(repo.id); }}
                    disabled={isScanning}
                    className="p-1 text-on-surface-variant hover:text-primary transition-colors disabled:opacity-40"
                    title="Re-scan"
                  >
                    <span className="material-symbols-outlined text-[20px]">
                      play_arrow
                    </span>
                  </button>
                  <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary transition-colors">chevron_right</span>
                </div>
              </div>
            </div>
          );
        })}

        {filteredRepos.length === 0 && (
          <div className="glass-card rounded-xl p-xl text-center text-on-surface-variant">
            <span className="material-symbols-outlined text-[48px] opacity-40 block mb-md">folder_off</span>
            <p className="font-bold text-on-background mb-xs">No Repositories Found</p>
            <p className="text-sm">Try adjusting your search filter or add a new repository.</p>
          </div>
        )}
      </div>

      {/* Load More */}
      {filteredRepos.length > 0 && (
        <div className="mt-xl flex justify-center">
          <button className="border border-outline-variant text-on-surface-variant px-xl py-md rounded-lg font-bold hover:bg-surface-container transition-all">
            Load More Repositories
          </button>
        </div>
      )}
    </div>
  );
};

export default Repository;
