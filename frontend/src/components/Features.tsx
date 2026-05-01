import React from 'react';
import { Sparkles, Monitor, Layout, Zap } from 'lucide-react';

const features = [
  {
    title: "Virtual Try-On",
    description: "High-fidelity cloth simulation powered by CUDA physics for zero-clipping realism.",
    icon: Monitor,
    color: "text-blue-400"
  },
  {
    title: "AI Stylist",
    description: "Personalized recommendations trained on 15M+ real-world fashion data points.",
    icon: Sparkles,
    color: "text-purple-400"
  },
  {
    title: "3D Store Builder",
    description: "Create immersive brand experiences with no-code 3D layout tools.",
    icon: Layout,
    color: "text-emerald-400"
  },
  {
    title: "Real-time Analytics",
    description: "Understand shopper behavior with 3D heatmaps and interactive tracking.",
    icon: Zap,
    color: "text-amber-400"
  }
];

const Features: React.FC = () => {
  return (
    <section className="py-24 bg-slate-900">
      <div className="container mx-auto px-6">
        <h3 className="text-3xl font-bold mb-16 text-center">Cutting-Edge Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="p-8 bg-slate-800 border border-slate-700 rounded-2xl hover:border-primary-500/50 transition-all group"
            >
              <feature.icon className={`w-12 h-12 mb-6 ${feature.color} group-hover:scale-110 transition-transform`} />
              <h4 className="text-xl font-bold mb-4">{feature.title}</h4>
              <p className="text-slate-400 text-sm leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
