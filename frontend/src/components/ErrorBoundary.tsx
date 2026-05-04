import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children?: ReactNode;
  fallbackName?: string;
}

interface State {
  hasError: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error in AetherStore Component:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 bg-red-900/10 border border-red-500/20 rounded-[2rem] flex flex-col items-center justify-center text-center space-y-4 min-h-[200px]">
          <div className="p-3 bg-red-500/20 rounded-2xl text-red-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-white font-black uppercase tracking-widest text-xs">Pillar Connection Lost</h3>
            <p className="text-slate-500 text-[10px] mt-1 uppercase font-bold">
              The {this.props.fallbackName || 'AI Module'} encountered a neural sync error.
            </p>
          </div>
          <button 
            onClick={() => this.setState({ hasError: false })}
            className="flex items-center gap-2 text-xs font-black text-white hover:text-red-400 transition-colors uppercase tracking-tighter"
          >
            <RefreshCw className="w-3 h-3" /> Re-initialize Sync
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
