import React, { useState, useEffect, useRef } from 'react';
import { Activity, Zap, Cpu, Search, Database } from 'lucide-react';
import { useStore } from '../store/useStore';

const NerveCenter: React.FC = () => {
  const { telemetry, setTelemetry, updateRemoteUser, removeRemoteUser } = useStore();
  const [latencyHistory, setLatencyHistory] = useState<number[]>([]);
  const [connected, setConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const userId = useRef(`user_${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    // Connect with unique ID
    ws.current = new WebSocket(`ws://localhost:8000/ws/nerve-center?user_id=${userId.current}`);
    
    ws.current.onopen = () => setConnected(true);
    ws.current.onclose = () => setConnected(false);
    
    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      switch (message.type) {
        case 'SYSTEM_TELEMETRY':
            setTelemetry(message.data);
            setLatencyHistory(prev => [...prev, message.data.performance.avg_ms].slice(-20));
            break;
        case 'USER_JOINED':
            console.log(`Presence: User ${message.user_id} joined the metaverse.`);
            break;
        case 'PRESENCE_UPDATE':
            if (message.user_id !== userId.current) {
                updateRemoteUser(message.user_id, message.state);
            }
            break;
        case 'USER_LEFT':
            removeRemoteUser(message.user_id);
            break;
      }
    };

    return () => ws.current?.close();
  }, [setTelemetry, updateRemoteUser, removeRemoteUser]);

  // Periodic Presence Sync
  useEffect(() => {
      const syncInterval = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
              ws.current.send(JSON.stringify({
                  type: 'PRESENCE_SYNC',
                  state: {
                      pos: [0, 0, 0], // In a real app, track camera position
                      rot: [0, 0, 0, 1]
                  }
              }));
          }
      }, 500); // 2FPS presence sync
      return () => clearInterval(syncInterval);
  }, []);

  if (!connected || !telemetry) {
    return (
      <div className="bg-slate-950/50 backdrop-blur-3xl border border-white/5 rounded-[2.5rem] p-8 flex items-center justify-center min-h-[300px]">
        <div className="text-center space-y-4">
            <Zap className="w-12 h-12 text-slate-700 mx-auto animate-pulse" />
            <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-600">Connecting to Nerve Center...</p>
        </div>
      </div>
    );
  }

  const { performance, pillars } = telemetry;
  const onlineCount = Object.values(pillars).filter((p: any) => p.status === 'online').length;
  const totalCount = Object.keys(pillars).length;

  return (
    <div className="bg-slate-950/80 backdrop-blur-3xl border border-white/10 rounded-[3rem] p-10 shadow-2xl relative overflow-hidden group">
      
      {/* Background HUD Grid */}
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:20px_20px]" />

      <div className="flex items-center justify-between mb-10 relative z-10">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 rounded-2xl border border-emerald-500/20 text-emerald-400">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h3 className="font-black text-white uppercase tracking-[0.2em] text-sm">System Nerve Center</h3>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-1">Real-time AI Telemetry</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/5 rounded-full border border-emerald-500/10">
            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-[9px] font-mono text-emerald-400">SYNC_ACTIVE</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10 relative z-10">
        {/* Latency Monitor */}
        <div className="bg-black/40 rounded-[2rem] p-6 border border-white/5">
            <div className="flex items-center justify-between mb-6">
                <span className="text-[9px] font-black uppercase text-slate-500 tracking-widest">Network Latency</span>
                <span className={`text-[10px] font-mono font-bold ${performance.load === 'nominal' ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {performance.avg_ms} MS
                </span>
            </div>
            <div className="flex items-end gap-1 h-16">
                {latencyHistory.map((lat, i) => (
                    <div 
                        key={i} 
                        className="flex-1 bg-primary-500/40 rounded-t-sm transition-all duration-500" 
                        style={{ height: `${Math.min(lat / 10, 100)}%` }} 
                    />
                ))}
            </div>
        </div>

        {/* Load Monitor */}
        <div className="bg-black/40 rounded-[2rem] p-6 border border-white/5 flex flex-col justify-center">
            <div className="flex items-center justify-between mb-2">
                <span className="text-[9px] font-black uppercase text-slate-500 tracking-widest">Compute Load</span>
                <span className="text-[10px] font-mono text-primary-400 font-bold uppercase">{performance.load}</span>
            </div>
            <div className="text-3xl font-black text-white tracking-tighter">
                {performance.p95_ms} <span className="text-xs text-slate-600 font-bold uppercase tracking-widest">P95 ms</span>
            </div>
        </div>
      </div>

      {/* Pillar Health Grid */}
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
            <span className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Pillar Integrity ({onlineCount}/{totalCount})</span>
        </div>
        <div className="grid grid-cols-6 sm:grid-cols-10 gap-2">
            {Object.entries(pillars).map(([name, stat]: [string, any]) => (
                <div 
                    key={name}
                    className={`aspect-square rounded-lg border transition-all duration-500 flex items-center justify-center group/p`}
                    title={`${name.toUpperCase()}: ${stat.health}`}
                >
                    <div className={`w-2 h-2 rounded-full ${stat.health === 'ok' ? 'bg-emerald-500' : 'bg-red-500'} ${stat.status === 'online' ? 'shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'opacity-20'}`} />
                </div>
            ))}
        </div>
      </div>

      <div className="mt-10 pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4 relative z-10">
          <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                  <Cpu className="w-3.5 h-3.5 text-slate-600" />
                  <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">MoE Enabled</span>
              </div>
              <div className="flex items-center gap-2">
                  <Database className="w-3.5 h-3.5 text-slate-600" />
                  <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">RAG Grounded</span>
              </div>
          </div>
          <button className="text-[9px] font-black text-primary-400 hover:text-white uppercase tracking-widest transition-colors">
              Export Audit Log
          </button>
      </div>

    </div>
  );
};

export default NerveCenter;
