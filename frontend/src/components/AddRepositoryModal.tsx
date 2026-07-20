import React, { useState } from 'react';
import { useSecurity } from '../context/SecurityContext';

interface AddRepositoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AddRepositoryModal: React.FC<AddRepositoryModalProps> = ({ isOpen, onClose }) => {
  const { addRepository } = useSecurity();
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [isPrivate, setIsPrivate] = useState(true);
  const [language, setLanguage] = useState('Python');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !url) return;
    addRepository(name, url, isPrivate, language);
    setName('');
    setUrl('');
    setIsPrivate(true);
    setLanguage('Python');
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-md z-50 flex items-center justify-center p-md">
      <div className="glass-card rounded-xl p-xl max-w-[480px] w-full border border-outline-variant/50 relative shadow-2xl">
        <button 
          onClick={onClose} 
          className="absolute top-md right-md text-on-surface-variant hover:text-on-surface transition-colors"
        >
          <span className="material-symbols-outlined">close</span>
        </button>

        <div className="mb-lg">
          <div className="w-12 h-12 rounded-lg bg-primary-container/20 border border-primary/20 flex items-center justify-center text-primary mb-md">
            <span className="material-symbols-outlined text-[32px]">add_box</span>
          </div>
          <h2 className="font-headline-md text-headline-md text-on-background">Add Repository</h2>
          <p className="font-body-md text-body-md text-on-surface-variant mt-1">Import a GitHub repository to trigger security analysis.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-md">
          {/* Repository Name */}
          <div className="space-y-xs">
            <label className="font-label-caps text-label-caps text-on-surface-variant block uppercase" htmlFor="repo-name">Repository Name</label>
            <input 
              type="text" 
              id="repo-name" 
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. auth-gateway-api"
              required
              className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-2 text-body-md text-on-background placeholder:text-outline-variant/60 focus:border-primary focus:ring-0 outline-none transition-all duration-300"
            />
          </div>

          {/* Repository URL */}
          <div className="space-y-xs">
            <label className="font-label-caps text-label-caps text-on-surface-variant block uppercase" htmlFor="repo-url">GitHub Repository URL</label>
            <div className="relative flex items-center">
              <span className="material-symbols-outlined absolute left-3 text-outline text-[18px]">link</span>
              <input 
                type="text" 
                id="repo-url" 
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="github.com/org/repo"
                required
                className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg pl-10 pr-md py-2 text-body-md text-on-background placeholder:text-outline-variant/60 focus:border-primary focus:ring-0 outline-none transition-all duration-300"
              />
            </div>
          </div>

          {/* Primary Language */}
          <div className="space-y-xs">
            <label className="font-label-caps text-label-caps text-on-surface-variant block uppercase" htmlFor="repo-lang">Primary Language</label>
            <select 
              id="repo-lang" 
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-md py-2 text-body-md text-on-background focus:border-primary focus:ring-0 outline-none transition-all duration-300"
            >
              <option value="Python">Python</option>
              <option value="JavaScript">JavaScript</option>
              <option value="TypeScript">TypeScript</option>
              <option value="Go">Go</option>
              <option value="YAML">YAML / DevOps</option>
            </select>
          </div>

          {/* Visibility */}
          <div className="pt-sm space-y-sm">
            <label className="font-label-caps text-label-caps text-on-surface-variant block uppercase">Visibility</label>
            <div className="flex gap-lg">
              <label className="flex items-center gap-sm cursor-pointer select-none">
                <input 
                  type="radio" 
                  name="visibility" 
                  checked={isPrivate} 
                  onChange={() => setIsPrivate(true)}
                  className="w-4 h-4 rounded-full border-outline-variant text-primary focus:ring-primary/20 bg-surface-container-lowest" 
                />
                <span className="font-body-md text-on-surface-variant flex items-center gap-1">
                  <span className="material-symbols-outlined text-[18px]">lock</span> Private
                </span>
              </label>
              <label className="flex items-center gap-sm cursor-pointer select-none">
                <input 
                  type="radio" 
                  name="visibility" 
                  checked={!isPrivate} 
                  onChange={() => setIsPrivate(false)}
                  className="w-4 h-4 rounded-full border-outline-variant text-primary focus:ring-primary/20 bg-surface-container-lowest" 
                />
                <span className="font-body-md text-on-surface-variant flex items-center gap-1">
                  <span className="material-symbols-outlined text-[18px]">public</span> Public
                </span>
              </label>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-md pt-md">
            <button 
              type="button" 
              onClick={onClose}
              className="flex-1 py-2 rounded-lg border border-outline-variant text-on-surface-variant font-bold hover:bg-surface-container transition-all text-center text-sm"
            >
              Cancel
            </button>
            <button 
              type="submit"
              className="flex-1 py-2 bg-primary text-on-primary font-bold rounded-lg hover:opacity-90 active:scale-95 transition-all text-center text-sm shadow-[0_0_15px_rgba(123,97,255,0.25)]"
            >
              Import & Scan
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddRepositoryModal;
