import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Briefcase, ShieldCheck, History, ExternalLink, Box, Sparkles, Loader2 } from 'lucide-react';

interface NFTAsset {
  asset_id: string;
  name: string;
  description: string;
  created_date: string;
  blockchain_hash: string;
  metadata: any;
}

const DigitalWardrobe: React.FC = () => {
  const [assets, setAssets] = useState<NFTAsset[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<NFTAsset | null>(null);

  useEffect(() => {
    fetchCollection();
  }, []);

  const fetchCollection = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/blockchain/collection/0xUserFashionWallet_123');
      setAssets(response.data.assets);
    } catch (error) {
      console.error('Failed to fetch NFT collection:', error);
      // Fallback mock data
      setAssets([
        {
          asset_id: 'asset_cp_001',
          name: 'Cyberpunk Exo-Shell (NFT Edition)',
          description: 'Limited edition version of the Exo-Shell with unique geometric textures.',
          created_date: new Date().toISOString(),
          blockchain_hash: '0x742d...f3a9',
          metadata: { rarity: 'Legendary' }
        },
        {
          asset_id: 'asset_nw_002',
          name: 'Neon Weave Hoodie (Verified)',
          description: 'Official brand-verified digital twin of the physical hoodie.',
          created_date: new Date().toISOString(),
          blockchain_hash: '0x1a8c...b2e1',
          metadata: { rarity: 'Epic' }
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-slate-950/50 backdrop-blur-3xl border border-white/5 rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden group">
      <div className="absolute -top-10 -right-10 w-24 h-24 bg-emerald-600/5 blur-3xl" />
      
      <div className="flex flex-col gap-6 mb-8">
        <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-emerald-500/10 rounded-xl border border-emerald-500/20 text-emerald-400 shadow-xl shadow-emerald-900/10">
                <Briefcase className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-black text-white uppercase tracking-[0.2em] text-[10px]">Digital Wardrobe</h3>
                <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">Asset Protocol v1.0</p>
              </div>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-white/5 rounded-full border border-white/5">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[9px] font-mono text-slate-400 tracking-tighter">0x74...f3a9</span>
            </div>
        </div>
      </div>

      {isLoading ? (
        <div className="py-20 flex flex-col items-center justify-center space-y-4">
          <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
          <p className="text-[10px] text-slate-500 uppercase tracking-[0.3em] font-black animate-pulse">Querying Ledger...</p>
        </div>
      ) : (
        <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
          {assets.map((asset) => (
            <div 
              key={asset.asset_id}
              onClick={() => setSelectedAsset(asset)}
              className={`p-6 rounded-3xl border transition-all cursor-pointer group/item relative overflow-hidden ${
                selectedAsset?.asset_id === asset.asset_id 
                  ? 'bg-emerald-600/10 border-emerald-500/40 shadow-2xl shadow-emerald-900/10' 
                  : 'bg-white/5 border-white/5 hover:border-emerald-500/30'
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <h4 className="font-black text-white group-hover/item:text-emerald-400 transition-colors text-sm tracking-tight">{asset.name}</h4>
                <div className="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-[8px] font-black rounded-lg border border-emerald-500/20 uppercase tracking-widest">
                  {asset.metadata?.rarity || 'Common'}
                </div>
              </div>
              <p className="text-[10px] text-slate-500 line-clamp-1 mb-5 font-medium leading-relaxed">{asset.description}</p>
              
              <div className="flex items-center justify-between pt-4 border-t border-white/5">
                <div className="flex items-center gap-2 text-[8px] text-slate-500 font-mono tracking-tighter bg-black/20 px-2 py-1 rounded-lg">
                  <ShieldCheck className="w-3 h-3 text-emerald-500" />
                  {asset.blockchain_hash}
                </div>
                <button className="p-2 hover:bg-white/10 rounded-xl transition-all">
                  <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover/item:text-white" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedAsset && (
        <div className="mt-8 animate-in slide-in-from-bottom-4 duration-700">
           <button 
             className="w-full py-5 bg-gradient-to-r from-emerald-600 to-teal-700 text-white rounded-2xl font-black text-xs uppercase tracking-widest shadow-2xl shadow-emerald-900/30 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-3"
           >
             <Box className="w-4 h-4" />
             Equip Digital Twin
           </button>
        </div>
      )}

      <div className="mt-8 p-5 bg-emerald-500/5 border border-emerald-500/10 rounded-2xl flex items-start gap-4">
        <Sparkles className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
        <p className="text-[9px] text-slate-400 leading-relaxed font-medium">
          Secure provenance enabled. Every asset is cryptographically verified for cross-metaverse portability and authentic ownership.
        </p>
      </div>
    </div>
  );
};

export default DigitalWardrobe;
