import React from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import Features from './components/Features';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow">
        <Hero />
        <Features />
        
        {/* Call to Action */}
        <section className="py-24 px-6">
          <div className="container mx-auto max-w-4xl bg-gradient-to-br from-primary-600 to-secondary-600 rounded-3xl p-12 text-center shadow-2xl shadow-primary-900/20">
            <h3 className="text-3xl md:text-4xl font-bold mb-6 text-white">Ready to Transform Your Fashion Experience?</h3>
            <p className="text-primary-100 mb-10 text-lg">Join the alpha and start building your immersive 3D store today.</p>
            <button className="bg-white text-primary-700 font-black py-4 px-12 rounded-full hover:bg-primary-50 transition-all uppercase tracking-widest text-sm shadow-xl">
              Get Started Now
            </button>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}

export default App;
