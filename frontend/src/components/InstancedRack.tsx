import React, { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';

interface InstancedRackProps {
  count?: number;
}

const InstancedRack: React.FC<InstancedRackProps> = ({ count = 50 }) => {
  const meshRef = useRef<THREE.InstancedMesh>(null);

  // Generate random positions for the instanced items (simulating a circular store rack)
  const dummy = useMemo(() => new THREE.Object3D(), []);
  const particles = useMemo(() => {
    const temp = [];
    for (let i = 0; i < count; i++) {
      const theta = (i / count) * Math.PI * 2;
      const radius = 2.5 + Math.random() * 0.5;
      const x = Math.cos(theta) * radius;
      const z = Math.sin(theta) * radius;
      const y = (Math.random() - 0.5) * 2;
      temp.push({ x, y, z, rotation: theta + Math.PI / 2 });
    }
    return temp;
  }, [count]);

  useFrame(() => {
    if (meshRef.current) {
      particles.forEach((particle, i) => {
        dummy.position.set(particle.x, particle.y, particle.z);
        dummy.rotation.y = particle.rotation + Math.sin(Date.now() * 0.001 + i) * 0.1; // gentle sway
        dummy.updateMatrix();
        meshRef.current!.setMatrixAt(i, dummy.matrix);
      });
      meshRef.current.instanceMatrix.needsUpdate = true;
    }
  });

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, count]} castShadow receiveShadow>
      {/* Simple hanger/shirt placeholder geometry */}
      <capsuleGeometry args={[0.2, 0.4, 4, 8]} />
      <meshPhysicalMaterial 
        color="#38bdf8" 
        metalness={0.5} 
        roughness={0.5} 
        clearcoat={1.0}
        transmission={0.2}
      />
    </instancedMesh>
  );
};

export default InstancedRack;
