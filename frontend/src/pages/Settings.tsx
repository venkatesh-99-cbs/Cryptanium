import React, { useState } from 'react';
import { useSecurity } from '../context/SecurityContext';

type Tab = 'profile' | 'notifications' | 'integrations' | 'security' | 'team';

const Settings: React.FC = () => {
  const { user, logout } = useSecurity();
  const [activeTab, setActiveTab] = useState<Tab>('profile');
  const [saveStatus, setSaveStatus] = useState('');
  const [profile, setProfile] = useState({
    name: user?.name ?? 'Alex Johnson',
    email: user?.email ?? 'alex@company.io',
    org: 'Acme Corp',
    role: 'Lead Security Engineer',
  });
  const [notifications, setNotifications] = useState({
    emailCritical: true,
    emailSummary: false,
    slackCritical: true,
    inAppAll: true,
    inAppScans: true,
  });
  const [tokens, setTokens] = useState({
    github: 'ghp_•••••••••••••••••••••••••••••',
    slack: '',
    jira: '',
  });

  const handleSave = async () => {
    setSaveStatus('saving');
    await new Promise(r => setTimeout(r, 800));
    setSaveStatus('saved');
    setTimeout(() => setSaveStatus(''), 2500);
  };

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'profile', label: 'Profile', icon: 'person' },
    { id: 'notifications', label: 'Notifications', icon: 'notifications' },
    { id: 'integrations', label: 'Integrations', icon: 'hub' },
    { id: 'security', label: 'Security', icon: 'lock' },
    { id: 'team', label: 'Team', icon: 'group' },
  ];

  return (
    <div className="flex-1">
      {/* Header */}
      <div className="mb-xl">
        <h2 className="text-headline-md font-headline-md font-bold text-on-background">Settings</h2>
        <p className="text-on-surface-variant text-sm mt-1">Manage your account, integrations, and notification preferences.</p>
      </div>

      <div className="flex flex-col md:flex-row gap-gutter">
        {/* Sidebar Nav */}
        <aside className="w-full md:w-[220px] shrink-0">
          <nav className="glass-card rounded-xl p-sm flex flex-row md:flex-col gap-xs">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-md px-md py-sm rounded-lg w-full text-left transition-all font-body-md text-sm ${activeTab === tab.id ? 'bg-primary/10 text-primary font-bold' : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'}`}
              >
                <span className="material-symbols-outlined text-[20px]">{tab.icon}</span>
                <span className="hidden md:inline">{tab.label}</span>
              </button>
            ))}
            <div className="flex-1 md:mt-auto md:border-t md:border-outline-variant/30 md:pt-sm">
              <button
                onClick={logout}
                className="flex items-center gap-md px-md py-sm rounded-lg w-full text-left text-error hover:bg-error/10 transition-all font-body-md text-sm"
              >
                <span className="material-symbols-outlined text-[20px]">logout</span>
                <span className="hidden md:inline">Log Out</span>
              </button>
            </div>
          </nav>
        </aside>

        {/* Content */}
        <div className="flex-1 min-w-0">

          {/* Profile */}
          {activeTab === 'profile' && (
            <div className="glass-card rounded-xl p-xl space-y-lg">
              <h3 className="font-bold text-on-background border-b border-outline-variant pb-md">Profile Information</h3>

              {/* Avatar */}
              <div className="flex items-center gap-xl">
                <div className="relative w-20 h-20 rounded-full bg-surface-container-highest border-2 border-primary/30 flex items-center justify-center">
                  <span className="material-symbols-outlined text-primary text-[40px]">person</span>
                  <div className="absolute bottom-0 right-0 w-6 h-6 bg-primary rounded-full flex items-center justify-center border-2 border-background">
                    <span className="material-symbols-outlined text-[14px] text-on-primary">edit</span>
                  </div>
                </div>
                <div>
                  <p className="font-bold text-on-background">{profile.name}</p>
                  <p className="text-sm text-on-surface-variant">{profile.role}</p>
                  <button className="text-primary text-sm hover:underline mt-xs">Change avatar</button>
                </div>
              </div>

              {/* Form Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
                {[
                  { label: 'Full Name', key: 'name', type: 'text', icon: 'person' },
                  { label: 'Email Address', key: 'email', type: 'email', icon: 'alternate_email' },
                  { label: 'Organization', key: 'org', type: 'text', icon: 'business' },
                  { label: 'Role', key: 'role', type: 'text', icon: 'badge' },
                ].map(field => (
                  <div key={field.key} className="flex flex-col gap-xs">
                    <label className="font-label-caps text-[11px] text-on-surface-variant uppercase">{field.label}</label>
                    <div className="relative group/input">
                      <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline group-focus-within/input:text-primary transition-colors text-[20px]">{field.icon}</span>
                      <input
                        type={field.type}
                        value={(profile as any)[field.key]}
                        onChange={e => setProfile({ ...profile, [field.key]: e.target.value })}
                        className="w-full bg-background border border-outline-variant rounded-lg pl-10 pr-md py-md text-body-md text-on-background outline-none focus:border-primary transition-all"
                      />
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={handleSave}
                className="flex items-center gap-sm bg-[#7B61FF] text-white px-xl py-md rounded-lg font-bold hover:bg-opacity-90 transition-all shadow-[0_0_15px_rgba(123,97,255,0.3)] disabled:opacity-60"
              >
                {saveStatus === 'saving' ? <><span className="material-symbols-outlined animate-spin">refresh</span> Saving...</> :
                 saveStatus === 'saved' ? <><span className="material-symbols-outlined">check_circle</span> Saved!</> :
                 <><span className="material-symbols-outlined">save</span> Save Changes</>}
              </button>
            </div>
          )}

          {/* Notifications */}
          {activeTab === 'notifications' && (
            <div className="glass-card rounded-xl p-xl space-y-lg">
              <h3 className="font-bold text-on-background border-b border-outline-variant pb-md">Notification Preferences</h3>
              <div className="space-y-md">
                {[
                  { key: 'emailCritical', label: 'Email alerts for critical findings', desc: 'Get emailed instantly when a critical vulnerability is found', icon: 'email' },
                  { key: 'emailSummary', label: 'Weekly email digest', desc: 'Summary of all findings from the past week', icon: 'summarize' },
                  { key: 'slackCritical', label: 'Slack notifications for critical findings', desc: 'Post a message to your Slack channel on critical issues', icon: 'chat' },
                  { key: 'inAppAll', label: 'In-app notifications for all findings', desc: 'Show badges and alerts in the dashboard', icon: 'notifications' },
                  { key: 'inAppScans', label: 'In-app scan completion alerts', desc: 'Notify when a scan finishes', icon: 'notifications_active' },
                ].map(item => (
                  <div key={item.key} className="flex items-center justify-between py-md border-b border-outline-variant/30">
                    <div className="flex items-start gap-md">
                      <span className="material-symbols-outlined text-on-surface-variant text-[22px] mt-0.5">{item.icon}</span>
                      <div>
                        <p className="font-bold text-on-background text-sm">{item.label}</p>
                        <p className="text-on-surface-variant text-sm">{item.desc}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setNotifications(prev => ({ ...prev, [item.key]: !(prev as any)[item.key] }))}
                      className={`relative w-12 h-6 rounded-full transition-colors ${(notifications as any)[item.key] ? 'bg-primary' : 'bg-surface-container-highest'}`}
                    >
                      <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-all ${(notifications as any)[item.key] ? 'left-6' : 'left-0.5'}`} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Integrations */}
          {activeTab === 'integrations' && (
            <div className="glass-card rounded-xl p-xl space-y-lg">
              <h3 className="font-bold text-on-background border-b border-outline-variant pb-md">Tool Integrations</h3>
              <div className="space-y-lg">
                {[
                  { key: 'github', label: 'GitHub Personal Access Token', icon: 'hub', connected: true },
                  { key: 'slack', label: 'Slack Bot Token', icon: 'chat', connected: false },
                  { key: 'jira', label: 'Jira API Token', icon: 'confirmation_number', connected: false },
                ].map(integration => (
                  <div key={integration.key} className="flex flex-col gap-xs">
                    <div className="flex items-center justify-between mb-xs">
                      <label className="flex items-center gap-sm font-label-caps text-[11px] text-on-surface-variant uppercase">
                        <span className="material-symbols-outlined text-[18px]">{integration.icon}</span>
                        {integration.label}
                      </label>
                      <span className={`text-[10px] font-label-caps px-2 py-0.5 rounded-full border ${integration.connected ? 'text-secondary border-secondary/30 bg-secondary/10' : 'text-outline border-outline-variant'}`}>
                        {integration.connected ? 'Connected' : 'Not Connected'}
                      </span>
                    </div>
                    <div className="flex gap-sm">
                      <input
                        type="password"
                        value={(tokens as any)[integration.key]}
                        onChange={e => setTokens({ ...tokens, [integration.key]: e.target.value })}
                        placeholder={`Enter your ${integration.label.split(' ')[0]} token...`}
                        className="flex-1 bg-background border border-outline-variant rounded-lg px-md py-md text-body-md text-on-background outline-none focus:border-primary transition-all font-code-sm text-sm"
                      />
                      <button className="border border-outline-variant text-on-surface-variant px-md py-md rounded-lg hover:border-primary hover:text-primary transition-all text-sm font-bold">
                        {integration.connected ? 'Update' : 'Connect'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Security Tool Status */}
              <div className="mt-xl border-t border-outline-variant pt-lg">
                <h4 className="font-label-caps text-[11px] uppercase tracking-wider text-on-surface-variant mb-md">Installed Scanning Tools</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-md">
                  {[
                    { name: 'Semgrep', status: true },
                    { name: 'Bandit', status: true },
                    { name: 'Gitleaks', status: true },
                    { name: 'npm audit', status: true },
                    { name: 'pip-audit', status: false },
                    { name: 'ESLint', status: true },
                  ].map(tool => (
                    <div key={tool.name} className={`rounded-lg p-md border flex items-center gap-sm ${tool.status ? 'border-secondary/20 bg-secondary/5' : 'border-outline-variant opacity-50'}`}>
                      <span className={`w-2 h-2 rounded-full ${tool.status ? 'bg-secondary' : 'bg-outline'}`} />
                      <span className="text-sm font-bold text-on-background">{tool.name}</span>
                      <span className={`ml-auto text-[10px] font-label-caps ${tool.status ? 'text-secondary' : 'text-outline'}`}>
                        {tool.status ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Security */}
          {activeTab === 'security' && (
            <div className="glass-card rounded-xl p-xl space-y-lg">
              <h3 className="font-bold text-on-background border-b border-outline-variant pb-md">Account Security</h3>
              <div className="space-y-lg">
                <div className="flex items-center justify-between py-md border-b border-outline-variant/30">
                  <div>
                    <p className="font-bold text-on-background">Two-Factor Authentication</p>
                    <p className="text-sm text-on-surface-variant">Add an extra layer of security to your account.</p>
                  </div>
                  <button className="border border-primary text-primary px-md py-sm rounded-lg text-sm font-bold hover:bg-primary/10 transition-all">Enable 2FA</button>
                </div>
                <div className="flex items-center justify-between py-md border-b border-outline-variant/30">
                  <div>
                    <p className="font-bold text-on-background">Change Password</p>
                    <p className="text-sm text-on-surface-variant">Last changed 30 days ago.</p>
                  </div>
                  <button className="border border-outline-variant text-on-surface-variant px-md py-sm rounded-lg text-sm font-bold hover:bg-surface-container hover:text-on-surface transition-all">Change</button>
                </div>
                <div className="flex items-center justify-between py-md border-b border-outline-variant/30">
                  <div>
                    <p className="font-bold text-on-background">Active Sessions</p>
                    <p className="text-sm text-on-surface-variant">Manage where you're logged in.</p>
                  </div>
                  <button className="border border-outline-variant text-on-surface-variant px-md py-sm rounded-lg text-sm font-bold hover:bg-surface-container hover:text-on-surface transition-all">View Sessions</button>
                </div>
                <div className="flex items-center justify-between py-md">
                  <div>
                    <p className="font-bold text-error">Delete Account</p>
                    <p className="text-sm text-on-surface-variant">Permanently delete your account and all data.</p>
                  </div>
                  <button className="border border-error/50 text-error px-md py-sm rounded-lg text-sm font-bold hover:bg-error/10 transition-all">Delete</button>
                </div>
              </div>
            </div>
          )}

          {/* Team */}
          {activeTab === 'team' && (
            <div className="glass-card rounded-xl p-xl space-y-lg">
              <div className="flex justify-between items-center border-b border-outline-variant pb-md">
                <h3 className="font-bold text-on-background">Team Members</h3>
                <button className="flex items-center gap-xs bg-[#7B61FF] text-white px-md py-sm rounded-lg text-sm font-bold hover:bg-opacity-90 transition-all">
                  <span className="material-symbols-outlined text-[18px]">person_add</span> Invite Member
                </button>
              </div>
              <div className="space-y-sm">
                {[
                  { name: 'Alex Johnson', email: 'alex@company.io', role: 'Owner', avatar: 'A' },
                  { name: 'Sarah Chen', email: 'sarah@company.io', role: 'Admin', avatar: 'S' },
                  { name: 'Marcus Rivera', email: 'marcus@company.io', role: 'Viewer', avatar: 'M' },
                  { name: 'Priya Patel', email: 'priya@company.io', role: 'Viewer', avatar: 'P' },
                ].map(member => (
                  <div key={member.email} className="flex items-center justify-between py-md border-b border-outline-variant/20">
                    <div className="flex items-center gap-md">
                      <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center font-bold text-primary">
                        {member.avatar}
                      </div>
                      <div>
                        <p className="font-bold text-on-background text-sm">{member.name}</p>
                        <p className="text-on-surface-variant text-xs">{member.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-md">
                      <span className={`text-[10px] font-label-caps px-3 py-1 rounded-full border ${member.role === 'Owner' ? 'text-primary border-primary/30 bg-primary/10' : member.role === 'Admin' ? 'text-secondary border-secondary/30 bg-secondary/10' : 'text-outline border-outline-variant'}`}>
                        {member.role}
                      </span>
                      {member.role !== 'Owner' && (
                        <button className="text-outline hover:text-error transition-colors">
                          <span className="material-symbols-outlined text-[20px]">remove_circle_outline</span>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;
