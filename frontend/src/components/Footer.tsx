import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-[#020617] text-slate-500 py-24 border-t border-white/5 relative overflow-hidden">
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-[500px] bg-primary-900/5 blur-[120px] pointer-events-none" />
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-16 mb-20">
          <div className="col-span-1 md:col-span-2">
            <h4 className="text-white font-black text-2xl tracking-tighter mb-6">AETHERSTORE</h4>
            <p className="text-sm leading-relaxed max-w-sm font-medium">
              The world's most advanced multisensory fashion ecosystem. Bridging the gap between Meta Research foundation models and premium digital commerce.
            </p>
          </div>
          
          <div>
            <h5 className="text-white font-black text-[10px] uppercase tracking-[0.3em] mb-8">Ecosystem</h5>
            <ul className="space-y-4 text-xs font-bold uppercase tracking-widest">
                <li><a href="#" className="hover:text-primary-400 transition-colors">Maverick MoE</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Sapiens Vision</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Neural Assets</a></li>
            </ul>
          </div>

          <div>
            <h5 className="text-white font-black text-[10px] uppercase tracking-[0.3em] mb-8">Governance</h5>
            <ul className="space-y-4 text-xs font-bold uppercase tracking-widest">
                <li><a href="#" className="hover:text-primary-400 transition-colors">Provenance</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Privacy Grid</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Secure Audio</a></li>
            </ul>
          </div>
        </div>

        <div className="pt-10 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6 text-[10px] font-black uppercase tracking-[0.2em]">
          <p className="text-slate-600">&copy; 2026 AetherStore Engine. Sentient Commerce Protocol.</p>
          <div className="flex gap-8">
            <a href="#" className="hover:text-white transition-colors">System Status</a>
            <a href="#" className="hover:text-white transition-colors">Protocol V2.0</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
