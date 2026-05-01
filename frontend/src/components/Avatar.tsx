import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface AvatarProps {
  measurements?: {
    height: number;
    chest: number;
    waist: number;
    hips: number;
  };
  skinTone?: string;
}

const Avatar: React.FC<AvatarProps> = ({ 
  measurements = { height: 175, chest: 95, waist: 80, hips: 95 },
  skinTone = '#FDBCB4'
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const bodyRef = useRef<THREE.Mesh>(null);
  const leftLegRef = useRef<THREE.Mesh>(null);
  const rightLegRef = useRef<THREE.Mesh>(null);

  const dimensions = useMemo(() => {
    const bodyHeight = measurements.height / 100;
    const bodyWidth = measurements.chest / 200;
    const bodyDepth = measurements.waist / 200;
    return { bodyHeight, bodyWidth, bodyDepth };
  }, [measurements]);

  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    
    // Idle animation: subtle breathing/sway
    if (groupRef.current) {
      groupRef.current.position.y = Math.sin(time * 0.5) * 0.02;
    }

    // Basic procedural movement
    if (leftLegRef.current && rightLegRef.current) {
      leftLegRef.current.rotation.x = Math.sin(time * 2) * 0.1;
      rightLegRef.current.rotation.x = Math.sin(time * 2 + Math.PI) * 0.1;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Torso */}
      <mesh ref={bodyRef} position={[0, dimensions.bodyHeight * 0.45, 0]} castShadow>
        <boxGeometry args={[Math.max(0.3, dimensions.bodyWidth * 0.7), dimensions.bodyHeight * 0.6, Math.max(0.2, dimensions.bodyDepth * 0.5)]} />
        <meshStandardMaterial color={skinTone} roughness={0.7} />
      </mesh>

      {/* Head */}
      <mesh position={[0, dimensions.bodyHeight * 0.75 + (dimensions.bodyWidth * 0.3), 0]} castShadow>
        <sphereGeometry args={[dimensions.bodyWidth * 0.35, 32, 32]} />
        <meshStandardMaterial color={skinTone} roughness={0.6} />
      </mesh>

      {/* Left Arm */}
      <mesh position={[dimensions.bodyWidth * 0.4, dimensions.bodyHeight * 0.6, 0]} rotation={[0, 0, Math.PI / 6]} castShadow>
        <cylinderGeometry args={[0.04, 0.04, dimensions.bodyHeight * 0.4]} />
        <meshStandardMaterial color={skinTone} />
      </mesh>

      {/* Right Arm */}
      <mesh position={[-dimensions.bodyWidth * 0.4, dimensions.bodyHeight * 0.6, 0]} rotation={[0, 0, -Math.PI / 6]} castShadow>
        <cylinderGeometry args={[0.04, 0.04, dimensions.bodyHeight * 0.4]} />
        <meshStandardMaterial color={skinTone} />
      </mesh>

      {/* Left Leg */}
      <mesh ref={leftLegRef} position={[dimensions.bodyWidth * 0.2, dimensions.bodyHeight * 0.1, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.06, dimensions.bodyHeight * 0.45]} />
        <meshStandardMaterial color="#2d3436" />
      </mesh>

      {/* Right Leg */}
      <mesh ref={rightLegRef} position={[-dimensions.bodyWidth * 0.2, dimensions.bodyHeight * 0.1, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.06, dimensions.bodyHeight * 0.45]} />
        <meshStandardMaterial color="#2d3436" />
      </mesh>

      {/* Ground shadows */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
        <planeGeometry args={[10, 10]} />
        <shadowMaterial opacity={0.3} />
      </mesh>
    </group>
  );
};

export default Avatar;
