import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-950 text-slate-400 py-12 border-t border-slate-900">
      <div className="container mx-auto px-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="text-center md:text-left">
            <h4 className="text-white font-bold text-lg mb-2">Aetherstore Engine</h4>
            <p className="text-sm">Revolutionizing 3D Fashion Commerce.</p>
          </div>
          <div className="flex space-x-8 text-sm">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-white transition-colors">Documentation</a>
          </div>
          <p className="text-xs">&copy; 2023 Aetherstore Engine. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
