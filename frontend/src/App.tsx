import React, { lazy, Suspense, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import Features from './components/Features';
import Footer from './components/Footer';
import Storefront from './components/Storefront';
import AIStylist from './components/AIStylist';
import AudioEngine from './components/AudioEngine';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingState from './components/LoadingState';
import { useAI } from './hooks/useAI';
import { useStore } from './store/useStore';

// Lazy load heavy multisensory components
const Scene3D = lazy(() => import('./components/Scene3D'));
const SplatViewer = lazy(() => import('./components/SplatViewer'));
const RunwayCreator = lazy(() => import('./components/RunwayCreator'));
const DigitalWardrobe = lazy(() => import('./components/DigitalWardrobe'));
const MovementTracker = lazy(() => import('./components/MovementTracker'));
const TrendInsights = lazy(() => import('./components/TrendInsights'));
const BodyControls = lazy(() => import('./components/BodyControls'));
const NeuromorphicLab = lazy(() => import('./components/NeuromorphicLab'));
const AutonomousHouse = lazy(() => import('./components/AutonomousHouse'));
const NerveCenter = lazy(() => import('./components/NerveCenter'));

function App() {
  const { 
    measurements, 
    selectedProduct, 
    isPhotorealMode, 
    activeMaterial,
    setSelectedProduct, 
    setPhotorealMode, 
    updateMeasurement, 
    resetMeasurements,
    setActiveMaterial
  } = useStore();

  const { isScanning, kinematics, handleAIScan, handleActionDetected } = useAI();

  // Material Auto-Sync Effect
  useEffect(() => {
    if (selectedProduct?.material) {
        const mat = selectedProduct.material.toLowerCase();
        if (mat.includes('silk') || mat.includes('knit')) setActiveMaterial('silk');
        else if (mat.includes('polymer')) setActiveMaterial('nylon');
        else setActiveMaterial('denim');
    }
  }, [selectedProduct, setActiveMaterial]);

  const handleProductSelect = (product: any) => {
    setSelectedProduct(product);
    document.getElementById('try-on-viewer')?.scrollIntoView({ behavior: 'smooth' });
  };

  const onAIScanChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleAIScan(file, (m) => useStore.getState().setMeasurements(m));
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-50">
      <Header />
      
      <main className="flex-grow">
        <Hero />
        
        <Storefront onSelectProduct={handleProductSelect} />

        {/* Try-On Experience Section */}
        <section id="try-on-viewer" className="py-32 px-6 bg-slate-900/50 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
             <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-600 rounded-full blur-[160px]" />
             <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-600 rounded-full blur-[160px]" />
          </div>

          <div className="container mx-auto">
            <div className="flex flex-col lg:flex-row gap-12 items-start">
              
              {/* Controls Sidebar */}
              <div className="w-full lg:w-[400px] space-y-8 shrink-0">
                <ErrorBoundary fallbackName="System Telemetry">
                    <Suspense fallback={<div className="h-60 bg-white/5 rounded-[2.5rem] animate-pulse" />}>
                        <NerveCenter />
                    </Suspense>
                </ErrorBoundary>

                <ErrorBoundary fallbackName="Autonomous House">
                    <Suspense fallback={<div className="h-80 bg-white/5 rounded-[2.5rem] animate-pulse" />}>
                        <AutonomousHouse />
                    </Suspense>
                </ErrorBoundary>

                <ErrorBoundary fallbackName="Neuromorphic Engine">
                    <Suspense fallback={<div className="h-80 bg-white/5 rounded-[2.5rem] animate-pulse" />}>
                        <NeuromorphicLab />
                    </Suspense>
                </ErrorBoundary>

                <ErrorBoundary fallbackName="Kinetic Tracker">
                    <Suspense fallback={<div className="h-40 bg-white/5 rounded-[2.5rem] animate-pulse" />}>
                        <MovementTracker onActionDetected={handleActionDetected} />
                    </Suspense>
                </ErrorBoundary>

                <ErrorBoundary fallbackName="Market Intelligence">
                    <Suspense fallback={<div className="h-40 bg-white/5 rounded-[2.5rem] animate-pulse" />}>
                        <TrendInsights />
                    </Suspense>
                </ErrorBoundary>

                <ErrorBoundary fallbackName="Runway Synth">
                    <Suspense fallback={<div className="h-60 bg-white/5 rounded-[2.5rem] animate-pulse" />}>
                        <RunwayCreator selectedProduct={selectedProduct} />
                    </Suspense>
                </ErrorBoundary>

                <ErrorBoundary fallbackName="Digital Vault">
                    <Suspense fallback={<div className="h-80 bg-white/5 rounded-[2.5rem] animate-pulse" />}>
                        <DigitalWardrobe />
                    </Suspense>
                </ErrorBoundary>
                
                <ErrorBoundary fallbackName="Anatomy Config">
                    <Suspense fallback={<div className="h-80 bg-white/5 rounded-[2.5rem] animate-pulse" />}>
                        <BodyControls 
                          measurements={measurements}
                          onMeasurementChange={(key, val) => updateMeasurement(key as any, val)}
                          onAIScan={onAIScanChange}
                          isScanning={isScanning}
                          onReset={resetMeasurements}
                        />
                    </Suspense>
                </ErrorBoundary>
              </div>

              {/* 3D Viewer Area */}
              <div className="flex-1 w-full bg-slate-800/30 rounded-[3rem] p-4 lg:p-8 min-h-[600px] border border-slate-800 shadow-inner group relative">
                <div className="absolute top-12 right-12 z-20">
                    <button 
                        onClick={() => setPhotorealMode(!isPhotorealMode)}
                        className={`px-6 py-2 rounded-full font-black text-[10px] uppercase tracking-widest transition-all ${
                            isPhotorealMode 
                                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/40' 
                                : 'bg-slate-900/80 text-slate-400 border border-slate-700 hover:border-emerald-500/50'
                        }`}
                    >
                        {isPhotorealMode ? '✨ Photoreal Splat Mode' : 'Standard 3D Mode'}
                    </button>
                </div>

                <ErrorBoundary fallbackName="Immersive Engine">
                    <Suspense fallback={<LoadingState message="Awakening Neural Render..." />}>
                        {isPhotorealMode ? (
                            <SplatViewer splatUrl={selectedProduct?.asset_urls?.['splat']} />
                        ) : (
                            <Scene3D 
                                measurements={measurements} 
                                kinematics={kinematics} 
                                activeMaterial={activeMaterial}
                            />
                        )}
                    </Suspense>
                </ErrorBoundary>
              </div>

            </div>
          </div>
        </section>

        <Features />
      </main>

      <Footer />
      <AIStylist />
      <AudioEngine storeVibe="Luxury tech-boutique with deep ambient synths" />
    </div>
  );
}

export default App;
