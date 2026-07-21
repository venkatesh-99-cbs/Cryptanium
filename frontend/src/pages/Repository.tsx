import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSecurity } from '../context/SecurityContext';

const Repository: React.FC = () => {
  const { repositories, scans, triggerScan, isScanning, activeScanRepo, loadRepositories, isLoading, addRepository } = useSecurity();
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [selectedRepoId, setSelectedRepoId] = useState('');
  const [adding, setAdding] = useState(false);
  const [connectedRepoIds, setConnectedRepoIds] = useState<string[]>(() => {
    try { return JSON.parse(localStorage.getItem('cryptanium_selected_repositories') || '[]').map(String); } catch { return []; }
  });

  useEffect(() => {
    void loadRepositories();
  }, []);

  const visibleRepos = connectedRepoIds.length
    ? repositories.filter(r => connectedRepoIds.includes(String(r.id ?? r.github_repo_id ?? r.full_name)))
    : [];
  const filteredRepos = visibleRepos.filter(r =>
    (r.name || '').toLowerCase().includes(search.toLowerCase()) ||
    (r.full_name || '').toLowerCase().includes(search.toLowerCase())
  );

  // Get the latest scan trust score for a repo
  const getRepoScan = (repoId: number) => {
    return scans.find(s => String(s.repository_id) === String(repoId));
  };

  const getScoreLabel = (score: number) => {
    if (score >= 85) return { label: 'OPTIMAL', color: 'text-secondary' };
    if (score >= 75) return { label: 'SECURE', color: 'text-secondary' };
    if (score >= 60) return { label: 'FAIR', color: 'text-tertiary' };
    if (score > 0) return { label: 'CRITICAL', color: 'text-error' };
    return { label: 'NOT SCANNED', color: 'text-on-surface-variant' };
  };

  const handleAddRepository = async () => {
    const repo = repositories.find(item => String(item.id ?? item.github_repo_id ?? item.full_name) === selectedRepoId);
    if (!repo) return;
    setAdding(true);
    try {
      await addRepository(repo.clone_url || repo.full_name);
      const key = String(repo.id ?? repo.github_repo_id ?? repo.full_name);
      const next = connectedRepoIds.includes(key) ? connectedRepoIds : [...connectedRepoIds, key];
      localStorage.setItem('cryptanium_selected_repositories', JSON.stringify(next));
      setConnectedRepoIds(next);
      setSelectedRepoId('');
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="flex-1">
      {/* Page Title */}
      <div className="mb-lg flex justify-between items-center">
        <div>
          <h2 className="text-headline-md font-headline-md font-bold text-on-background">Repositories</h2>
          <p className="text-on-surface-variant text-sm mt-1">
            {isLoading
              ? 'Loading repositories...'
              : repositories.length === 0
              ? 'Login with GitHub to see your repositories'
              : `${visibleRepos.length} repositories connected`}
          </p>
        </div>
        <span className="px-3 py-1 rounded-full bg-surface-container text-on-surface-variant text-[11px] font-label-caps border border-outline-variant">
          TOTAL: {visibleRepos.length}
        </span>
      </div>

      {/* Search + Add */}
      <div className="mb-lg flex flex-col md:flex-row items-stretch gap-md">
        <div className="relative flex-1 max-w-sm">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[18px]">search</span>
          <input
            type="text"
            placeholder="Search repositories..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg pl-10 pr-md py-2 text-sm focus:border-primary focus:ring-0 outline-none transition-all"
          />
        </div>
        <div className="flex flex-1 md:max-w-md gap-sm">
          <select aria-label="Select GitHub repository" value={selectedRepoId} onChange={e => setSelectedRepoId(e.target.value)} className="flex-1 bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-2 text-sm focus:border-primary focus:ring-0 outline-none transition-all">
            <option value="">Select a GitHub repository</option>
            {repositories.map(repo => <option key={repo.id ?? repo.github_repo_id ?? repo.full_name} value={repo.id ?? repo.github_repo_id ?? repo.full_name}>{repo.full_name || repo.name}</option>)}
          </select>
          <button
            onClick={() => void handleAddRepository()}
            disabled={adding || !selectedRepoId}
            className="flex items-center gap-xs px-md py-2 rounded-lg bg-primary text-white text-sm disabled:opacity-40"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            {adding ? 'Adding...' : 'Add'}
          </button>
        </div>
        <button
          onClick={() => void loadRepositories()}
          disabled={isLoading}
          className="flex items-center gap-xs px-md py-2 border border-outline-variant rounded-lg text-on-surface-variant hover:text-on-surface transition-colors disabled:opacity-40 text-sm"
        >
          <span className={`material-symbols-outlined text-[18px] ${isLoading ? 'animate-spin' : ''}`}>refresh</span>
          Refresh
        </button>
      </div>

      {/* Repositories List */}
      {filteredRepos.length === 0 ? (
        <div className="glass-card rounded-xl p-xl text-center text-on-surface-variant">
          <span className="material-symbols-outlined text-[64px] opacity-30 block mb-md">folder_off</span>
          <p className="font-bold text-on-background text-lg">
            {isLoading ? 'Loading...' : visibleRepos.length === 0 ? 'No Repositories Selected' : 'No Matches'}
          </p>
          <p className="text-sm mt-2 opacity-60">
            {visibleRepos.length === 0
              ? 'Use Add Repository to select a repository from your GitHub account.'
              : 'Try adjusting your search.'}
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-sm">
          {filteredRepos.map(repo => {
            const latestScan = getRepoScan(repo.id);
            const score = latestScan?.trust_score || 0;
            const { label, color } = getScoreLabel(score);
            const isActiveRepo = activeScanRepo === String(repo.id);

            return (
              <div
                key={repo.id ?? repo.github_repo_id ?? repo.full_name}
                className="glass-card p-md flex items-center justify-between rounded-xl transition-all cursor-pointer hover:border-primary/20 group"
                onClick={() => latestScan ? navigate(`/scans/${latestScan.scan_id}`) : undefined}
              >
                <div className="flex items-center gap-lg flex-1 min-w-0">
                  <div className="w-12 h-12 bg-surface-container-highest rounded-lg flex items-center justify-center border border-outline-variant shrink-0">
                    <span className="material-symbols-outlined text-primary">
                      {repo.visibility === 'private' ? 'lock' : 'folder_managed'}
                    </span>
                  </div>
                  <div className="flex flex-col min-w-0">
                    <h3 className="text-lg font-bold text-on-background group-hover:text-primary transition-colors truncate">
                      {repo.name}
                    </h3>
                    <div className="flex items-center gap-md mt-1 flex-wrap">
                      {repo.language && (
                        <span className="text-on-surface-variant text-sm flex items-center gap-xs">
                          <span className="material-symbols-outlined text-[16px]">code</span>
                          {repo.language}
                        </span>
                      )}
                      <span className="text-on-surface-variant text-sm flex items-center gap-xs">
                        <span className="material-symbols-outlined text-[16px]">account_tree</span>
                        {repo.default_branch}
                      </span>
                      {(repo.visibility === 'private') && (
                        <span className="bg-surface-container text-outline-variant text-[10px] px-2 py-0.5 rounded border border-outline-variant font-label-caps uppercase">Private</span>
                      )}
                      {latestScan && (
                        <span className="text-on-surface-variant text-xs flex items-center gap-xs">
                          <span className="material-symbols-outlined text-[14px]">history</span>
                          {latestScan.findings_count} findings
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-xl shrink-0">
                  {/* Last scan time */}
                  <div className="flex flex-col items-end hidden md:flex">
                    <span className="text-[10px] font-label-caps text-on-surface-variant mb-1">LAST SCAN</span>
                    <span className="text-on-surface text-sm">
                      {latestScan?.created_at
                        ? new Date(latestScan.created_at).toLocaleDateString()
                        : '—'}
                    </span>
                  </div>

                  {/* Trust Score */}
                  <div className="flex items-center gap-md min-w-[120px] justify-end">
                    <div className="flex flex-col items-end mr-sm">
                      <span className={`text-[20px] font-bold ${color}`}>
                        {score > 0 ? `${score}/100` : '—'}
                      </span>
                      <span className={`text-[10px] font-label-caps opacity-70 ${color}`}>{label}</span>
                    </div>

                    {/* Scan button */}
                    <button
                      onClick={e => { e.stopPropagation(); triggerScan(repo.id); }}
                      disabled={isScanning}
                      className={`p-2 rounded-lg transition-colors disabled:opacity-40 ${
                        isActiveRepo
                          ? 'bg-primary/10 text-primary'
                          : 'text-on-surface-variant hover:text-primary hover:bg-primary/5'
                      }`}
                      title={isActiveRepo ? 'Scanning...' : 'Run security scan'}
                    >
                      <span className={`material-symbols-outlined text-[20px] ${isActiveRepo ? 'animate-spin' : ''}`}>
                        {isActiveRepo ? 'refresh' : 'play_arrow'}
                      </span>
                    </button>

                    <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary transition-colors">
                      chevron_right
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Repository;
