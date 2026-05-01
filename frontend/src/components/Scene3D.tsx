import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stage, Environment, ContactShadows } from '@react-three/drei';
import Avatar from './Avatar';

interface Scene3DProps {
  measurements?: any;
}

const Scene3D: React.FC<Scene3DProps> = ({ measurements }) => {
  return (
    <div className="w-full h-[600px] bg-slate-900 rounded-3xl overflow-hidden shadow-2xl border border-slate-800 relative group">
      <div className="absolute top-6 left-6 z-10">
        <h4 className="text-white font-bold uppercase tracking-widest text-xs opacity-50">3D Interactive Viewer</h4>
      </div>
      
      <Canvas shadows camera={{ position: [0, 1.5, 4], fov: 50 }}>
        <Suspense fallback={null}>
          <Stage environment="city" intensity={0.5} contactShadow={false}>
            <Avatar measurements={measurements} />
          </Stage>
          <Environment preset="city" />
          <ContactShadows 
            opacity={0.4} 
            scale={10} 
            blur={2} 
            far={10} 
            resolution={256} 
            color="#000000" 
          />
        </Suspense>
        <OrbitControls 
          enablePan={false} 
          minPolarAngle={Math.PI / 4} 
          maxPolarAngle={Math.PI / 1.5} 
          makeDefault 
        />
      </Canvas>
      
      {/* Interaction Help Overlay */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 px-4 py-2 bg-slate-800/80 backdrop-blur-md rounded-full border border-slate-700 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
        <p className="text-[10px] text-slate-300 font-medium">Drag to rotate • Scroll to zoom</p>
      </div>
    </div>
  );
};

export default Scene3D;
