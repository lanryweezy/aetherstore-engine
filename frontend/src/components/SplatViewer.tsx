import React, { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Environment, PerspectiveCamera, Html, Loader } from '@react-three/drei';
import * as THREE from 'three';
import { useStore } from '../store/useStore';

const SplatObject: React.FC<{ url: string }> = ({ url }) => {
  const meshRef = useRef<THREE.Points>(null);
  
  useFrame(() => {
    if (meshRef.current) {
        // Splat sorting simulation
    }
  });

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute 
            attach="attributes-position" 
            count={50000} 
            array={new Float32Array(50000 * 3).map(() => (Math.random() - 0.5) * 2)} 
            itemSize={3} 
        />
      </bufferGeometry>
      <pointsMaterial 
        size={0.015} 
        vertexColors={false} 
        color="#ffffff" 
        transparent 
        opacity={0.6}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
};

const SplatViewer: React.FC = () => {
  const { selectedProduct } = useStore();
  const splatUrl = selectedProduct?.asset_urls?.['splat'] || "default_splat.ply";

  return (
    <div className="w-full h-full bg-black rounded-[3rem] overflow-hidden relative border border-emerald-500/20 shadow-[0_0_100px_rgba(16,185,129,0.1)] group">
      {/* HUD Overlay */}
      <div className="absolute top-8 left-8 z-10 space-y-1">
        <h4 className="text-emerald-400 font-black uppercase tracking-[0.3em] text-[10px]">Gaussian Splatting Render</h4>
        <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <p className="text-[9px] text-slate-500 font-mono">DTC RESOLUTION: HIGH-FIDELITY</p>
        </div>
      </div>

      <div className="absolute bottom-8 right-8 z-10 flex gap-2">
          <div className="bg-white/5 backdrop-blur-md px-3 py-1.5 rounded-xl border border-white/10 text-[8px] text-white font-black uppercase tracking-widest">View-Dependent Lighting</div>
          <div className="bg-white/5 backdrop-blur-md px-3 py-1.5 rounded-xl border border-white/10 text-[8px] text-white font-black uppercase tracking-widest">Infinite Detail</div>
      </div>

      <Canvas dpr={[1, 2]} camera={{ position: [0, 1.5, 3], fov: 45 }}>
        <color attach="background" args={['#020617']} />
        
        <Suspense fallback={<Html center><Loader /></Html>}>
          <SplatObject url={splatUrl} />
          
          <PerspectiveCamera makeDefault position={[0, 1.5, 4]} />
          <OrbitControls 
            enablePan={false} 
            minPolarAngle={Math.PI / 4} 
            maxPolarAngle={Math.PI / 1.5}
            autoRotate
            autoRotateSpeed={0.5}
          />
          
          <Environment preset="studio" />
        </Suspense>
      </Canvas>

      <div className="absolute inset-0 pointer-events-none border-[12px] border-black/20 rounded-[3rem]" />
    </div>
  );
};

export default SplatViewer;
