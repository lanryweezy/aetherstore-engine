import React, { Suspense, useState, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stage, Environment, PerformanceMonitor, AdaptiveDpr, Html } from '@react-three/drei';
import { XR, ARButton } from '@react-three/xr';
import { EffectComposer, Bloom, DepthOfField, Vignette } from '@react-three/postprocessing';
import axios from 'axios';
import Avatar from './KineticAvatar';
import InstancedRack from './InstancedRack';
import HeatmapPoints from './HeatmapPoints';
import { useStore } from '../store/useStore';

interface Scene3DProps {
  measurements?: any;
  kinematics?: any;
  activeMaterial?: string; // e.g., 'silk', 'nylon', 'denim'
}

const Scene3D: React.FC<Scene3DProps> = ({ measurements, kinematics, activeMaterial = 'silk' }) => {
  const { remoteUsers } = useStore();
  const [dpr, setDpr] = useState(1.5);
  const [showStore, setShowStore] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [heatmapData, setHeatmapData] = useState<any[]>([]);
  const [hapticTooltip, setHapticTooltip] = useState<{ x: number, y: number, text: string } | null>(null);
  const lastRotation = useRef(0);

  // Audio Trigger Logic (FlowDec Integration)
  const triggerFoley = async (intensity: number) => {
    try {
        await axios.post(`http://localhost:8000/api/ai/generate-foley?fabric_type=${activeMaterial}&motion_intensity=${intensity.toFixed(2)}`);
    } catch (e) { /* silent fail for foley */ }
  };

  const fetchHeatmap = async () => {
    try {
        const response = await axios.get('http://localhost:8000/api/analytics/heatmap/default_store');
        setHeatmapData(response.data.spatial_heatmap_3d);
        setShowHeatmap(true);
    } catch (e) { console.error("Heatmap failed", e); }
  };

  const handleHeatmapPointClick = async (point: any) => {
    setHapticTooltip({ x: window.innerWidth / 2, y: window.innerHeight / 2, text: "Consulting Maverick..." });
    try {
        const response = await axios.post(`http://localhost:8000/api/ai/maverick-advice?user_id=guest&message=Explain hotspot at ${point.x}, ${point.y}, ${point.z} with intensity ${point.intensity}`);
        setHapticTooltip({
            x: window.innerWidth / 2,
            y: 400,
            text: `Maverick Insight: ${response.data.reply}`
        });
    } catch (e) { console.error(e); }
  };

  return (
    <div 
        className="w-full h-[600px] bg-slate-950 rounded-[3rem] overflow-hidden shadow-[0_0_80px_rgba(0,0,0,0.8)] border border-white/5 relative group"
    >
      
      {/* Haptic Spatial HUD (TactoVis Integration) */}
      {hapticTooltip && (
          <div 
            className="absolute z-50 pointer-events-none bg-emerald-500/10 backdrop-blur-xl border border-emerald-500/30 px-4 py-2 rounded-xl animate-in fade-in zoom-in-95 duration-300 shadow-[0_0_20px_rgba(16,185,129,0.2)]"
            style={{ left: hapticTooltip.x - 200, top: hapticTooltip.y - 100 }}
          >
              <div className="flex items-center gap-2 mb-1">
                  <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                  <span className="text-[8px] font-black text-white uppercase tracking-widest">Virtual Feel Probe</span>
              </div>
              <p className="text-[10px] font-mono text-emerald-400 font-bold uppercase tracking-tight">{hapticTooltip.text}</p>
          </div>
      )}

      {/* HUD Layer */}
      <div className="absolute top-6 left-6 z-20 pointer-events-none">
        <h4 className="text-white font-black uppercase tracking-[0.3em] text-[10px]">Multisensory Sync Active</h4>
        <div className="flex items-center gap-2 mt-2">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-[9px] text-slate-500 font-mono uppercase">
                {showHeatmap ? 'SPATIAL ANALYTICS HUD' : `Spatial Audio • Material: ${activeMaterial}`}
            </span>
        </div>
      </div>

      <div className="absolute bottom-6 right-6 z-20 flex gap-3">
         <button 
             onClick={() => showHeatmap ? setShowHeatmap(false) : fetchHeatmap()}
             className={`px-4 py-2 rounded-xl border border-white/10 font-bold text-[9px] uppercase tracking-widest transition-all pointer-events-auto ${showHeatmap ? 'bg-rose-600 text-white shadow-lg' : 'bg-white/5 backdrop-blur-md text-white hover:bg-white/10'}`}
         >
             {showHeatmap ? 'Hide Hotspots' : 'Spatial Heatmap'}
         </button>
         <button 
             onClick={() => setShowStore(!showStore)}
             className="px-4 py-2 bg-white/5 backdrop-blur-md rounded-xl border border-white/10 text-white font-bold text-[9px] uppercase tracking-widest hover:bg-white/10 transition-all pointer-events-auto"
         >
             Toggle Environment
         </button>
         <div className="pointer-events-auto">
             <ARButton 
                 className="px-6 py-2 bg-primary-600 rounded-xl font-black text-[10px] uppercase tracking-widest text-white shadow-xl shadow-primary-900/40 hover:bg-primary-500 transition-all"
             />
         </div>
      </div>

      {/* WebGPU/WebGL Canvas */}
      <Canvas shadows camera={{ position: [0, 1.5, 4], fov: 50 }} dpr={dpr}>
        <PerformanceMonitor onDecline={() => setDpr(1)} onIncline={() => setDpr(2)} />
        <AdaptiveDpr pixelated />
        
        <XR>
            <Suspense fallback={null}>
            <Stage environment="city" intensity={0.5} adjustCamera={false}>
                {/* Local User Avatar */}
                <Avatar 
                    measurements={measurements} 
                    kinematics={kinematics} 
                    isMoving={!!kinematics} 
                    material={activeMaterial}
                    onPointerOver={(e: any) => {
                        const metrics = activeMaterial === 'silk' ? 'Softness: 0.98 | Breath: 0.85' : 'Softness: 0.45 | Durability: 0.92';
                        setHapticTooltip({ x: e.clientX, y: e.clientY, text: metrics });
                    }}
                    onPointerOut={() => setHapticTooltip(null)}
                />

                {/* Remote Peer Avatars */}
                {Object.entries(remoteUsers).map(([id, state]: [string, any]) => (
                    <group key={id} position={state.pos} rotation={state.rot}>
                        <Avatar 
                            measurements={{ height: 175, chest: 95, waist: 80, hips: 95 }}
                            isMoving={true}
                            skinTone="#475569"
                            material={state.active_material || 'denim'}
                        />
                        <Html position={[0, 2, 0]} center>
                            <div className="bg-slate-950/80 backdrop-blur-md border border-white/10 px-2 py-0.5 rounded-full text-[7px] font-black text-white uppercase tracking-widest whitespace-nowrap shadow-xl">
                                Peer: {id.slice(0, 8)}
                            </div>
                        </Html>
                    </group>
                ))}
                
                {showStore && <InstancedRack count={100} />}
                {showHeatmap && <HeatmapPoints points={heatmapData} onPointClick={handleHeatmapPointClick} />}
            </Stage>
            
            <Environment preset="city" />
            
            {/* Cinematic Post-Processing */}
            <EffectComposer disableNormalPass>
                <DepthOfField focusDistance={0} focalLength={0.02} bokehScale={2} height={480} />
                <Bloom luminanceThreshold={0.5} mipmapBlur intensity={1.5} />
                <Vignette eskil={false} offset={0.1} darkness={1.1} />
            </EffectComposer>

            </Suspense>
            
            <OrbitControls 
                enablePan={false} 
                minPolarAngle={Math.PI / 4} 
                maxPolarAngle={Math.PI / 1.5} 
                makeDefault 
                onChange={(e) => {
                    // Detect rotation speed to trigger fabric rustle
                    if (e?.target?.object?.rotation?.y) {
                        const delta = Math.abs(e.target.object.rotation.y - lastRotation.current);
                        if (delta > 0.05) {
                            triggerFoley(Math.min(delta * 5, 1.0));
                        }
                        lastRotation.current = e.target.object.rotation.y;
                    }
                }}
            />
        </XR>
      </Canvas>
      
      {/* Interaction Help Overlay */}
      <div className="absolute bottom-6 left-6 px-4 py-2 bg-slate-900/80 backdrop-blur-md rounded-xl border border-white/5 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
        <p className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Hover to feel • Drag to rotate</p>
      </div>
    </div>
  );
};

export default Scene3D;
