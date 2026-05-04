import { Sparkles, Brain, Boxes, Zap, Fingerprint, Layers, Volume2, Video, Cpu, Rocket } from 'lucide-react';

const featureList = [
  {
    title: "Autonomous AI Label",
    description: "A self-directing agent that autonomously designs collections, creates marketing, and deploys Web3 contracts.",
    icon: Rocket,
    color: "text-fuchsia-500",
    bg: "bg-fuchsia-500/10"
  },
  {
    title: "Neuromorphic Manufaturing",
    description: "Translate aesthetic thought patterns directly into industrial CNC & 3D Knitting G-Code.",
    icon: Cpu,
    color: "text-purple-500",
    bg: "bg-purple-500/10"
  },
  {
    title: "Universal Perception",
    description: "Multi-modal reasoning powered by Llama 4 Maverick and 3.2 Vision for expert-level styling.",
    icon: Brain,
    color: "text-red-400",
    bg: "bg-red-400/10"
  },
  {
    title: "Metric 3D Synthesis",
    description: "Generate simulation-ready metric meshes from casual video using ShapeR and SAM 3.",
    icon: Boxes,
    color: "text-blue-400",
    bg: "bg-blue-400/10"
  },
  {
    title: "Multisensory Immersion",
    description: "High-fidelity fabric foley and dynamic OSTs via FlowDec and MusicGen at 4.5kbps.",
    icon: Volume2,
    color: "text-emerald-400",
    bg: "bg-emerald-400/10"
  },
  {
    title: "Kinetic Geometry",
    description: "308-point Sapiens body scanning and Momentum kinematics for lifelike motion.",
    icon: Zap,
    color: "text-yellow-400",
    bg: "bg-yellow-400/10"
  },
  {
    title: "Sentient Social NPCs",
    description: "Autonomous shop assistants powered by Meta Motivo with human-level social intelligence.",
    icon: Fingerprint,
    color: "text-purple-400",
    bg: "bg-purple-400/10"
  },
  {
    title: "Mirror-Reality AR",
    description: "Real-time temporally consistent garment tracking using SAM 2 for live video streams.",
    icon: Video,
    color: "text-cyan-400",
    bg: "bg-cyan-400/10"
  }
];

const Features: React.FC = () => {
  return (
    <section className="py-40 bg-[#020617] relative overflow-hidden">
      {/* Background HUD */}
      <div className="absolute top-0 left-0 w-full h-full opacity-5 pointer-events-none">
          <div className="grid grid-cols-12 h-full">
              {[...Array(12)].map((_, i) => (
                  <div key={i} className="border-r border-white/20 h-full" />
              ))}
          </div>
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center mb-24">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-full mb-6">
                <span className="text-[10px] font-black uppercase tracking-[0.3em] text-primary-500">Multisensory Capabilities</span>
            </div>
            <h3 className="text-5xl md:text-6xl font-black tracking-tighter text-white">
                THE PINNACLE OF<br />FASHION TECHNOLOGY
            </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
          {featureList.map((feature, index) => (
            <div 
              key={index} 
              className="p-10 bg-white/5 border border-white/5 rounded-[3rem] hover:border-white/20 transition-all duration-700 group relative overflow-hidden"
            >
              <div className={`absolute -top-12 -right-12 w-40 h-40 ${feature.bg} blur-[60px] opacity-0 group-hover:opacity-100 transition-opacity duration-1000`} />
              
              <div className={`p-5 rounded-3xl inline-flex items-center justify-center mb-10 ${feature.bg} border border-white/5 group-hover:scale-110 transition-transform duration-500`}>
                <feature.icon className={`w-8 h-8 ${feature.color}`} />
              </div>
              
              <h4 className="text-2xl font-black mb-4 tracking-tight text-white group-hover:text-primary-400 transition-colors duration-500">
                {feature.title}
              </h4>
              <p className="text-slate-500 text-sm leading-relaxed font-medium group-hover:text-slate-400 transition-colors duration-500">
                {feature.description}
              </p>
              
              <div className="mt-8 pt-8 border-t border-white/5 flex items-center justify-between opacity-50 group-hover:opacity-100 transition-opacity duration-700">
                  <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Foundation Stack</span>
                  <div className="flex -space-x-2">
                      <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700" />
                      <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700" />
                      <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700" />
                  </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
