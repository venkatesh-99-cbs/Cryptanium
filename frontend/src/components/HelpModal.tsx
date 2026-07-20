import React from 'react';

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const HelpModal: React.FC<HelpModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const scanners = [
    { name: 'Semgrep', desc: 'Static Application Security Testing (SAST) for Python, JS/TS, Go, and Ruby. Detects framework vulnerabilities and logic flaws.', color: 'text-primary' },
    { name: 'Bandit', desc: 'Security scanner for Python code. Identifies common issues like shell command injection, insecure permissions, and pickles.', color: 'text-secondary' },
    { name: 'Gitleaks', desc: 'Secret detection scanner. Audits repositories for hardcoded AWS keys, database connection strings, SSH keys, and credentials.', color: 'text-tertiary' },
    { name: 'npm audit & pip-audit', desc: 'Dependency vulnerability scanners. Evaluates package-lock.json and requirements.txt for outdated, vulnerable packages.', color: 'text-error' },
    { name: 'ESLint', desc: 'Code quality and syntax linter. Ensures basic syntax correctness, unused declarations, and code cleanliness.', color: 'text-on-surface-variant' }
  ];

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-md z-50 flex items-center justify-center p-md">
      <div className="glass-card rounded-xl p-xl max-w-2xl w-full border border-outline-variant/50 relative shadow-2xl flex flex-col max-h-[90vh]">
        <button 
          onClick={onClose} 
          className="absolute top-md right-md text-on-surface-variant hover:text-on-surface transition-colors"
        >
          <span className="material-symbols-outlined">close</span>
        </button>

        <div className="mb-lg shrink-0">
          <div className="w-12 h-12 rounded-lg bg-primary-container/20 border border-primary/20 flex items-center justify-center text-primary mb-md">
            <span className="material-symbols-outlined text-[32px]">help_outline</span>
          </div>
          <h2 className="font-headline-md text-headline-md text-on-background">Cryptanium Documentation</h2>
          <p className="font-body-md text-body-md text-on-surface-variant mt-1">Understanding security scans, scanners, and calculations.</p>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-lg">
          {/* Trust Score Calculation */}
          <div className="p-md bg-surface-container rounded-xl border border-outline-variant/30">
            <h3 className="font-bold text-sm text-secondary flex items-center gap-2 mb-1">
              <span className="material-symbols-outlined text-sm">calculate</span> Trust Score Calculation
            </h3>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              The Security Trust Score is computed out of 100 based on the density and severity of vulnerabilities discovered:
              <br/>
              - <strong className="text-error">Critical Severity</strong>: Deducts 10 points per finding.
              <br/>
              - <strong className="text-tertiary">High Severity</strong>: Deducts 5 points per finding.
              <br/>
              - <strong className="text-[#ffcc00]">Medium Severity</strong>: Deducts 2 points per finding.
              <br/>
              - <strong className="text-secondary">Low Severity</strong>: Deducts 0.5 points per finding.
              <br/>
              Postures scoring &ge; 80 are rated <span className="text-secondary font-bold">Good</span>, 60-79 are <span className="text-tertiary font-bold">Needs Attention</span>, and &lt; 60 are <span className="text-error font-bold">Critical</span>.
            </p>
          </div>

          {/* Scanners */}
          <div className="space-y-md">
            <h3 className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider">Built-in Scanners</h3>
            <div className="grid gap-sm">
              {scanners.map((s) => (
                <div key={s.name} className="p-md bg-surface-container-high/40 rounded-lg border border-outline-variant/20 flex gap-md">
                  <div className="shrink-0 flex items-center pt-0.5">
                    <span className={`material-symbols-outlined text-[20px] ${s.color}`}>shield</span>
                  </div>
                  <div className="space-y-0.5">
                    <h4 className="font-bold text-sm text-on-background">{s.name}</h4>
                    <p className="text-xs text-on-surface-variant leading-relaxed">{s.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-xl pt-md border-t border-outline-variant/30 flex justify-end shrink-0">
          <button 
            onClick={onClose}
            className="px-lg py-2 bg-primary text-on-primary font-bold rounded-lg hover:opacity-90 active:scale-95 transition-all text-sm shadow-[0_0_15px_rgba(123,97,255,0.2)]"
          >
            Acknowledge
          </button>
        </div>
      </div>
    </div>
  );
};

export default HelpModal;
