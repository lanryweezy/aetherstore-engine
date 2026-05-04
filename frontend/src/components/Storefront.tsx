import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShoppingCart, Eye, Sparkles, Tag, Search, RefreshCw, X, TrendingUp, Brain, Camera } from 'lucide-react';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  material: string;
  asset_urls: {
    '3d_model': string;
    image: string;
  };
}

interface StorefrontProps {
  onSelectProduct: (product: Product) => void;
}

const Storefront: React.FC<StorefrontProps> = ({ onSelectProduct }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [filter, setCategoryFilter] = useState('All');
  const [similarTo, setSimilarTo] = useState<Product | null>(null);
  const [similarProducts, setSimilarProducts] = useState<Product[]>([]);
  const [isLoadingSimilar, setIsLoadingSimilar] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFile, setSearchFile] = useState<File | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [hoveredProduct, setHoveredProduct] = useState<string | null>(null);
  const [aiReasoning, setAiReasoning] = useState<Record<string, string>>({});
  const [isAnalyzing, setIsAnalyzing] = useState<string | null>(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/products');
        setProducts(response.data);
      } catch (error) {
        console.error('Failed to fetch products:', error);
        setProducts([
          { id: '1', name: 'Cyberpunk Exo-Shell', description: 'Ultra-lightweight protective shell.', price: 299.99, category: 'Outerwear', material: 'Bio-Polymer', asset_urls: { '3d_model': '', image: '' } },
          { id: '2', name: 'Neon Weave Hoodie', description: 'Smart-fabric hoodie.', price: 159.00, category: 'Tops', material: 'Thermal-Knit', asset_urls: { '3d_model': '', image: '' } },
          { id: '3', name: 'Grav-Lift Sneakers', description: 'Next-gen footwear.', price: 450.00, category: 'Shoes', material: 'Nano-Spring', asset_urls: { '3d_model': '', image: '' } }
        ]);
      }
    };
    fetchProducts();

    const handleNewDrop = (e: any) => {
        console.log("Autonomous Drop Detected!", e.detail);
        fetchProducts(); 
    };
    window.addEventListener('aetherstore:new-drop' as any, handleNewDrop);
    return () => window.removeEventListener('aetherstore:new-drop' as any, handleNewDrop);
  }, []);

  const analyzeWithAI = async (product: Product) => {
    if (aiReasoning[product.id]) return;
    setIsAnalyzing(product.id);
    try {
        const response = await axios.post(`http://localhost:8000/api/ai/analyze-product/${product.id}`);
        setAiReasoning(prev => ({ ...prev, [product.id]: response.data.reasoning }));
    } catch (e) { console.error(e); }
    finally { setIsAnalyzing(null); }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim() && !searchFile) return;
    
    setIsSearching(true);
    try {
        const formData = new FormData();
        formData.append('query', searchQuery);
        if (searchFile) formData.append('file', searchFile);

        const response = await axios.post('http://localhost:8000/api/intelligence/multimodal-search', formData);
        const matched = products.filter(p => response.data.map((r: any) => r.id).includes(p.id));
        
        setSimilarProducts(matched.length > 0 ? matched : products.slice(0, 3));
        setSimilarTo({ name: searchQuery || 'Visual Anchor' } as any);
    } catch (error) {
        console.error('Search failed:', error);
    } finally {
        setIsSearching(false);
        setSearchFile(null);
    }
  };

  const findSimilar = async (product: Product) => {
    setSimilarTo(product);
    setIsLoadingSimilar(true);
    try {
      const response = await axios.post(`http://localhost:8000/api/recommendations/visual-similarity/${product.id}`);
      const similarIds = response.data.similar_products.map((p: any) => p.product_id);
      const matched = products.filter(p => similarIds.includes(p.id));
      setSimilarProducts(matched.length > 0 ? matched : products.filter(p => p.id !== product.id).slice(0, 3));
    } catch (error) { console.error(error); }
    finally { setIsLoadingSimilar(false); }
  };

  const categories = ['All', 'Outerwear', 'Tops', 'Bottoms', 'Shoes'];
  const baseProducts = similarTo ? similarProducts : products;
  const filteredProducts = filter === 'All' ? baseProducts : baseProducts.filter(p => p.category === filter);

  return (
    <section className="py-32 px-6 bg-[#020617]">
      <div className="container mx-auto">

        {/* AI Multi-Modal Search Bar */}
        <div className="mb-24 max-w-4xl mx-auto">
            <form onSubmit={handleSearch} className="relative group">
                <div className="absolute inset-0 bg-primary-500/20 blur-[100px] opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
                <div className="relative flex items-center bg-slate-900/50 backdrop-blur-3xl border border-white/5 rounded-[2rem] p-3 pl-8 shadow-[0_0_50px_rgba(0,0,0,0.5)] focus-within:border-primary-500/30 transition-all duration-500">
                    <Search className="w-5 h-5 text-slate-500 mr-4" />
                    <input 
                        type="text" 
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search collection with AI perception (image + text)..."
                        className="flex-1 bg-transparent border-none text-white focus:ring-0 placeholder:text-slate-600 font-bold text-lg"
                    />
                    
                    <label className={`p-4 rounded-2xl cursor-pointer transition-all mr-2 ${searchFile ? 'bg-primary-600 text-white' : 'bg-white/5 text-slate-500 hover:bg-white/10'}`}>
                        <Camera className="w-5 h-5" />
                        <input type="file" className="hidden" onChange={(e) => setSearchFile(e.target.files?.[0] || null)} />
                    </label>

                    <button 
                        type="submit"
                        className="bg-white text-slate-950 px-10 py-4 rounded-[1.5rem] font-black text-xs uppercase tracking-widest transition-all hover:bg-primary-400 hover:text-white flex items-center gap-2 active:scale-95"
                    >
                        {isSearching ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                        {isSearching ? 'Decoding...' : 'Joint Discovery'}
                    </button>
                </div>
                {searchFile && (
                    <div className="mt-4 flex justify-center animate-in slide-in-from-top-2 duration-300">
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-primary-500/10 text-primary-400 border border-primary-500/20 rounded-full text-[9px] font-black uppercase">
                            <span className="w-1 bg-primary-400 h-1 rounded-full animate-pulse" />
                            Visual Anchor: {searchFile.name}
                        </div>
                    </div>
                )}
            </form>
        </div>
        
        {similarTo && (
            <div className="mb-16 p-8 bg-primary-600/5 border border-primary-500/10 rounded-[2.5rem] flex items-center justify-between animate-in fade-in slide-in-from-top-8 duration-700">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-primary-500/10 rounded-[1.5rem] text-primary-400 shadow-xl shadow-primary-900/10">
                        <Search className="w-7 h-7" />
                    </div>
                    <div>
                        <h3 className="text-xl font-black tracking-tight">AI Curated: "{similarTo.name}"</h3>
                    </div>
                </div>
                <button onClick={() => setSimilarTo(null)} className="p-4 hover:bg-white/5 rounded-full text-slate-500 hover:text-white transition-all">
                    <X className="w-7 h-7" />
                </button>
            </div>
        )}

        <div className="flex flex-col md:flex-row justify-between items-end mb-20 gap-10">
          <div className="max-w-xl">
            <h2 className="text-5xl font-black mb-6 tracking-tighter uppercase">Global Collection</h2>
            <p className="text-slate-500 font-medium leading-relaxed">Browse physically-verified digital fashion inventory. All items are simulation-ready.</p>
          </div>
          <div className="flex gap-3 overflow-x-auto pb-4 no-scrollbar">
            {categories.map(cat => (
              <button key={cat} onClick={() => setCategoryFilter(cat)} className={`px-8 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all border ${filter === cat ? 'bg-white text-slate-950 border-white' : 'bg-transparent text-slate-500 border-white/5'}`}>
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
          {filteredProducts.map(product => (
            <div 
              key={product.id}
              onMouseEnter={() => { setHoveredProduct(product.id); analyzeWithAI(product); }}
              onMouseLeave={() => setHoveredProduct(null)}
              className="group bg-slate-900/30 border border-white/5 rounded-[2.5rem] overflow-hidden hover:border-primary-500/30 transition-all duration-700 hover:shadow-[0_0_80px_rgba(79,70,229,0.15)] flex flex-col relative"
            >
              {/* AI Reasoning Overlay */}
              <div className={`absolute inset-0 z-20 bg-slate-950/90 backdrop-blur-2xl p-10 flex flex-col justify-center transition-all duration-500 ${hoveredProduct === product.id ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12 pointer-events-none'}`}>
                  <div className="flex items-center gap-3 mb-6">
                      <Brain className="w-6 h-6 text-primary-400" />
                      <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white">Maverick MoE Reasoning</span>
                  </div>
                  {isAnalyzing === product.id ? (
                      <div className="space-y-4">
                          <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                              <div className="h-full bg-primary-500 animate-progress" style={{ width: '60%' }} />
                          </div>
                          <p className="text-xs font-black text-slate-500 uppercase tracking-widest animate-pulse text-center">Synchronizing expert networks...</p>
                      </div>
                  ) : (
                      <p className="text-sm text-slate-300 font-medium leading-relaxed italic">
                        "{aiReasoning[product.id] || 'Analyzing product architecture...'}"
                      </p>
                  )}
                  <div className="mt-10 pt-8 border-t border-white/5 flex gap-4">
                      <button onClick={() => onSelectProduct(product)} className="flex-1 py-4 bg-primary-600 text-white rounded-2xl font-black text-[10px] uppercase tracking-widest shadow-xl">Activate Try-On</button>
                      <button className="p-4 bg-white/5 border border-white/10 rounded-2xl text-white hover:bg-white/10 transition-all"><ShoppingCart className="w-5 h-5" /></button>
                  </div>
              </div>

              {/* Product Preview Area */}
              <div className="h-[400px] bg-slate-900/50 relative flex items-center justify-center overflow-hidden border-b border-white/5">
                <div className="w-40 h-40 bg-slate-800 rounded-[2rem] border border-white/5" />
                <div className="absolute top-6 right-6 bg-slate-950/80 backdrop-blur-xl px-4 py-2 rounded-2xl border border-white/10">
                  <span className="text-xs font-black text-white">${product.price}</span>
                </div>
                <div className="absolute top-20 right-6 flex items-center gap-1.5 bg-emerald-500/10 text-emerald-400 text-[9px] font-black px-3 py-1.5 rounded-full border border-emerald-500/20 backdrop-blur-xl">
                  <TrendingUp className="w-3 h-3" /> HOT
                </div>
              </div>

              {/* Product Details */}
              <div className="p-10 flex-1 flex flex-col">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="text-2xl font-black tracking-tight">{product.name}</h3>
                    <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.2em] mt-2">{product.category}</p>
                  </div>
                  <Sparkles className="w-6 h-6 text-primary-400" />
                </div>
                <p className="text-slate-500 text-sm leading-relaxed line-clamp-2 font-medium">{product.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Storefront;
