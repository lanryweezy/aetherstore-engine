import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { TrendingUp, Activity } from 'lucide-react';

const TrendInsights: React.FC = () => {
  const [trends, setTrends] = useState<[string, number][]>([]);
  const [ratio, setRatio] = useState(1.0);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/intelligence/trend-momentum');
        setTrends(response.data.trending);
        setRatio(response.data.target_shift_ratio);
      } catch (error) {
        console.error('Failed to fetch trends:', error);
      }
    };

    fetchTrends();
    const interval = setInterval(fetchTrends, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-950/50 backdrop-blur-3xl border border-white/5 rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden group">
      <div className="absolute -top-10 -right-10 w-24 h-24 bg-rose-600/5 blur-3xl" />
      
      <div className="flex items-center gap-3 mb-8">
        <div className="p-2.5 bg-rose-500/10 rounded-xl border border-rose-500/20 text-rose-400">
          <TrendingUp className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-black text-white uppercase tracking-[0.2em] text-[10px]">Market Momentum</h3>
          <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">SHIFT15M Live Feed</p>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        {trends.length > 0 ? trends.map(([cat, momentum]) => (
          <div key={cat} className="p-5 bg-white/5 rounded-3xl border border-white/5 hover:border-rose-500/30 transition-all group/item">
            <div className="text-[9px] text-slate-500 uppercase font-black mb-2 tracking-tighter group-hover/item:text-slate-300 transition-colors">{cat}</div>
            <div className="text-xl font-black text-emerald-400 flex items-center gap-1">
              <span className="text-sm">↑</span>
              {(momentum * 100).toFixed(1)}%
            </div>
          </div>
        )) : (
          <div className="col-span-2 py-8 text-center text-[10px] text-slate-600 font-bold uppercase tracking-widest animate-pulse">
            Synchronizing with fashion grid...
          </div>
        )}
      </div>

      <div className="mt-8 pt-8 border-t border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-2.5 text-slate-500 text-[10px] font-black uppercase tracking-widest">
          <Activity className="w-3.5 h-3.5 text-primary-400" /> Target Shift
        </div>
        <div className="text-2xl font-mono font-black text-primary-400 tracking-tighter">
          {ratio.toFixed(2)}
        </div>
      </div>
    </div>
  );
};

export default TrendInsights;
