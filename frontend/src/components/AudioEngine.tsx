import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { Volume2, VolumeX, Music, Loader2 } from 'lucide-react';

interface AudioEngineProps {
  storeVibe?: string;
}

const AudioEngine: React.FC<AudioEngineProps> = ({ storeVibe = "Luxury minimalist boutique with ambient pads" }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    const generateVibe = async () => {
      setIsLoading(true);
      try {
        const response = await axios.post(`http://localhost:8000/api/ai/generate-store-music?style_prompt=${encodeURIComponent(storeVibe)}`);
        // In a real app, this would be a real URL. For demo, we'll use a placeholder if the file doesn't exist yet.
        setAudioUrl(response.data.audio_url);
      } catch (error) {
        console.error('Failed to generate store vibe:', error);
      } finally {
        setIsLoading(false);
      }
    };

    generateVibe();
  }, [storeVibe]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch(e => console.log("Audio play blocked by browser", e));
    }
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="fixed bottom-8 left-8 z-50 flex items-center gap-3">
      <button 
        onClick={togglePlay}
        className={`p-4 rounded-2xl border transition-all flex items-center gap-3 ${
          isPlaying 
            ? 'bg-primary-600 border-primary-500 text-white shadow-lg shadow-primary-900/40' 
            : 'bg-slate-900/80 backdrop-blur-xl border-slate-700 text-slate-400 hover:border-primary-500/50'
        }`}
      >
        {isLoading ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : isPlaying ? (
          <Volume2 className="w-5 h-5" />
        ) : (
          <VolumeX className="w-5 h-5" />
        )}
        
        <div className="text-left">
          <p className="text-[10px] uppercase font-black tracking-tighter leading-none mb-1">
            {isLoading ? 'Generating OST...' : 'AI Atmosphere'}
          </p>
          <p className="text-xs font-medium opacity-80 max-w-[120px] truncate">
            {storeVibe}
          </p>
        </div>
      </button>

      {/* Hidden Audio Element */}
      <audio 
        ref={audioRef} 
        src={audioUrl || ''} 
        loop 
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      />
      
      {/* Vibe Status Indicator */}
      <div className="glass px-4 py-2 rounded-xl border-emerald-500/20 text-[10px] font-mono text-emerald-400 flex items-center gap-2">
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
        FLOWDEC: 4.5kbps
      </div>
    </div>
  );
};

export default AudioEngine;
