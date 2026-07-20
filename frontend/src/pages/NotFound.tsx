import React from 'react';
import { useNavigate } from 'react-router-dom';

const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#0b0e14] text-on-background flex items-center justify-center">
      <div className="text-center">
        <div className="relative mb-xl inline-block">
          <div className="text-[120px] font-bold text-primary/20 leading-none select-none" aria-hidden="true">404</div>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="material-symbols-outlined text-[60px] text-primary">search_off</span>
          </div>
        </div>
        <h1 className="text-headline-lg font-headline-lg font-bold text-on-background mb-md">Page Not Found</h1>
        <p className="text-on-surface-variant text-body-lg mb-xl max-w-md mx-auto">
          The page you're looking for doesn't exist or has been moved. Head back to the dashboard to continue.
        </p>
        <div className="flex items-center justify-center gap-md">
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-[#7B61FF] text-white px-xl py-md rounded-xl font-bold hover:bg-opacity-90 transition-all shadow-[0_0_20px_rgba(123,97,255,0.4)] flex items-center gap-sm"
          >
            <span className="material-symbols-outlined">home</span>
            Go to Dashboard
          </button>
          <button
            onClick={() => navigate(-1)}
            className="border border-outline-variant text-on-surface-variant px-xl py-md rounded-xl font-bold hover:bg-surface-container transition-all"
          >
            Go Back
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
