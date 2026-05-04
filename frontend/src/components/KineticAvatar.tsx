import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface KineticAvatarProps {
  measurements?: {
    height: number;
    chest: number;
    waist: number;
    hips: number;
  };
  kinematics?: any; 
  skinTone?: string;
  isMoving?: boolean;
  material?: string;
  onPointerOver?: (e: any) => void;
  onPointerOut?: () => void;
}

const KineticAvatar: React.FC<KineticAvatarProps> = ({ 
  measurements = { height: 175, chest: 95, waist: 80, hips: 95 },
  kinematics,
  skinTone = '#FDBCB4',
  isMoving = false,
  material = 'silk',
  onPointerOver,
  onPointerOut
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const clothRef = useRef<THREE.Mesh>(null);
  
  // Bone Refs for Momentum Integration
  const spineRef = useRef<THREE.Group>(null);
  const leftShoulderRef = useRef<THREE.Group>(null);
  const rightShoulderRef = useRef<THREE.Group>(null);
  const leftArmRef = useRef<THREE.Group>(null);
  const rightArmRef = useRef<THREE.Group>(null);

  const dims = useMemo(() => {
    return {
      h: measurements.height / 100,
      w: measurements.chest / 200,
      d: measurements.waist / 200
    };
  }, [measurements]);

  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    
    // Neural Cloth Vertex Displacement (Simulating Material Physics)
    if (clothRef.current) {
        const flowIntensity = material === 'silk' ? 0.08 : (material === 'nylon' ? 0.04 : 0.01);
        const waveSpeed = material === 'silk' ? 2.5 : 1.2;
        
        // Procedural vertex animation for realistic drape and movement
        const positions = clothRef.current.geometry.attributes.position;
        for (let i = 0; i < positions.count; i++) {
            const x = positions.getX(i);
            const z = Math.sin(x * 10 + time * waveSpeed) * flowIntensity;
            positions.setZ(i, z);
        }
        positions.needsUpdate = true;
    }

    if (kinematics && kinematics.joint_rotations) {
      const rots = kinematics.joint_rotations;
      if (leftShoulderRef.current) leftShoulderRef.current.quaternion.fromArray(rots.shoulder_l || [0,0,0,1]);
      if (rightShoulderRef.current) rightShoulderRef.current.quaternion.fromArray(rots.shoulder_r || [0,0,0,1]);
    } else if (isMoving) {
      if (spineRef.current) spineRef.current.rotation.y = Math.sin(time * 0.5) * 0.05;
      if (leftArmRef.current) leftArmRef.current.rotation.z = Math.sin(time * 2) * 0.2 + 0.5;
      if (rightArmRef.current) rightArmRef.current.rotation.z = -Math.sin(time * 2) * 0.2 - 0.5;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Root / Pelvis */}
      <mesh position={[0, dims.h * 0.45, 0]} castShadow>
        <boxGeometry args={[dims.w * 0.8, dims.h * 0.1, dims.d]} />
        <meshStandardMaterial color={skinTone} />
      </mesh>

      {/* Spine / Torso */}
      <group ref={spineRef} position={[0, dims.h * 0.5, 0]}>
        <mesh position={[0, dims.h * 0.15, 0]} castShadow>
          <boxGeometry args={[dims.w, dims.h * 0.3, dims.d * 0.8]} />
          <meshStandardMaterial color={skinTone} />
        </mesh>

        {/* Shoulders */}
        <group ref={leftShoulderRef} position={[dims.w * 0.5, dims.h * 0.25, 0]}>
          <group ref={leftArmRef}>
            <mesh position={[dims.w * 0.2, 0, 0]} rotation={[0, 0, -Math.PI / 2]} castShadow>
              <cylinderGeometry args={[0.04, 0.03, dims.w * 0.5]} />
              <meshStandardMaterial color={skinTone} />
            </mesh>
          </group>
        </group>

        <group ref={rightShoulderRef} position={[-dims.w * 0.5, dims.h * 0.25, 0]}>
          <group ref={rightArmRef}>
            <mesh position={[-dims.w * 0.2, 0, 0]} rotation={[0, 0, Math.PI / 2]} castShadow>
              <cylinderGeometry args={[0.04, 0.03, dims.w * 0.5]} />
              <meshStandardMaterial color={skinTone} />
            </mesh>
          </group>
        </group>

        {/* Head */}
        <mesh position={[0, dims.h * 0.35 + 0.1, 0]} castShadow>
          <sphereGeometry args={[0.12, 32, 32]} />
          <meshStandardMaterial color={skinTone} />
        </mesh>
      </group>

      {/* Neural Cloth Layer (The Smart Garment) */}
      <mesh 
        ref={clothRef} 
        position={[0, dims.h * 0.65, 0]} 
        castShadow
        onPointerOver={onPointerOver}
        onPointerOut={onPointerOut}
      >
        <torusGeometry args={[dims.w * 0.55, dims.h * 0.15, 64, 128]} />
        <meshPhysicalMaterial 
            color={material === 'silk' ? '#818cf8' : (material === 'nylon' ? '#10b981' : '#475569')}
            roughness={material === 'silk' ? 0.1 : 0.7}
            metalness={material === 'silk' ? 0.2 : 0.1}
            transmission={material === 'silk' ? 0.4 : 0}
            thickness={material === 'silk' ? 1.0 : 0}
            clearcoat={1.0}
            emissive={material === 'silk' ? '#4f46e5' : '#000000'}
            emissiveIntensity={0.2}
        />
      </mesh>

      {/* Legs */}
      <mesh position={[dims.w * 0.2, dims.h * 0.2, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.05, dims.h * 0.4]} />
        <meshStandardMaterial color="#1e293b" />
      </mesh>
      <mesh position={[-dims.w * 0.2, dims.h * 0.2, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.05, dims.h * 0.4]} />
        <meshStandardMaterial color="#1e293b" />
      </mesh>

      {/* Grid Floor */}
      <gridHelper args={[10, 20, 0x444444, 0x222222]} position={[0, 0, 0]} />
    </group>
  );
};

export default KineticAvatar;
