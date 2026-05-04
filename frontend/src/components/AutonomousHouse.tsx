import React, { useState } from 'react';
import axios from 'axios';
import { Hexagon, Database, Cpu, Rocket, Loader2, Sparkles, Network } from 'lucide-react';

const AutonomousHouse: React.FC = () => {
  const [step, setStep] = useState<'idle' | 'analyzing' | 'generating' | 'ready'>('idle');
  const [result, setResult] = useState<any>(null);

  const triggerAutonomousCycle = () => {
    setStep('analyzing');
    
    // Simulate analyzing global market data
    setTimeout(() => {
      setStep('generating');
      executeAIHouse();
    }, 2500);
  };

  const executeAIHouse = async () => {
    try {
      const market_data = { global_sentiment: "bullish", dominant_trend: "cyber-punk" };
      const response = await axios.post('http://localhost:8000/api/ai/trigger-autonomous-house', market_data);
      setResult(response.data);
      setStep('ready');

      // Trigger a global UI refresh to show new products
      window.dispatchEvent(new CustomEvent('aetherstore:new-drop', { detail: response.data.collection }));
    } catch (error) {
      console.error("Autonomous cycle failed:", error);
      setStep('idle');
    }
  };

  return (
    <div className="bg-slate-950/80 backdrop-blur-3xl border border-white/10 rounded-[3rem] p-10 shadow-[0_0_100px_rgba(0,0,0,0.8)] relative overflow-hidden group">
      
      {/* Background Neon Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-fuchsia-600/10 blur-[120px] pointer-events-none" />
      
      <div className="flex flex-col md:flex-row items-start justify-between gap-8 mb-12 relative z-10">
        <div>
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-fuchsia-500/20 rounded-2xl border border-fuchsia-500/30 text-fuchsia-400 shadow-[0_0_30px_rgba(217,70,239,0.3)]">
              <Hexagon className="w-8 h-8" />
            </div>
            <div>
              <h3 className="font-black text-white uppercase tracking-[0.2em] text-xl">Autonomous Label</h3>
              <p className="text-[10px] text-fuchsia-400 font-bold uppercase tracking-widest mt-1 flex items-center gap-2">
                <span className="w-2 h-2 bg-fuchsia-500 rounded-full animate-pulse" />
                Zero-Human Intervention Cycle
              </p>
            </div>
          </div>
          <p className="text-slate-400 text-sm max-w-md leading-relaxed font-medium">
            Deploy a self-sustaining AI entity that analyzes market trends, establishes a brand identity, designs a 3D collection, and mints smart contracts autonomously.
          </p>
        </div>

        {step === 'idle' && (
          <button 
            onClick={triggerAutonomousCycle}
            className="group relative overflow-hidden shrink-0 px-8 py-5 bg-white text-slate-950 rounded-2xl font-black text-xs uppercase tracking-widest transition-all shadow-2xl hover:shadow-fuchsia-900/40 hover:scale-105 active:scale-95 flex items-center gap-3"
          >
            <div className="absolute inset-0 bg-fuchsia-400/20 translate-y-full group-hover:translate-y-0 transition-transform duration-500" />
            <Rocket className="w-5 h-5 relative z-10" />
            <span className="relative z-10">Deploy Agent</span>
          </button>
        )}
      </div>

      <div className="relative z-10 bg-black/40 rounded-[2rem] border border-white/5 p-8 min-h-[300px] flex flex-col items-center justify-center">
        
        {step === 'idle' && (
           <div className="text-center opacity-50">
               <Network className="w-16 h-16 mx-auto mb-4 text-slate-600" />
               <p className="text-xs font-black uppercase tracking-widest text-slate-500">Agent in stasis...</p>
           </div>
        )}

        {step === 'analyzing' && (
          <div className="text-center space-y-6 animate-in zoom-in-95 duration-500">
             <Database className="w-16 h-16 mx-auto text-fuchsia-400 animate-pulse" />
             <div>
                <h4 className="text-sm font-black text-white uppercase tracking-[0.2em]">Extracting Trend DNA</h4>
                <p className="text-[10px] text-slate-400 font-bold uppercase mt-2 italic">Closing the sentient feedback loop...</p>
             </div>
          </div>
        )}

        {step === 'generating' && (
          <div className="text-center space-y-6 animate-in fade-in duration-500">
             <Cpu className="w-16 h-16 mx-auto text-indigo-400 animate-spin" />
             <div>
                <h4 className="text-sm font-black text-white uppercase tracking-[0.2em]">Synthesizing Brand & Collection</h4>
                <p className="text-[10px] text-slate-400 font-bold uppercase mt-2 max-w-[250px] mx-auto text-center">
                  Llama 4 and ShapeR are autonomously generating 3D assets optimized via user spatial analytics.
                </p>
             </div>
          </div>
        )}

        {step === 'ready' && result && (
          <div className="w-full animate-in slide-in-from-bottom-4 duration-700">
             <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2 text-fuchsia-400">
                    <Sparkles className="w-5 h-5" />
                    <span className="font-black text-xs uppercase tracking-widest">Brand Optimized via DNA</span>
                </div>
                <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/5">
                    <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest">Logic: {result.dna_stats?.design_logic_v3}</span>
                </div>
             </div>

             <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                 <div className="bg-white/5 p-5 rounded-3xl border border-white/5">
                    <p className="text-[8px] uppercase tracking-[0.2em] text-slate-500 font-black mb-2">Entity Name</p>
                    <p className="text-2xl font-black text-white tracking-tighter">{result.brand_identity.name}</p>
                    <p className="text-xs text-fuchsia-400 font-bold mt-1">{result.brand_identity.theme}</p>
                 </div>
                 <div className="bg-white/5 p-5 rounded-3xl border border-white/5 flex flex-col justify-center">
                    <p className="text-[8px] uppercase tracking-[0.2em] text-slate-500 font-black mb-2">Target Focus</p>
                    <p className="text-sm font-black text-emerald-400 uppercase tracking-widest">{result.dna_stats?.dominant_category}</p>
                    <p className="text-[9px] text-slate-400 font-bold uppercase mt-2">P95 Engagement Sync</p>
                 </div>
             </div>

             <div className="bg-white/5 p-6 rounded-3xl border border-white/5 mb-6">
                 <p className="text-[8px] uppercase tracking-[0.2em] text-slate-500 font-black mb-3">Generated Collection ({result.collection.length} Items)</p>
                 <div className="space-y-2">
                     {result.collection.map((item: any, i: number) => (
                         <div key={i} className="flex justify-between items-center p-3 bg-black/20 rounded-xl">
                             <span className="text-sm font-bold text-white">{item.name}</span>
                             <span className="text-[10px] font-mono text-fuchsia-400">{item.base_price_eth} ETH</span>
                         </div>
                     ))}
                 </div>
             </div>

             <div className="p-5 border-l-2 border-fuchsia-500 bg-fuchsia-500/5 mb-6">
                 <p className="text-sm text-slate-300 font-medium italic">"{result.brand_identity.manifesto}"</p>
             </div>

             <button 
                onClick={() => setStep('idle')}
                className="w-full py-4 bg-transparent border border-white/10 text-slate-400 hover:text-white hover:bg-white/5 rounded-2xl font-black text-xs uppercase tracking-widest transition-all active:scale-95"
             >
                Terminate & Redeploy Agent
             </button>
          </div>
        )}

      </div>
    </div>
  );
};

export default AutonomousHouse;
