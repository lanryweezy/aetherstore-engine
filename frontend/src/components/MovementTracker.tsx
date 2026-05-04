import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, Pause, Activity, Zap, RefreshCw } from 'lucide-react';

interface MovementTrackerProps {
  onActionDetected?: (action: string, intensity: string) => void;
}

const MovementTracker: React.FC<MovementTrackerProps> = ({ onActionDetected }) => {
  const [isTracking, setIsTracking] = useState(false);
  const [currentAction, setCurrentAction] = useState<string>("Analyzing...");
  const [intensity, setIntensity] = useState<string>("Normal");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const analyzeIntent = async () => {
    setIsAnalyzing(true);
    try {
      const response = await axios.post('http://localhost:8000/api/ai/analyze-movement-context?video_stream_id=live_user_stream');
      const { detected_action, movement_intensity } = response.data;
      
      setCurrentAction(detected_action);
      setIntensity(movement_intensity);
      
      if (onActionDetected) {
        onActionDetected(detected_action, movement_intensity);
      }
    } catch (error) {
      console.error('V-JEPA Analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  useEffect(() => {
    let interval: any;
    if (isTracking) {
      interval = setInterval(analyzeIntent, 8000);
    }
    return () => clearInterval(interval);
  }, [isTracking]);

  return (
    <div className="bg-slate-950/50 backdrop-blur-3xl border border-white/5 rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden group">
      <div className="absolute -top-10 -right-10 w-24 h-24 bg-cyan-600/5 blur-3xl" />
      
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 rounded-xl border border-cyan-500/20 text-cyan-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-black text-white uppercase tracking-[0.2em] text-[10px]">Kinetic Intelligence</h3>
            <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">V-JEPA Stream</p>
          </div>
        </div>
        <button 
          onClick={() => setIsTracking(!isTracking)}
          className={`p-3 rounded-2xl transition-all border ${
            isTracking 
                ? 'bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20' 
                : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20'
          }`}
        >
          {isTracking ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </button>
      </div>

      <div className="space-y-6">
        <div className="p-6 bg-white/5 rounded-3xl border border-white/5 relative overflow-hidden group/item">
          <div className="text-[9px] text-slate-500 uppercase font-black mb-3 tracking-[0.15em] group-hover/item:text-slate-300 transition-colors">Detected Intent</div>
          <div className="text-xl font-black text-white flex items-center gap-3">
            {isTracking ? currentAction : 'GRID_STANDBY'}
            {isAnalyzing && <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />}
          </div>
          
          {isTracking && (
            <div className="mt-5 space-y-3">
               <div className="flex justify-between text-[8px] text-slate-500 uppercase font-black tracking-widest">
                  <span>Movement Intensity</span>
                  <span className={intensity === 'high' ? 'text-red-400' : 'text-cyan-400'}>{intensity}</span>
               </div>
               <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden border border-white/5">
                  <div 
                    className={`h-full transition-all duration-1000 ease-out ${intensity === 'high' ? 'w-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]' : 'w-1/3 bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.5)]'}`} 
                  />
               </div>
            </div>
          )}
        </div>

        <div className="flex items-start gap-3 p-4 bg-cyan-500/5 rounded-2xl border border-cyan-500/10">
          <Zap className="w-4 h-4 text-cyan-500 shrink-0 mt-0.5" />
          <p className="text-[9px] text-slate-400 font-bold uppercase leading-relaxed tracking-wider">
            {isTracking 
              ? `V-JEPA is optimizing cloth-mesh dynamics for ${currentAction.toLowerCase()}.`
              : "Initialize stream to enable context-aware physics and autonomous recommendations."}
          </p>
        </div>
      </div>
    </div>
  );
};

export default MovementTracker;
