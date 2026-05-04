import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Film, Play, Sparkles, Download, Share2, Loader2, MessageSquare, Heart, Clock } from 'lucide-react';

interface RunwayCreatorProps {
  selectedProduct?: any;
}

const RunwayCreator: React.FC<RunwayCreatorProps> = ({ selectedProduct }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoUrl, setAudioUrl] = useState<string | null>(null);
  const [style, setStyle] = useState("Neon Tokyo Night");
  const [step, setStep] = useState<'idle' | 'processing' | 'ready'>('idle');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [reactions, setReactions] = useState<any[]>([]);
  const [collectiveVibe, setCollectiveVibe] = useState<string>("Initializing...");

  const styles = [
    { id: 'tokyo', name: 'Neon Tokyo Night', icon: '🌃' },
    { id: 'paris', name: 'Parisian Morning', icon: '🥐' },
    { id: 'studio', name: 'Minimalist White Studio', icon: '📸' },
    { id: 'desert', name: 'Burning Man Sunset', icon: '🔥' }
  ];

  const fetchSocialReactions = async () => {
    if (!selectedProduct) return;
    try {
        const response = await axios.get(`http://localhost:8000/api/ai/social-reactions/${selectedProduct.id}`);
        setReactions(response.data.reactions);
        setCollectiveVibe(response.data.collective_vibe);
    } catch (e) { console.error(e); }
  };

  const generateRunway = async () => {
    if (!selectedProduct) return alert("Please select a product first");
    
    setIsGenerating(true);
    setStep('processing');
    fetchSocialReactions();
    
    try {
      // Dispatches asynchronous worker task
      const response = await axios.post(`http://localhost:8000/api/ai/generate-runway-reel?avatar_id=user_default&product_id=${selectedProduct.id}&scene_style=${encodeURIComponent(style)}`);
      setTaskId(response.data.task_id);
    } catch (error) {
      console.error('Movie Gen dispatch failed:', error);
      setStep('idle');
      setIsGenerating(false);
    }
  };

  // Poll for Task Completion
  useEffect(() => {
    let pollInterval: any;
    if (taskId && step === 'processing') {
        pollInterval = setInterval(async () => {
            try {
                const response = await axios.get(`http://localhost:8000/api/ai/task-status/${taskId}`);
                if (response.data.status === 'SUCCESS') {
                    setAudioUrl(response.data.result.video_url);
                    setStep('ready');
                    setIsGenerating(false);
                    setTaskId(null);
                    clearInterval(pollInterval);
                } else if (response.data.status === 'FAILURE') {
                    alert("Neural rendering failed on worker node.");
                    setStep('idle');
                    setIsGenerating(false);
                    setTaskId(null);
                    clearInterval(pollInterval);
                }
            } catch (e) { console.error("Poll failed", e); }
        }, 3000);
    }
    return () => clearInterval(pollInterval);
  }, [taskId, step]);

  return (
    <div className="bg-slate-950/50 backdrop-blur-3xl border border-white/5 rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden group">
      <div className="absolute -top-24 -right-24 w-64 h-64 bg-red-600/5 blur-[100px]" />
      
      <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-red-500/10 rounded-xl border border-red-500/20 text-red-400">
              <Film className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-black text-white uppercase tracking-[0.2em] text-[10px]">Cinematic Runway</h3>
              <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">Distributed Worker Engine</p>
            </div>
          </div>
          {step === 'processing' && (
              <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/5 animate-in fade-in zoom-in duration-500">
                  <Clock className="w-2.5 h-2.5 text-rose-500 animate-pulse" />
                  <span className="text-[8px] font-black text-slate-400 uppercase tracking-widest">Task: {taskId?.slice(0,8)}</span>
              </div>
          )}
      </div>

      {step === 'idle' && (
        <div className="space-y-6 animate-in fade-in duration-700">
          <div className="p-6 bg-white/5 rounded-3xl border border-white/5 text-center group/prod">
            {selectedProduct ? (
              <div className="space-y-1">
                <p className="text-[8px] text-slate-500 uppercase font-black tracking-widest">Active Template</p>
                <p className="text-sm font-black text-white group-hover/prod:text-red-400 transition-colors">{selectedProduct.name}</p>
              </div>
            ) : (
              <p className="text-[10px] text-slate-600 font-bold uppercase tracking-widest">Initialize assets to begin</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            {styles.map((s) => (
              <button key={s.id} onClick={() => setStyle(s.name)} className={`p-4 rounded-2xl border text-left transition-all relative overflow-hidden ${style === s.name ? 'bg-red-600/10 border-red-500/30 text-white shadow-lg' : 'bg-white/5 border-white/5 text-slate-500 hover:border-white/10'}`}>
                <span className="text-lg mb-2 block">{s.icon}</span>
                <span className="text-[9px] font-black uppercase tracking-tighter leading-tight">{s.name}</span>
              </button>
            ))}
          </div>

          <button onClick={generateRunway} disabled={!selectedProduct || isGenerating} className="w-full py-5 bg-white text-slate-950 rounded-2xl font-black text-xs uppercase tracking-widest transition-all hover:bg-red-500 hover:text-white disabled:opacity-20 flex items-center justify-center gap-2 active:scale-95">
            <Sparkles className="w-4 h-4" /> Synthesize HD Reel
          </button>
        </div>
      )}

      {step === 'processing' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-in fade-in duration-700">
          <div className="py-20 text-center space-y-6">
             <div className="relative inline-block">
                <Loader2 className="w-16 h-16 text-red-500 animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center">
                   <Film className="w-6 h-6 text-white" />
                </div>
             </div>
             <div className="space-y-3">
               <h4 className="text-sm font-black text-white uppercase tracking-[0.2em]">Neural Rendering...</h4>
               <p className="text-[9px] text-slate-600 font-bold uppercase max-w-[200px] mx-auto leading-relaxed tracking-widest">Movie Gen is processing in a background worker node.</p>
             </div>
          </div>
          
          <div className="bg-black/20 rounded-[2rem] p-6 border border-white/5 flex flex-col h-[250px]">
              <div className="flex items-center gap-2 mb-4 text-[8px] font-black uppercase tracking-widest text-slate-500">
                  <MessageSquare className="w-3 h-3" /> Live Community Reaction
              </div>
              <div className="space-y-4 overflow-hidden">
                  {reactions.map((r, i) => (
                      <div key={i} className="animate-in slide-in-from-right-4 fade-in duration-500" style={{ animationDelay: `${i * 300}ms` }}>
                          <div className="flex items-center gap-2 mb-1">
                              <span className="text-[9px] font-black text-red-400">{r.user}</span>
                              <Heart className="w-2.5 h-2.5 text-rose-500 fill-rose-500" />
                          </div>
                          <p className="text-[10px] text-slate-400 leading-tight font-medium">"{r.text}"</p>
                      </div>
                  ))}
              </div>
          </div>
        </div>
      )}

      {step === 'ready' && (
        <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-700">
          <div className="aspect-[9/16] bg-slate-900 rounded-[2rem] border border-white/5 flex flex-col items-center justify-center relative group overflow-hidden shadow-2xl">
             <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-80" />
             <div className="w-20 h-20 bg-white/10 backdrop-blur-md rounded-full border border-white/10 flex items-center justify-center group-hover:scale-110 transition-all cursor-pointer shadow-2xl">
                <Play className="w-8 h-8 text-white fill-white" />
             </div>
             <div className="absolute bottom-8 left-6 right-6 flex items-center justify-between">
                <div className="space-y-1">
                    <span className="block text-[8px] font-black text-slate-500 uppercase tracking-[0.2em]">Resolution</span>
                    <span className="text-[10px] font-mono text-red-400 font-bold tracking-tighter">1080P • 30FPS • HD</span>
                </div>
                <div className="flex gap-2">
                   <button className="p-3 bg-white/5 hover:bg-white/10 rounded-xl border border-white/5 transition-all"><Download className="w-4 h-4 text-slate-300" /></button>
                   <button className="p-3 bg-white/5 hover:bg-white/10 rounded-xl border border-white/5 transition-all"><Share2 className="w-4 h-4 text-slate-300" /></button>
                </div>
             </div>
          </div>
          <button onClick={() => setStep('idle')} className="w-full py-4 bg-transparent border border-white/10 text-slate-400 rounded-2xl font-black text-[9px] uppercase tracking-[0.3em] hover:bg-white/5 hover:text-white transition-all active:scale-95">Generate Version 2.0</button>
        </div>
      )}

    </div>
  );
};

export default RunwayCreator;
