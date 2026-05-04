import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

const LoadingState: React.FC<LoadingStateProps> = ({ message = "Synchronizing AI Pillars..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-20 w-full min-h-[300px] animate-in fade-in duration-700">
      <div className="relative mb-6">
        <div className="absolute inset-0 bg-primary-500 blur-2xl opacity-20 animate-pulse" />
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin relative z-10" />
      </div>
      <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500 animate-pulse">
        {message}
      </p>
    </div>
  );
};

export default LoadingState;
