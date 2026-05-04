import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const Hero: React.FC = () => {
  const canvasRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    canvasRef.current.appendChild(renderer.domElement);

    // Create a more "High-Tech" background geometry
    const geometry = new THREE.TorusKnotGeometry(3, 0.8, 100, 16);
    const material = new THREE.MeshPhysicalMaterial({ 
      color: 0x6366f1,
      wireframe: true,
      transparent: true,
      opacity: 0.15,
      emissive: 0x4f46e5,
      emissiveIntensity: 0.5
    });
    const knot = new THREE.Mesh(geometry, material);
    scene.add(knot);

    // Floating particles for depth
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 2000;
    const posArray = new Float32Array(particlesCount * 3);
    for(let i=0; i<particlesCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 20;
    }
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const particlesMaterial = new THREE.PointsMaterial({
        size: 0.005,
        color: 0x818cf8,
        transparent: true,
        opacity: 0.8
    });
    const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particlesMesh);

    const pointLight = new THREE.PointLight(0x6366f1, 2);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);
    scene.add(new THREE.AmbientLight(0x1e1b4b, 1));

    camera.position.z = 10;

    const animate = () => {
      requestAnimationFrame(animate);
      knot.rotation.x += 0.002;
      knot.rotation.y += 0.003;
      particlesMesh.rotation.y += 0.001;
      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
      canvasRef.current?.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <section className="relative h-[90vh] flex items-center justify-center overflow-hidden bg-[#020617]">
      <div ref={canvasRef} className="absolute inset-0 z-0" />
      
      {/* Background Glows */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-primary-600/10 rounded-full blur-[120px]" />
          <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px]" />
      </div>

      <div className="container mx-auto px-6 relative z-10 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full mb-8 animate-in fade-in slide-in-from-top-4 duration-1000">
           <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
           <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">Pinnacle Intelligence v2.0 Active</span>
        </div>
        
        <h2 className="text-6xl md:text-8xl font-black mb-8 leading-[0.9] tracking-tighter text-white">
          THE FUTURE OF<br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-400 via-indigo-400 to-purple-500">
            SENTIENT FASHION
          </span>
        </h2>
        
        <p className="text-lg md:text-xl text-slate-400 mb-12 max-w-2xl mx-auto font-medium leading-relaxed">
          Experience a borderless, multisensory fashion metaverse powered by 25 state-of-the-art Meta Research foundation models.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-5 justify-center">
          <button className="bg-primary-600 hover:bg-primary-500 text-white font-black py-5 px-12 rounded-2xl transition-all shadow-2xl shadow-primary-900/40 text-sm uppercase tracking-widest hover:scale-[1.02] active:scale-[0.98]">
            Enter Marketplace
          </button>
          <button className="bg-slate-900/50 hover:bg-slate-800 text-white font-black py-5 px-12 rounded-2xl transition-all border border-white/10 backdrop-blur-md text-sm uppercase tracking-widest hover:scale-[1.02] active:scale-[0.98]">
            Launch AI Lab
          </button>
        </div>
      </div>

      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce opacity-20">
          <div className="w-6 h-10 border-2 border-white rounded-full flex justify-center pt-2">
              <div className="w-1 h-2 bg-white rounded-full" />
          </div>
      </div>
    </section>
  );
};

export default Hero;
