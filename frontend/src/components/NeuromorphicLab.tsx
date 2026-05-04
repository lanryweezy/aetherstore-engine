import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Brain, Cpu, Waves, Download, Loader2, Sparkles, Clock } from 'lucide-react';

const NeuromorphicLab: React.FC = () => {
  const [step, setStep] = useState<'idle' | 'scanning' | 'generating' | 'ready'>('idle');
  const [manifest, setManifest] = useState<any>(null);
  const [taskId, setTaskId] = useState<string | null>(null);

  const startBrainwaveScan = () => {
    setStep('scanning');
    
    // Simulate reading EEG telemetry (e.g., from a connected neuro-headset)
    setTimeout(() => {
      setStep('generating');
      dispatchNeuromorphicTask();
    }, 3000);
  };

  const dispatchNeuromorphicTask = async () => {
    try {
      const eeg_data = {
          gamma_waves: Math.random() * 0.5 + 0.5,
          beta_waves: Math.random() * 0.5 + 0.3
      };
      
      const response = await axios.post('http://localhost:8000/api/ai/neuromorphic-fabrication?user_id=neuro_user_01', eeg_data);
      setTaskId(response.data.task_id);
    } catch (error) {
      console.error("Neuromorphic dispatch failed:", error);
      setStep('idle');
    }
  };

  // Poll for Task Completion
  useEffect(() => {
    let pollInterval: any;
    if (taskId && step === 'generating') {
        pollInterval = setInterval(async () => {
            try {
                const response = await axios.get(`http://localhost:8000/api/ai/task-status/${taskId}`);
                if (response.data.status === 'SUCCESS') {
                    setManifest(response.data.result);
                    setStep('ready');
                    setTaskId(null);
                    clearInterval(pollInterval);
                } else if (response.data.status === 'FAILURE') {
                    alert("Fabrication compilation failed on worker node.");
                    setStep('idle');
                    setTaskId(null);
                    clearInterval(pollInterval);
                }
            } catch (e) { console.error("Poll failed", e); }
        }, 3000);
    }
    return () => clearInterval(pollInterval);
  }, [taskId, step]);

  return (
    <div className="bg-slate-950/80 backdrop-blur-3xl border border-white/10 rounded-[3rem] p-10 shadow-[0_0_100px_rgba(0,0,0,0.8)] relative overflow-hidden group">
      
      {/* Background Neural Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-600/10 blur-[100px] pointer-events-none" />
      
      <div className="flex flex-col md:flex-row items-start justify-between gap-8 mb-12 relative z-10">
        <div>
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-purple-500/20 rounded-2xl border border-purple-500/30 text-purple-400 shadow-[0_0_30px_rgba(168,85,247,0.3)]">
              <Brain className="w-8 h-8" />
            </div>
            <div>
              <h3 className="font-black text-white uppercase tracking-[0.2em] text-xl">Neuromorphic Lab</h3>
              <p className="text-[10px] text-purple-400 font-bold uppercase tracking-widest mt-1 flex items-center gap-2">
                <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                Distributed Fabrication Pipeline
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-end gap-3">
            {step === 'idle' && (
            <button 
                onClick={startBrainwaveScan}
                className="group relative overflow-hidden shrink-0 px-8 py-5 bg-white text-slate-950 rounded-2xl font-black text-xs uppercase tracking-widest transition-all shadow-2xl hover:shadow-purple-900/40 hover:scale-105 active:scale-95 flex items-center gap-3"
            >
                <div className="absolute inset-0 bg-purple-400/20 translate-y-full group-hover:translate-y-0 transition-transform duration-500" />
                <Waves className="w-5 h-5 relative z-10" />
                <span className="relative z-10">Initiate Neural Link</span>
            </button>
            )}
            {taskId && (
                <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/5 animate-in fade-in zoom-in duration-500">
                    <Clock className="w-2.5 h-2.5 text-purple-400 animate-pulse" />
                    <span className="text-[8px] font-black text-slate-400 uppercase tracking-widest">Node Task: {taskId.slice(0,8)}</span>
                </div>
            )}
        </div>
      </div>

      <div className="relative z-10 bg-black/40 rounded-[2rem] border border-white/5 p-8 min-h-[300px] flex flex-col items-center justify-center">
        
        {step === 'idle' && (
           <div className="text-center opacity-50">
               <Brain className="w-16 h-16 mx-auto mb-4 text-slate-600" />
               <p className="text-xs font-black uppercase tracking-widest text-slate-500">Waiting for neuro-telemetry...</p>
           </div>
        )}

        {step === 'scanning' && (
          <div className="text-center space-y-6 animate-in zoom-in-95 duration-500">
             <div className="relative inline-flex items-center justify-center w-32 h-32">
                <div className="absolute inset-0 border-4 border-t-purple-500 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin" />
                <div className="absolute inset-2 border-4 border-b-indigo-500 border-r-transparent border-t-transparent border-l-transparent rounded-full animate-spin direction-reverse" />
                <Waves className="w-10 h-10 text-purple-400 animate-pulse" />
             </div>
             <div>
                <h4 className="text-sm font-black text-white uppercase tracking-[0.2em]">Reading Gamma Waves</h4>
                <p className="text-[10px] text-slate-400 font-bold uppercase mt-2">TRIBE v2 aesthetic evaluation in progress.</p>
             </div>
          </div>
        )}

        {step === 'generating' && (
          <div className="text-center space-y-6 animate-in fade-in duration-500">
             <Cpu className="w-16 h-16 mx-auto text-indigo-400 animate-bounce" />
             <div>
                <h4 className="text-sm font-black text-white uppercase tracking-[0.2em]">Compiling Machine Code</h4>
                <p className="text-[10px] text-slate-400 font-bold uppercase mt-2 max-w-[250px] mx-auto text-center">
                  Remote worker is converting neuro-topology into toolpaths.
                </p>
             </div>
          </div>
        )}

        {step === 'ready' && manifest && (
          <div className="w-full animate-in slide-in-from-bottom-4 duration-700">
             <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2 text-emerald-400">
                    <Sparkles className="w-5 h-5" />
                    <span className="font-black text-xs uppercase tracking-widest">Physical Manifest Ready</span>
                </div>
                <div className="text-[10px] font-mono text-slate-500 bg-white/5 px-3 py-1 rounded-full border border-white/5">
                    {manifest.manifest_id}
                </div>
             </div>

             <div className="bg-white/5 p-8 rounded-3xl border border-white/5 mb-8 flex flex-col items-center gap-4">
                 <div className="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center text-emerald-400 border border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.2)]">
                     <Cpu className="w-6 h-6" />
                 </div>
                 <p className="text-sm font-black text-white uppercase tracking-[0.2em]">Distributed Fabrication Complete</p>
                 <p className="text-[10px] text-slate-500 font-bold uppercase text-center max-w-xs">G-Code has been synthesized for Stoll CMS 530 3D-Knitting architecture.</p>
             </div>

             <div className="flex gap-4">
                 <button className="flex-1 py-4 bg-purple-600 hover:bg-purple-500 text-white rounded-2xl font-black text-xs uppercase tracking-widest transition-all shadow-[0_0_30px_rgba(168,85,247,0.3)] flex items-center justify-center gap-2 active:scale-95">
                    <Download className="w-4 h-4" />
                    Download G-Code (.gcode)
                 </button>
                 <button 
                    onClick={() => setStep('idle')}
                    className="px-6 py-4 bg-transparent border border-white/10 text-slate-400 hover:text-white hover:bg-white/5 rounded-2xl font-black text-xs uppercase tracking-widest transition-all active:scale-95"
                 >
                    Reset Link
                 </button>
             </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default NeuromorphicLab;
