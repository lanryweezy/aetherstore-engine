import React, { useState } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import Features from './components/Features';
import Footer from './components/Footer';
import Scene3D from './components/Scene3D';
import { Ruler, Trash2, Camera } from 'lucide-react';

function App() {
  const [measurements, setMeasurements] = useState({
    height: 175,
    chest: 95,
    waist: 80,
    hips: 95
  });

  const handleMeasurementChange = (key: keyof typeof measurements, val: number) => {
    setMeasurements(prev => ({ ...prev, [key]: val }));
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-50">
      <Header />
      
      <main className="flex-grow">
        <Hero />
        
        {/* Virtual Try-On Section */}
        <section className="py-24 px-6 bg-slate-900/50">
          <div className="container mx-auto">
            <div className="flex flex-col lg:flex-row gap-12 items-start">
              
              {/* Controls Sidebar */}
              <div className="w-full lg:w-[400px] space-y-8 shrink-0">
                <div className="p-8 bg-slate-800 border border-slate-700 rounded-3xl space-y-6 shadow-xl">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-primary-500/20 rounded-lg text-primary-400">
                      <Ruler className="w-5 h-5" />
                    </div>
                    <h3 className="text-xl font-bold uppercase tracking-tight">Body Parameters</h3>
                  </div>

                  {Object.entries(measurements).map(([key, value]) => (
                    <div key={key} className="space-y-3">
                      <div className="flex justify-between items-center text-sm font-medium">
                        <span className="capitalize text-slate-400">{key}</span>
                        <span className="text-primary-400 font-mono">{value}cm</span>
                      </div>
                      <input 
                        type="range" 
                        min={key === 'height' ? 140 : 60} 
                        max={key === 'height' ? 210 : 130} 
                        value={value}
                        onChange={(e) => handleMeasurementChange(key as any, Number(e.target.value))}
                        className="w-full h-1.5 bg-slate-700 rounded-full appearance-none cursor-pointer accent-primary-500"
                      />
                    </div>
                  ))}

                  <div className="pt-6 flex gap-3">
                    <button className="flex-1 flex items-center justify-center gap-2 py-3 bg-primary-600 hover:bg-primary-700 rounded-xl font-bold transition-all text-sm uppercase tracking-wider">
                      <Camera className="w-4 h-4" />
                      AI Scan
                    </button>
                    <button className="p-3 bg-slate-700 hover:bg-slate-600 rounded-xl transition-all">
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                <div className="p-6 bg-indigo-900/10 border border-indigo-500/20 rounded-2xl">
                  <p className="text-xs text-indigo-300 leading-relaxed italic">
                    "Our AI uses the SHIFT15M dataset to predict how these measurements affect garment drape across 15 million reference points."
                  </p>
                </div>
              </div>

              {/* 3D Viewer Area */}
              <div className="flex-1 w-full">
                <Scene3D measurements={measurements} />
                <div className="mt-8 flex gap-4 overflow-x-auto pb-4 custom-scrollbar">
                  {[1, 2, 3, 4].map(i => (
                    <button key={i} className="w-24 h-24 shrink-0 bg-slate-800 border border-slate-700 rounded-2xl hover:border-primary-500 transition-all overflow-hidden relative group">
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 to-transparent flex items-end justify-center p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <span className="text-[10px] font-bold text-white uppercase tracking-tighter">Try On</span>
                      </div>
                      <div className="w-full h-full bg-slate-700 animate-pulse" />
                    </button>
                  ))}
                </div>
              </div>

            </div>
          </div>
        </section>

        <Features />
      </main>

      <Footer />
    </div>
  );
}

export default App;
