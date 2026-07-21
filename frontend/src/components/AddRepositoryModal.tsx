import React, { useState } from 'react';
import { useSecurity } from '../context/SecurityContext';

const AddRepositoryModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const { repositories, addRepository } = useSecurity();
  const [selectedId, setSelectedId] = useState('');
  if (!isOpen) return null;
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    const repo = repositories.find(item => String(item.id ?? item.github_repo_id ?? item.full_name) === selectedId);
    if (!repo) return;
    const selected = JSON.parse(localStorage.getItem('cryptanium_selected_repositories') || '[]') as Array<string | number>;
    const repoKey = repo.id ?? repo.github_repo_id ?? repo.full_name;
    if (!selected.includes(repoKey)) selected.push(repoKey);
    localStorage.setItem('cryptanium_selected_repositories', JSON.stringify(selected));
    await addRepository(repo.clone_url || '');
    setSelectedId(''); onClose();
  };
  return <div className="fixed inset-0 bg-black/70 backdrop-blur-md z-50 flex items-center justify-center p-md">
    <div className="glass-card rounded-xl p-xl max-w-[480px] w-full border border-outline-variant/50 relative">
      <button onClick={onClose} className="absolute top-md right-md text-on-surface-variant"><span className="material-symbols-outlined">close</span></button>
      <h2 className="font-headline-md text-headline-md text-on-background mb-sm">Add GitHub Repository</h2>
      <p className="text-on-surface-variant mb-lg">Select only from repositories available in your GitHub account.</p>
      <form onSubmit={submit} className="space-y-lg">
        <select aria-label="GitHub repository" required value={selectedId} onChange={e => setSelectedId(e.target.value)} className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-3 text-on-background">
          <option value="">Choose a repository</option>
          {repositories.map(repo => <option key={repo.id ?? repo.github_repo_id ?? repo.full_name} value={repo.id ?? repo.github_repo_id ?? repo.full_name}>{repo.full_name || repo.name}</option>)}
        </select>
        <div className="flex gap-md"><button type="button" onClick={onClose} className="flex-1 py-2 rounded-lg border border-outline-variant">Cancel</button><button type="submit" className="flex-1 py-2 bg-primary text-on-primary rounded-lg font-bold">Add Repository</button></div>
      </form>
    </div>
  </div>;
};
export default AddRepositoryModal;
