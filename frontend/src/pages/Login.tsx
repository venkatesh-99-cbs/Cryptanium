import React, { useState, useEffect } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useSecurity } from '../context/SecurityContext';

const Login: React.FC = () => {
  const { login, isAuthenticated } = useSecurity();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [githubLoading, setGithubLoading] = useState(false);

  useEffect(() => {
    const container = document.body;
    const particleCount = 15;
    const particles: HTMLDivElement[] = [];

    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div');
      const size = Math.random() * 2 + 1;
      const x = Math.random() * 100;
      const y = Math.random() * 100;
      const duration = Math.random() * 20 + 10;
      const delay = Math.random() * 5;
      particle.className = 'fixed rounded-full pointer-events-none z-0';
      particle.style.width = `${size}px`;
      particle.style.height = `${size}px`;
      particle.style.left = `${x}%`;
      particle.style.top = `${y}%`;
      particle.style.filter = 'blur(1px)';
      particle.style.background = 'rgba(201, 191, 255, 0.2)';
      particle.animate([
        { transform: 'translateY(0) translateX(0)', opacity: 0 },
        { transform: `translateY(-${Math.random() * 100 + 50}px) translateX(${Math.random() * 40 - 20}px)`, opacity: 0.5 },
        { transform: `translateY(-${Math.random() * 200 + 100}px) translateX(${Math.random() * 80 - 40}px)`, opacity: 0 }
      ], { duration: duration * 1000, delay: delay * 1000, iterations: Infinity, easing: 'linear' });
      container.appendChild(particle);
      particles.push(particle);
    }
    return () => particles.forEach(p => p.remove());
  }, []);

  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  const handleGitHub = async () => {
    setGithubLoading(true);
    window.location.href = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/auth/login`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // OAuth is the supported login flow; the submit action opens it too.
    window.location.href = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/auth/login`;
    setIsLoading(false);
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#0b0e14] text-on-background font-body-md flex items-center justify-center relative overflow-hidden">
      {/* Atmospheric Background */}
      <div className="bg-gradient-noise absolute inset-0 pointer-events-none" />
      <div className="absolute top-[-10%] right-[-5%] w-[400px] h-[400px] bg-primary/5 rounded-full blur-[100px] animate-pulse-slow pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[-5%] w-[400px] h-[400px] bg-secondary/5 rounded-full blur-[100px] animate-pulse-slow pointer-events-none" />

      {/* Main Login Container */}
      <main className="relative z-10 w-full max-w-[440px] px-margin-mobile md:px-0">
        {/* Branding Header */}
        <div className="text-center mb-xl">
          <img src="/cyyptanium.jpeg" alt="Cryptanium" className="inline-block w-24 h-24 rounded-xl object-cover border border-outline-variant mb-md shadow-lg" />
          <h1 className="text-headline-md font-headline-md tracking-tight text-on-background font-bold">CRYPTANIUM</h1>
          <p className="font-label-caps text-label-caps text-primary mt-sm uppercase tracking-widest">Security Suite</p>
        </div>

        {/* Login Card */}
        <div className="glass-card rounded-xl p-xl">
          <div className="mb-lg">
            <h2 className="text-headline-md font-headline-md text-on-background font-semibold">Welcome Back</h2>
            <p className="font-body-md text-body-md text-on-surface-variant mt-xs">Sign in to continue to your dashboard</p>
          </div>

          {/* OAuth Section */}
          <button
            onClick={handleGitHub}
            disabled={githubLoading}
            className="w-full flex items-center justify-center gap-md py-md bg-surface-container-highest border border-outline-variant rounded-lg font-body-md text-on-background hover:bg-surface-bright transition-all duration-200 active:scale-[0.98] disabled:opacity-60"
          >
            {githubLoading ? (
              <span className="material-symbols-outlined animate-spin">refresh</span>
            ) : (
              <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.43.372.823 1.102.823 2.222 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
              </svg>
            )}
            {githubLoading ? 'Authenticating...' : 'Sign in with GitHub'}
          </button>

          <div className="relative flex items-center py-lg">
            <div className="flex-grow border-t border-outline-variant" />
            <span className="flex-shrink mx-4 font-label-caps text-label-caps text-outline">or</span>
            <div className="flex-grow border-t border-outline-variant" />
          </div>

          {/* Credentials Form */}
          <form onSubmit={handleSubmit} className="space-y-lg">
            <div className="space-y-xs">
              <label className="font-label-caps text-label-caps text-on-surface-variant block uppercase" htmlFor="email">Email address</label>
              <div className="relative flex items-center group/input">
                <span className="material-symbols-outlined absolute left-md text-outline group-focus-within/input:text-primary transition-colors text-[20px]">alternate_email</span>
                <input
                  className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg pl-xl py-md text-body-md text-on-background placeholder:text-outline-variant focus:ring-0 focus:outline-none focus:border-primary transition-all duration-300 neon-glow"
                  id="email"
                  placeholder="you@example.com"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-xs">
              <div className="flex justify-between items-center">
                <label className="font-label-caps text-label-caps text-on-surface-variant block uppercase" htmlFor="password">Password</label>
                <a className="font-label-caps text-label-caps text-primary hover:underline" href="#">Forgot password?</a>
              </div>
              <div className="relative flex items-center group/input">
                <span className="material-symbols-outlined absolute left-md text-outline group-focus-within/input:text-primary transition-colors text-[20px]">lock</span>
                <input
                  className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg pl-xl pr-xl py-md text-body-md text-on-background placeholder:text-outline-variant focus:ring-0 focus:outline-none focus:border-primary transition-all duration-300 neon-glow"
                  id="password"
                  placeholder="••••••••"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-md text-outline hover:text-on-surface-variant transition-colors">
                  <span className="material-symbols-outlined text-[20px]">{showPassword ? 'visibility_off' : 'visibility'}</span>
                </button>
              </div>
            </div>

            <div className="flex items-center gap-md">
              <input
                className="w-4 h-4 rounded-sm bg-surface-container-lowest border-outline-variant text-primary focus:ring-primary/20"
                id="remember"
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
              />
              <label className="font-body-md text-body-md text-on-surface-variant select-none" htmlFor="remember">Remember me</label>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-md bg-[#5d3fe0] hover:bg-[#7B61FF] text-white font-bold rounded-lg shadow-[0_0_20px_rgba(123,97,255,0.3)] hover:shadow-[0_0_25px_rgba(123,97,255,0.5)] transition-all duration-300 active:scale-[0.97] flex items-center justify-center gap-sm disabled:opacity-60"
            >
              {isLoading ? <span className="material-symbols-outlined animate-spin">refresh</span> : null}
              {isLoading ? 'Signing in...' : 'Login'}
            </button>
          </form>

          <div className="mt-xl text-center">
            <p className="font-body-md text-body-md text-on-surface-variant">
              Don't have an account?{' '}
              <a className="text-primary font-bold hover:underline" href="#">Sign up</a>
            </p>
          </div>
        </div>

        {/* Footer Security Badge */}
        <div className="mt-xl flex items-center justify-center gap-md opacity-40 grayscale hover:grayscale-0 hover:opacity-100 transition-all duration-500">
          <span className="material-symbols-outlined text-on-surface-variant text-[20px]">verified_user</span>
          <span className="font-label-caps text-label-caps text-on-surface-variant">ISO 27001 Certified &amp; SOC2 Compliant</span>
        </div>
      </main>
    </div>
  );
};

export default Login;
