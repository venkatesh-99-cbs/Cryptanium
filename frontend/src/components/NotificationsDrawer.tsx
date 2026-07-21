import React from 'react';
import { useSecurity } from '../context/SecurityContext';

interface NotificationsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const NotificationsDrawer: React.FC<NotificationsDrawerProps> = ({ isOpen, onClose }) => {
  const { scans, findings } = useSecurity();

  if (!isOpen) return null;

  // Generate notifications from scans and critical findings
  const notifications = [
    ...scans.slice(0, 3).map((s) => ({
      id: `scan-${s.id}`,
      type: 'scan',
      title: `Scan Completed: ${s.repository_name || s.repoName || 'Repository'}`,
      desc: `Analysis finished. Trust score: ${s.trust_score ?? s.trustScore ?? 0}/100.`,
      time: s.scannedAt,
      icon: (s.trust_score ?? s.trustScore ?? 0) >= 80 ? 'check_circle' : 'warning',
      color: (s.trust_score ?? s.trustScore ?? 0) >= 80 ? 'text-secondary' : 'text-tertiary'
    })),
    ...findings.filter((f) => f.severity === 'Critical').slice(0, 2).map((f) => ({
      id: `finding-${f.id}`,
      type: 'finding',
      title: `Critical Alert in ${f.repoName || 'Repository'}`,
      desc: `${f.description || f.title || 'Security issue'} detected at ${f.file_path || f.filePath || 'unknown file'} (line ${f.line_number || f.line || 'unknown'}).`,
      time: f.date,
      icon: 'dangerous',
      color: 'text-error'
    }))
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Background overlay */}
      <div 
        onClick={onClose} 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" 
      />

      <div className="fixed inset-y-0 right-0 pl-10 max-w-full flex">
        <div className="w-screen max-w-md glass-card border-l border-outline-variant/50 flex flex-col h-full shadow-2xl">
          {/* Header */}
          <div className="px-lg py-md border-b border-outline-variant flex justify-between items-center bg-surface-container-high/50">
            <div className="flex items-center gap-sm">
              <span className="material-symbols-outlined text-primary">notifications</span>
              <h2 className="font-headline-md text-headline-md font-bold">Notifications</h2>
            </div>
            <button 
              onClick={onClose} 
              className="text-on-surface-variant hover:text-on-surface p-1 rounded-full hover:bg-surface-container-high transition-all"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>

          {/* List Content */}
          <div className="flex-1 overflow-y-auto custom-scrollbar p-md space-y-md">
            {notifications.length === 0 ? (
              <div className="text-center py-xl text-on-surface-variant">
                <span className="material-symbols-outlined text-[48px] opacity-40 mb-xs">notifications_off</span>
                <p>No new notifications</p>
              </div>
            ) : (
              notifications.map((n, index) => (
                <div 
                  key={n.id || `notification-${index}`}
                  className="p-md bg-surface-container-high/40 rounded-xl border border-outline-variant/30 hover:border-primary/20 transition-all flex gap-md group"
                >
                  <span className={`material-symbols-outlined shrink-0 ${n.color} text-[24px]`}>{n.icon}</span>
                  <div className="flex-1 space-y-xs">
                    <h3 className="font-bold text-sm text-on-background group-hover:text-primary transition-colors">{n.title}</h3>
                    <p className="text-xs text-on-surface-variant leading-relaxed">{n.desc}</p>
                    <span className="text-[10px] text-outline font-label-caps block pt-1">{n.time}</span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="p-md border-t border-outline-variant bg-surface-container/50 text-center">
            <button 
              onClick={onClose}
              className="font-label-caps text-label-caps text-primary hover:underline"
            >
              Dismiss All Alerts
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationsDrawer;
