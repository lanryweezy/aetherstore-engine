import React, { useState, useRef } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import Features from './components/Features';
import Footer from './components/Footer';
import Scene3D from './components/Scene3D';
import Storefront from './components/Storefront';
import AIStylist from './components/AIStylist';
import axios from 'axios';
import { Ruler, Trash2, Camera, Loader2, Sparkles } from 'lucide-react';

function App() {
  const [measurements, setMeasurements] = useState({
    height: 175,
    chest: 95,
    waist: 80,
    hips: 95
  });
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [isScanning, setIsScanning] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleMeasurementChange = (key: keyof typeof measurements, val: number) => {
    setMeasurements(prev => ({ ...prev, [key]: val }));
  };

  const handleProductSelect = (product: any) => {
    setSelectedProduct(product);
    // Scroll to try-on section
    document.getElementById('try-on-viewer')?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleAIScan = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsScanning(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/ai/scan-body', formData);
      if (response.data.measurements) {
        setMeasurements({
          height: Math.round(response.data.measurements.height),
          chest: Math.round(response.data.measurements.chest),
          waist: Math.round(response.data.measurements.waist),
          hips: Math.round(response.data.measurements.hips)
        });
      }
    } catch (error) {
      console.error('AI Scan failed:', error);
      alert('AI Scan failed. Please try a clearer photo.');
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-50">
      <Header />
      
      <main className="flex-grow">
        <Hero />

        {/* Storefront Section */}
        <Storefront onSelectProduct={handleProductSelect} />
        
        {/* Virtual Try-On Section */}
        <section id="try-on-viewer" className="py-24 px-6 bg-slate-900/50">
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
                    <input 
                      type="file" 
                      ref={fileInputRef} 
                      className="hidden" 
                      accept="image/*" 
                      onChange={handleAIScan} 
                    />
                    <button 
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isScanning}
                      className="flex-1 flex items-center justify-center gap-2 py-3 bg-primary-600 hover:bg-primary-700 rounded-xl font-bold transition-all text-sm uppercase tracking-wider disabled:opacity-50"
                    >
                      {isScanning ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Camera className="w-4 h-4" />
                      )}
                      {isScanning ? 'Processing...' : 'AI Scan'}
                    </button>
                    <button 
                      onClick={() => setMeasurements({ height: 175, chest: 95, waist: 80, hips: 95 })}
                      className="p-3 bg-slate-700 hover:bg-slate-600 rounded-xl transition-all"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {selectedProduct && (
                  <div className="p-8 bg-slate-800 border border-primary-500/30 rounded-3xl space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="flex items-center gap-2 text-primary-400 text-xs font-bold uppercase tracking-widest">
                      <Sparkles className="w-3 h-3" /> Selected for Try-On
                    </div>
                    <h4 className="text-2xl font-bold">{selectedProduct.name}</h4>
                    <p className="text-slate-400 text-sm">{selectedProduct.description}</p>
                    <button className="w-full py-4 bg-gradient-to-r from-primary-600 to-indigo-600 rounded-xl font-black text-xs uppercase tracking-widest shadow-lg shadow-primary-900/20">
                      Simulate Fabric Physics
                    </button>
                  </div>
                )}

                <div className="p-6 bg-indigo-900/10 border border-indigo-500/20 rounded-2xl">
                  <p className="text-xs text-indigo-300 leading-relaxed italic">
                    "Our AI uses the SHIFT15M dataset to predict how these measurements affect garment drape across 15 million reference points."
                  </p>
                </div>
              </div>

              {/* 3D Viewer Area */}
              <div className="flex-1 w-full">
                <Scene3D measurements={measurements} />
              </div>

            </div>
          </div>
        </section>

        <Features />
      </main>

      <Footer />
      <AIStylist />
    </div>
  );
}

export default App;
