import React, { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useSecurity } from '../context/SecurityContext';
import AddRepositoryModal from '../components/AddRepositoryModal';
import NotificationsDrawer from '../components/NotificationsDrawer';
import HelpModal from '../components/HelpModal';

const DashboardLayout: React.FC = () => {
  const { user, logout, toastMessage } = useSecurity();
  const navigate = useNavigate();
  const [isAddRepoOpen, setIsAddRepoOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const navItems = [
    { path: '/dashboard', label: 'Overview', icon: 'dashboard' },
    { path: '/repositories', label: 'Repositories', icon: 'folder_managed' },
    { path: '/scans', label: 'Scans', icon: 'data_exploration' },
    { path: '/findings', label: 'Findings', icon: 'security' },
    { path: '/reports', label: 'Reports', icon: 'analytics' },
    { path: '/assistant', label: 'AI Assistant', icon: 'smart_toy' },
    { path: '/settings', label: 'Settings', icon: 'settings' }
  ];

  return (
    <div className="bg-[#0b0e14] text-[#e1e2eb] min-h-screen font-body-md relative overflow-x-hidden">
      {toastMessage && (
        <div role="status" className="fixed right-6 top-20 z-[70] flex items-center gap-sm rounded-xl border border-secondary/30 bg-[#10251a] px-lg py-md text-secondary shadow-2xl">
          <span className="material-symbols-outlined">check_circle</span>
          <span className="text-sm font-bold">{toastMessage}</span>
        </div>
      )}
      {/* SideNavBar Rail */}
      <aside className="fixed h-full left-0 w-[240px] z-40 border-r border-outline-variant bg-surface-container-low flex flex-col py-lg hidden md:flex">
        <div className="px-md mb-xl flex items-center gap-sm">
          <img src="/cyyptanium.jpeg" alt="Cryptanium" className="w-10 h-10 rounded object-cover" />
          <div className="flex flex-col">
            <span className="text-headline-md font-headline-md font-bold tracking-tight text-on-background">CRYPTANIUM</span>
            <span className="font-label-caps text-[10px] text-outline uppercase tracking-widest leading-none">Security Suite</span>
          </div>
        </div>
        
        <nav className="flex-1 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-md px-4 py-3 mx-2 rounded transition-all duration-200 ${
                  isActive
                    ? 'bg-primary-container/20 text-primary font-bold border-l-4 border-primary scale-[0.98]'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-highest'
                }`
              }
            >
              <span className="material-symbols-outlined" style={{ fontVariationSettings: item.icon === 'dashboard' || item.icon === 'data_exploration' || item.icon === 'smart_toy' || item.icon === 'folder_managed' || item.icon === 'security' || item.icon === 'analytics' ? "'FILL' 0" : undefined }}>{item.icon}</span>
              <span className="font-body-md">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Footer Profile */}
        <div className="mt-auto px-md pt-lg border-t border-outline-variant/30">
          <div className="p-md bg-surface-container rounded-xl flex items-center gap-md border border-outline-variant/30 group hover:border-primary/30 transition-all duration-300">
            <div className="w-10 h-10 rounded-full overflow-hidden border border-primary/20 shrink-0">
              <img className="w-full h-full object-cover" alt="User avatar" src={user?.avatar_url || '/cyyptanium.jpeg'} />
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="font-body-md font-bold text-on-surface truncate">{user?.username || 'Cryptanium user'}</p>
              <p className="text-[12px] text-outline truncate">{user?.email || 'Loading profile…'}</p>
            </div>
            <button onClick={handleLogout} className="material-symbols-outlined text-on-surface-variant hover:text-error transition-colors" title="Logout">
              logout
            </button>
          </div>
        </div>
      </aside>

      {/* Top App Bar & Main Content Wrapper */}
      <div className="md:ml-[240px] flex flex-col min-h-screen relative">
        <header className="h-16 flex justify-between items-center px-margin-desktop bg-background/80 backdrop-blur-xl border-b border-outline-variant sticky top-0 z-50">
          <div className="flex items-center gap-md">
            <div className="md:hidden flex items-center gap-2 font-headline-md font-bold text-on-background mr-md"><img src="/cyyptanium.jpeg" alt="Cryptanium" className="w-8 h-8 rounded object-cover" />CRYPTANIUM</div>
            <div className="hidden md:block">
              {/* Responsive path indicator */}
              <div className="flex items-center text-on-surface-variant font-label-caps gap-xs uppercase tracking-widest text-[10px]">
                <span>Workspace</span>
                <span className="material-symbols-outlined text-[14px]">chevron_right</span>
                <span className="text-primary">Production Cluster</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-lg">
            <div className="flex items-center gap-sm">
              <button 
                onClick={() => setIsNotificationsOpen(true)}
                className="p-2 text-on-surface-variant hover:bg-surface-container-high rounded-full transition-all relative"
              >
                <span className="material-symbols-outlined">notifications</span>
                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-error animate-pulse"></span>
              </button>
              <button 
                onClick={() => setIsHelpOpen(true)}
                className="p-2 text-on-surface-variant hover:bg-surface-container-high rounded-full transition-all"
              >
                <span className="material-symbols-outlined">help_outline</span>
              </button>
            </div>
            
            <button 
              onClick={() => setIsAddRepoOpen(true)}
              className="bg-primary text-on-primary px-4 py-2 rounded-lg font-bold font-body-md flex items-center gap-sm hover:opacity-90 active:scale-[0.98] transition-all"
            >
              <span className="material-symbols-outlined">add</span>
              <span>Add Repository</span>
            </button>
          </div>
        </header>

        {/* Content Canvas */}
        <main className="flex-1 p-margin-mobile md:p-margin-desktop relative min-h-[calc(100vh-64px)] flex flex-col">
          <Outlet />
        </main>
      </div>

      {/* Overlays / Modals */}
      <AddRepositoryModal isOpen={isAddRepoOpen} onClose={() => setIsAddRepoOpen(false)} />
      <NotificationsDrawer isOpen={isNotificationsOpen} onClose={() => setIsNotificationsOpen(false)} />
      <HelpModal isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />
    </div>
  );
};

export default DashboardLayout;
