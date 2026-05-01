import React from 'react';
import { ShoppingBag, User, Box } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-slate-900/80 backdrop-blur-md text-white sticky top-0 z-50 border-b border-slate-800">
      <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Box className="text-primary-500 w-8 h-8" />
          <h1 className="text-xl font-bold tracking-tight">Aetherstore Engine</h1>
        </div>
        <ul className="hidden md:flex space-x-8 text-sm font-medium">
          <li><a href="#" className="hover:text-primary-500 transition-colors">Home</a></li>
          <li><a href="#" className="hover:text-primary-500 transition-colors">Products</a></li>
          <li><a href="#" className="hover:text-primary-500 transition-colors">Try-On</a></li>
          <li><a href="#" className="hover:text-primary-500 transition-colors">AI Assistant</a></li>
        </ul>
        <div className="flex items-center space-x-4">
          <button className="p-2 hover:bg-slate-800 rounded-full transition-colors">
            <User className="w-5 h-5" />
          </button>
          <button className="p-2 hover:bg-slate-800 rounded-full transition-colors">
            <ShoppingBag className="w-5 h-5" />
          </button>
        </div>
      </nav>
    </header>
  );
};

export default Header;
