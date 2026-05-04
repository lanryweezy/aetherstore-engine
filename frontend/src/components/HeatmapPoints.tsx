import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface HeatmapPointsProps {
  points: { x: number, y: number, z: number, intensity: number }[];
  onPointClick?: (point: any) => void;
}

const HeatmapPoints: React.FC<HeatmapPointsProps> = ({ points, onPointClick }) => {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);

  useMemo(() => {
    if (meshRef.current) {
      points.forEach((point, i) => {
        dummy.position.set(point.x, point.y, point.z);
        dummy.scale.setScalar(0.05 + point.intensity * 0.1);
        dummy.updateMatrix();
        meshRef.current!.setMatrixAt(i, dummy.matrix);
        
        const color = new THREE.Color().setHSL(0.1 - point.intensity * 0.1, 1, 0.5);
        meshRef.current!.setColorAt(i, color);
      });
      meshRef.current.instanceMatrix.needsUpdate = true;
      if (meshRef.current.instanceColor) meshRef.current.instanceColor.needsUpdate = true;
    }
  }, [points, dummy]);

  return (
    <instancedMesh 
        ref={meshRef} 
        args={[undefined, undefined, points.length]}
        onClick={(e) => {
            e.stopPropagation();
            if (e.instanceId !== undefined && onPointClick) {
                onPointClick(points[e.instanceId]);
            }
        }}
    >
      <sphereGeometry args={[1, 16, 16]} />
      <meshBasicMaterial transparent opacity={0.6} />
    </instancedMesh>
  );
};

export default HeatmapPoints;
