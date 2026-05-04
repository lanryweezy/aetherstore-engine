import React from 'react';
import { ShoppingBag, User, Box } from 'lucide-react';

import { useStore } from '../store/useStore';

const Header: React.FC = () => {
  const { telemetry } = useStore();
  
  const pillars = telemetry?.pillars || {};
  const online = Object.values(pillars).filter((s: any) => s.status === 'online').length;
  const total = Object.keys(pillars).length;
  const avgLat = telemetry?.performance?.avg_ms || 0;

  return (
    <header className="bg-slate-950/70 backdrop-blur-xl text-white sticky top-0 z-50 border-b border-white/5">
      <nav className="container mx-auto px-6 py-5 flex justify-between items-center">
        <div className="flex items-center gap-3 group cursor-pointer">
          <div className="relative">
            <div className="absolute inset-0 bg-primary-500 blur-lg opacity-20 group-hover:opacity-40 transition-opacity" />
            <Box className="text-primary-500 w-9 h-9 relative z-10" />
          </div>
          <h1 className="text-2xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            AETHERSTORE
          </h1>
        </div>
        
        <ul className="hidden lg:flex items-center space-x-10 text-[10px] uppercase font-black tracking-[0.2em] text-slate-400">
          <li><a href="#" className="hover:text-white transition-colors">Digital Home</a></li>
          <li><a href="#" className="hover:text-white transition-colors">Collection</a></li>
          <li><a href="#" className="hover:text-white transition-colors">Lab</a></li>
          <li><a href="/static/super_intelligence_demo.html" className="text-primary-400 hover:text-primary-300 transition-colors">Super-AI</a></li>
        </ul>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 text-[10px] font-mono text-slate-500 bg-white/5 px-3 py-1.5 rounded-full border border-white/5">
             <span className={`w-1.5 h-1.5 rounded-full animate-pulse ${online > 0 ? 'bg-emerald-500' : 'bg-amber-500'}`} />
             {online}/{total} PILLARS • {avgLat}MS
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2.5 bg-white/5 hover:bg-white/10 rounded-xl border border-white/5 transition-all">
                <User className="w-4 h-4 text-slate-300" />
            </button>
            <button className="p-2.5 bg-white/5 hover:bg-white/10 rounded-xl border border-white/5 transition-all relative">
                <ShoppingBag className="w-4 h-4 text-slate-300" />
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-primary-500 rounded-full" />
            </button>
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;
