import React from 'react';
import { Ruler, Camera, Loader2, RefreshCw } from 'lucide-react';

interface BodyControlsProps {
  measurements: any;
  onMeasurementChange: (key: any, val: number) => void;
  onAIScan: (e: React.ChangeEvent<HTMLInputElement>) => void;
  isScanning: boolean;
  onReset: () => void;
}

const BodyControls: React.FC<BodyControlsProps> = ({ 
  measurements, 
  onMeasurementChange, 
  onAIScan, 
  isScanning, 
  onReset 
}) => {
  return (
    <div className="p-8 bg-slate-950/50 backdrop-blur-3xl border border-white/5 rounded-[2.5rem] space-y-8 shadow-2xl relative overflow-hidden group">
      <div className="absolute -top-10 -right-10 w-24 h-24 bg-primary-600/5 blur-3xl" />
      
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary-500/10 rounded-xl border border-primary-500/20 text-primary-400">
            <Ruler className="w-5 h-5" />
          </div>
          <h3 className="font-black text-white uppercase tracking-[0.2em] text-[10px]">Anatomy Calibration</h3>
        </div>
        <button 
          onClick={onReset}
          className="p-2 text-slate-600 hover:text-white transition-all hover:rotate-180 duration-500"
          title="Reset Geometry"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-6">
        {Object.entries(measurements).map(([key, val]: [string, any]) => (
          <div key={key} className="group/item">
            <div className="flex justify-between text-[9px] text-slate-500 uppercase font-black mb-3 tracking-[0.15em] group-hover/item:text-slate-300 transition-colors">
              <span>{key.replace('_', ' ')}</span>
              <span className="text-primary-400 font-mono text-[10px]">{val} MM</span>
            </div>
            <div className="relative h-1.5 w-full bg-slate-800 rounded-full overflow-hidden border border-white/5">
                <input 
                  type="range" 
                  min={key === 'height' ? 140 : 60}
                  max={key === 'height' ? 210 : 130}
                  value={val}
                  onChange={(e) => onMeasurementChange(key as any, parseInt(e.target.value))}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                <div 
                    className="absolute top-0 left-0 h-full bg-gradient-to-r from-primary-600 to-indigo-500 transition-all duration-300"
                    style={{ width: `${((val - (key === 'height' ? 140 : 60)) / ((key === 'height' ? 210 : 130) - (key === 'height' ? 140 : 60))) * 100}%` }}
                />
            </div>
          </div>
        ))}
      </div>

      <div className="pt-6 border-t border-white/5">
        <label className="relative w-full flex items-center justify-center gap-3 py-5 bg-white hover:bg-primary-500 text-slate-950 hover:text-white rounded-2xl font-black text-xs uppercase tracking-widest transition-all shadow-xl hover:shadow-primary-900/30 cursor-pointer overflow-hidden group/btn active:scale-95">
          <div className="absolute inset-0 bg-primary-400/20 translate-y-full group-hover/btn:translate-y-0 transition-transform duration-500" />
          <div className="relative z-10 flex items-center gap-3">
              {isScanning ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Camera className="w-5 h-5 group-hover/btn:scale-110 transition-transform" />
              )}
              {isScanning ? 'Extracting Sapiens Data...' : 'AI Foundation Scan'}
          </div>
          <input 
            type="file" 
            className="hidden" 
            accept="image/*" 
            onChange={onAIScan}
            disabled={isScanning}
          />
        </label>
        <div className="mt-6 flex items-start gap-3 p-4 bg-white/5 rounded-2xl border border-white/5">
            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-1.5 animate-pulse shrink-0" />
            <p className="text-[9px] text-slate-500 font-bold uppercase leading-relaxed tracking-wider">
              308-Point Sapiens Engine Active. Geometry accuracy optimized for PBR physics.
            </p>
        </div>
      </div>
    </div>
  );
};

export default BodyControls;
