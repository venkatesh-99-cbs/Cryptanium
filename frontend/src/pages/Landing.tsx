import React, { useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Landing: React.FC = () => {
  const navigate = useNavigate();
  const heroGradientRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = e.clientX / window.innerWidth;
      const y = e.clientY / window.innerHeight;
      if (heroGradientRef.current) {
        heroGradientRef.current.style.background = `radial-gradient(circle at ${x * 100}% ${y * 100}%, rgba(123, 97, 255, 0.12) 0%, transparent 70%)`;
      }
    };
    document.addEventListener('mousemove', handleMouseMove);
    return () => document.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const tools = [
    { name: 'Semgrep', icon: 'shield', color: 'text-primary' },
    { name: 'Bandit', icon: 'policy', color: 'text-secondary' },
    { name: 'Gitleaks', icon: 'key', color: 'text-tertiary' },
    { name: 'npm audit', icon: 'inventory_2', color: 'text-error' },
    { name: 'pip-audit', icon: 'package_2', color: 'text-primary' },
    { name: 'ESLint', icon: 'code', color: 'text-on-surface-variant' },
  ];

  return (
    <div className="min-h-screen bg-[#0b0e14] text-on-background font-body-md">
      {/* Header Navigation */}
      <header className="fixed top-0 right-0 w-full z-50 bg-background/80 backdrop-blur-xl border-b border-outline-variant px-margin-desktop h-16 flex justify-between items-center">
        <div className="flex items-center gap-sm">
          <div className="w-8 h-8 bg-primary-container/20 rounded flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>security</span>
          </div>
          <img src="/cyyptanium.jpeg" alt="Cryptanium" className="w-10 h-10 rounded object-cover" />
          <span className="text-headline-md font-headline-md font-bold tracking-tight text-on-background">CRYPTANIUM</span>
        </div>
        <nav className="hidden md:flex items-center gap-xl">
          <a href="#features" className="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-all">Features</a>
          <a href="#how-it-works" className="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-all">How It Works</a>
          <a href="#tools" className="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-all">Integrations</a>
          <a href="#faq" className="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-all">FAQ</a>
        </nav>
        <div className="flex items-center gap-md">
          <Link to="/login" className="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-all">Login</Link>
          <Link to="/login" className="bg-[#7B61FF] text-white px-md py-sm rounded-lg font-body-md text-body-md hover:bg-opacity-90 transition-all shadow-[0_0_15px_rgba(123,97,255,0.3)]">
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative pt-32 pb-16 overflow-hidden">
        {/* Atmospheric Background */}
        <div ref={heroGradientRef} className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[600px] hero-gradient pointer-events-none -z-10" />
        <div className="absolute top-20 right-[10%] w-[300px] h-[300px] bg-primary/5 rounded-full blur-[100px] pointer-events-none -z-10 animate-pulse-slow" />
        <div className="absolute bottom-0 left-[5%] w-[400px] h-[400px] bg-secondary/5 rounded-full blur-[120px] pointer-events-none -z-10 animate-pulse-slow" />

        <div className="max-w-4xl mx-auto text-center px-margin-mobile">
          {/* AI Badge */}
          <div className="inline-flex items-center gap-xs px-sm py-1 rounded-full bg-primary/10 border border-primary/20 text-primary mb-xl">
            <span className="material-symbols-outlined text-[16px]" style={{ fontVariationSettings: "'FILL' 1" }}>auto_awesome</span>
            <span className="font-label-caps text-label-caps">AI-Powered Repository Security</span>
          </div>

          <h1 className="text-[clamp(36px,5vw,56px)] font-bold text-on-background mb-md leading-tight tracking-tight" style={{ letterSpacing: '-0.02em' }}>
            Secure Every Commit. <br />
            <span className="text-primary">Trust Every Deployment.</span>
          </h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl mx-auto mb-xl opacity-80">
            Cryptanium scans your repositories using industry-leading security tools and AI to deliver a unified trust score and actionable insights. Detect vulnerabilities, secrets, and risky dependencies before they reach production.
          </p>
          <div className="flex flex-col sm:flex-row gap-md justify-center items-center mb-32">
            <button
              onClick={() => navigate('/login')}
              className="w-full sm:w-auto bg-[#7B61FF] text-white px-xl py-md rounded-xl font-bold text-lg hover:bg-opacity-90 transition-all flex items-center justify-center gap-sm shadow-[0_0_20px_rgba(123,97,255,0.4)]"
            >
              Get Started <span className="material-symbols-outlined">arrow_forward</span>
            </button>
            <a href="#features" className="w-full sm:w-auto glass-card border border-outline-variant px-xl py-md rounded-xl font-bold text-lg text-on-background hover:bg-surface-container-high transition-all text-center">
              Learn More
            </a>
          </div>
        </div>

        {/* Supported Tools Grid */}
        <section id="tools" className="max-w-7xl mx-auto px-margin-desktop pb-24">
          <div className="text-center mb-xl">
            <h2 className="font-label-caps text-label-caps text-on-surface-variant/60 tracking-[0.2em] uppercase">Built-in integrations for modern pipelines</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-gutter">
            {tools.map((tool) => (
              <div key={tool.name} className="glass-card p-md rounded-xl flex flex-col items-center gap-sm neon-glow transition-all group cursor-pointer">
                <div className={`w-12 h-12 flex items-center justify-center ${tool.color} group-hover:scale-110 transition-transform`}>
                  <span className="material-symbols-outlined text-[32px]">{tool.icon}</span>
                </div>
                <span className="font-label-caps text-label-caps text-on-surface">{tool.name}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="max-w-7xl mx-auto px-margin-desktop pb-24">
          <div className="text-center mb-xl">
            <div className="inline-flex items-center gap-xs px-sm py-1 rounded-full bg-secondary/10 border border-secondary/20 text-secondary mb-md">
              <span className="material-symbols-outlined text-[14px]">verified</span>
              <span className="font-label-caps text-label-caps">Platform Capabilities</span>
            </div>
            <h2 className="text-headline-lg font-headline-lg text-on-background mb-md">Everything you need to stay secure</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">
            {[
              { icon: 'manage_search', color: 'text-primary', title: 'Deep SAST Analysis', desc: 'Multi-language static analysis using Semgrep and Bandit to find logic flaws, XSS, SQLi, and more.' },
              { icon: 'key_off', color: 'text-error', title: 'Secrets Detection', desc: 'Gitleaks scans entire git history to find exposed API keys, tokens, and connection strings before attackers do.' },
              { icon: 'inventory_2', color: 'text-tertiary', title: 'Dependency Audit', desc: 'npm audit and pip-audit cross-reference your dependencies against known CVE databases in real-time.' },
              { icon: 'smart_toy', color: 'text-secondary', title: 'AI-Powered Insights', desc: 'Our AI assistant contextualizes findings and generates working code patches with detailed remediation plans.' },
              { icon: 'analytics', color: 'text-primary', title: 'Trust Score & Reports', desc: 'Unified security health scoring across all repositories with exportable PDF, JSON, and CSV reports.' },
              { icon: 'notifications_active', color: 'text-tertiary', title: 'Real-time Alerts', desc: 'Instant notifications for critical findings with actionable guidance on remediation paths.' }
            ].map((feat) => (
              <div key={feat.title} className="glass-card p-lg rounded-xl neon-glow transition-all hover:translate-y-[-2px]">
                <div className={`w-10 h-10 flex items-center justify-center ${feat.color} mb-md`}>
                  <span className="material-symbols-outlined text-[32px]">{feat.icon}</span>
                </div>
                <h3 className="font-bold text-on-background text-lg mb-sm">{feat.title}</h3>
                <p className="text-on-surface-variant text-body-md leading-relaxed">{feat.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Visual Element / Dashboard Preview */}
        <section className="max-w-5xl mx-auto px-margin-desktop mb-24">
          <div className="glass-card rounded-[2rem] p-sm overflow-hidden relative group cursor-pointer">
            <div className="absolute inset-0 bg-primary/5 group-hover:bg-primary/10 transition-colors duration-500" />
            <div className="relative rounded-[1.5rem] overflow-hidden border border-outline-variant/30 bg-surface-container-low aspect-[16/9] flex items-center justify-center">
              <div className="absolute inset-0 grid grid-cols-12 gap-2 p-8 opacity-40">
                {Array.from({ length: 48 }).map((_, i) => (
                  <div key={i} className={`h-1 rounded-full ${i % 3 === 0 ? 'bg-primary/60' : i % 5 === 0 ? 'bg-secondary/60' : 'bg-surface-container-highest'}`} />
                ))}
              </div>
              <div className="relative z-10 text-center">
                <div className="text-7xl font-bold text-secondary mb-2">82</div>
                <div className="font-label-caps text-label-caps text-secondary/60">TRUST SCORE</div>
              </div>
              <div className="absolute top-md right-md flex gap-xs">
                <div className="w-2 h-2 rounded-full bg-error animate-pulse" />
                <div className="w-2 h-2 rounded-full bg-secondary" />
                <div className="w-2 h-2 rounded-full bg-primary" />
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="max-w-3xl mx-auto px-margin-desktop text-center pb-24">
          <div className="glass-card rounded-2xl p-xl border border-primary/10 bg-primary/5">
            <h2 className="text-headline-lg font-headline-lg text-on-background mb-md">Ready to Secure Your Repositories?</h2>
            <p className="text-on-surface-variant mb-xl">Join thousands of engineering teams who trust Cryptanium to protect their codebase from critical vulnerabilities.</p>
            <button
              onClick={() => navigate('/login')}
              className="bg-[#7B61FF] text-white px-xl py-md rounded-xl font-bold hover:bg-opacity-90 transition-all shadow-[0_0_20px_rgba(123,97,255,0.4)] inline-flex items-center gap-sm"
            >
              Start Scanning Free <span className="material-symbols-outlined">arrow_forward</span>
            </button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-surface-container-lowest border-t border-outline-variant w-full py-xl">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center px-margin-desktop gap-lg">
          <div className="flex flex-col gap-xs items-center md:items-start">
            <div className="flex items-center gap-xs">
              <div className="w-6 h-6 bg-primary-container/20 rounded flex items-center justify-center">
                <span className="material-symbols-outlined text-primary text-[14px]" style={{ fontVariationSettings: "'FILL' 1" }}>security</span>
              </div>
              <span className="font-bold text-lg">CRYPTANIUM</span>
            </div>
            <p className="font-body-md text-body-md text-on-surface-variant">© 2024 Cryptanium Security. All rights reserved.</p>
          </div>
          <div className="flex flex-wrap justify-center gap-xl">
            <a href="#" className="font-body-md text-body-md text-on-surface-variant hover:text-primary transition-colors">Terms of Service</a>
            <a href="#" className="font-body-md text-body-md text-on-surface-variant hover:text-primary transition-colors">Privacy Policy</a>
            <a href="#" className="font-body-md text-body-md text-on-surface-variant hover:text-primary transition-colors">Contact Support</a>
            <a href="#" className="font-body-md text-body-md text-on-surface-variant hover:text-primary transition-colors">Documentation</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
