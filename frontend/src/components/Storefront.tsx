import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShoppingCart, Eye, Sparkles, Tag, ChevronRight } from 'lucide-react';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
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
  const [loading, setLoading] = useState(true);
  const [filter, setCategoryFilter] = useState('All');

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/products');
        setProducts(response.data);
      } catch (error) {
        console.error('Failed to fetch products:', error);
        // Fallback mock data for development
        setProducts([
          {
            id: '1',
            name: 'Cyberpunk Exo-Shell',
            description: 'Ultra-lightweight protective shell with reactive lighting.',
            price: 299.99,
            category: 'Outerwear',
            asset_urls: { '3d_model': '', image: '' }
          },
          {
            id: '2',
            name: 'Neon Weave Hoodie',
            description: 'Smart-fabric hoodie that adapts to body temperature.',
            price: 159.00,
            category: 'Tops',
            asset_urls: { '3d_model': '', image: '' }
          },
          {
            id: '3',
            name: 'Grav-Lift Sneakers',
            description: 'Next-gen footwear with simulated weightlessness.',
            price: 450.00,
            category: 'Shoes',
            asset_urls: { '3d_model': '', image: '' }
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  const categories = ['All', 'Outerwear', 'Tops', 'Bottoms', 'Shoes'];
  const filteredProducts = filter === 'All' ? products : products.filter(p => p.category === filter);

  return (
    <section className="py-24 px-6 bg-slate-950">
      <div className="container mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-8">
          <div>
            <h2 className="text-4xl font-bold mb-4 flex items-center gap-3">
              Digital Collection <Tag className="text-primary-500 w-6 h-6" />
            </h2>
            <p className="text-slate-400 max-w-xl">
              Browse our physically-verified digital fashion assets. All items are simulation-ready.
            </p>
          </div>
          
          <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                className={`px-6 py-2 rounded-full text-sm font-bold transition-all whitespace-nowrap ${
                  filter === cat 
                    ? 'bg-primary-600 text-white shadow-lg shadow-primary-900/20' 
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
          {filteredProducts.map(product => (
            <div 
              key={product.id}
              className="group bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden hover:border-primary-500/50 transition-all hover:shadow-2xl hover:shadow-primary-900/10"
            >
              {/* Product Preview Area */}
              <div className="h-72 bg-slate-800 relative flex items-center justify-center overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                
                {/* 3D Model Placeholder or Image */}
                <div className="w-32 h-32 bg-slate-700 rounded-2xl animate-pulse group-hover:scale-110 transition-transform duration-500" />
                
                <div className="absolute top-4 right-4 bg-slate-900/80 backdrop-blur-md px-3 py-1 rounded-full border border-slate-700">
                  <span className="text-xs font-mono text-primary-400">${product.price}</span>
                </div>
                
                <div className="absolute bottom-4 left-4 flex gap-2">
                   <div className="bg-emerald-500/10 text-emerald-400 text-[10px] font-bold px-2 py-1 rounded border border-emerald-500/20 uppercase tracking-tighter">
                     Physics Ready
                   </div>
                </div>
              </div>

              {/* Product Details */}
              <div className="p-8">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold group-hover:text-primary-400 transition-colors">{product.name}</h3>
                    <p className="text-xs text-slate-500 font-medium uppercase tracking-widest mt-1">{product.category}</p>
                  </div>
                  <Sparkles className="w-5 h-5 text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <p className="text-slate-400 text-sm leading-relaxed mb-8 line-clamp-2">
                  {product.description}
                </p>
                
                <div className="flex gap-3">
                  <button 
                    onClick={() => onSelectProduct(product)}
                    className="flex-1 flex items-center justify-center gap-2 py-3 bg-slate-800 hover:bg-primary-600 text-white rounded-xl font-bold transition-all text-sm group/btn"
                  >
                    <Eye className="w-4 h-4 group-hover/btn:scale-110 transition-transform" />
                    Try On
                  </button>
                  <button className="p-3 bg-slate-800 hover:bg-slate-700 rounded-xl transition-all">
                    <ShoppingCart className="w-5 h-5 text-slate-400" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {filteredProducts.length === 0 && (
          <div className="text-center py-24 border-2 border-dashed border-slate-800 rounded-3xl">
             <p className="text-slate-500 font-medium">No products found in this category.</p>
          </div>
        )}
      </div>
    </section>
  );
};

export default Storefront;
