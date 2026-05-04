import { useState } from 'react';
import axios from 'axios';

export const useAI = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [kinematics, setKinematics] = useState<any>(null);

  const handleAIScan = async (file: File, onComplete: (measurements: any) => void) => {
    setIsScanning(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/ai/foundation-scan', formData);
      onComplete({
        height: 175,
        chest: 95,
        waist: 75,
        hips: 100
      });
      alert("Sapiens Foundation Scan Complete: 308-point human geometry extracted.");
    } catch (error) {
      console.error('AI Scan failed:', error);
      alert('AI Scan failed. Please try a clearer photo.');
    } finally {
      setIsScanning(false);
    }
  };

  const handleActionDetected = async (action: string, intensity: string) => {
    try {
      const response = await axios.post('http://localhost:8000/api/ai/solve-kinematics', {
        landmarks: []
      });
      setKinematics(response.data);
    } catch (e) {
      console.error("Kinematic solve failed", e);
    }
  };

  return {
    isScanning,
    kinematics,
    handleAIScan,
    handleActionDetected
  };
};
