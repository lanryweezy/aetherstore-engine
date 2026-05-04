import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Sparkles, MessageSquare, Loader2, X } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

const AIStylist: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your AetherStore AI Stylist, powered by Meta Llama 4 Maverick. I've analyzed your Sapiens body geometry and current fashion distribution shifts. How can I help you refine your digital style today?",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await axios.post('http://localhost:8000/api/ai/maverick-advice', {
        message: input,
        user_id: 'guest_user'
      });

      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.reply,
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      console.error('Maverick failed:', error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm having trouble connecting to the Maverick expert network. Please try again in a moment.",
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <>
      {/* Floating Toggle Button */}
      <button 
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-8 right-8 p-4 bg-primary-600 text-white rounded-[1.5rem] shadow-[0_0_50px_rgba(79,70,229,0.4)] hover:bg-primary-500 transition-all z-50 group border border-primary-500/50 ${isOpen ? 'scale-0' : 'scale-100'}`}
      >
        <div className="flex items-center gap-3 px-2">
            <MessageSquare className="w-6 h-6 group-hover:rotate-12 transition-transform" />
            <span className="text-xs font-black uppercase tracking-widest hidden md:block">Stylist</span>
        </div>
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 border-2 border-slate-950 rounded-full animate-pulse" />
      </button>

      {/* Chat Window */}
      <div className={`fixed bottom-8 right-8 w-[calc(100%-4rem)] md:w-[450px] h-[70vh] max-h-[700px] bg-slate-950/80 backdrop-blur-3xl border border-white/10 rounded-[2.5rem] shadow-[0_0_100px_rgba(0,0,0,0.8)] flex flex-col overflow-hidden z-50 transition-all duration-700 cubic-bezier(0.4, 0, 0.2, 1) ${isOpen ? 'scale-100 opacity-100 translate-y-0' : 'scale-90 opacity-0 translate-y-24 pointer-events-none'}`}>
        
        {/* Header */}
        <div className="p-8 bg-white/5 border-b border-white/5 flex justify-between items-center shrink-0">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-primary-500/10 rounded-2xl border border-primary-500/20">
              <Sparkles className="w-6 h-6 text-primary-400" />
            </div>
            <div>
              <h4 className="text-white font-black text-sm tracking-tight uppercase">Sentient Stylist</h4>
              <p className="text-slate-500 text-[9px] font-black uppercase tracking-[0.2em] mt-1">Llama 4 Maverick MoE</p>
            </div>
          </div>
          <button 
            onClick={() => setIsOpen(false)} 
            className="p-3 hover:bg-white/5 rounded-full text-slate-500 hover:text-white transition-all border border-transparent hover:border-white/5"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
          {messages.map(msg => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[90%] p-6 rounded-[2rem] text-sm leading-relaxed font-medium shadow-2xl ${
                msg.sender === 'user' 
                ? 'bg-primary-600 text-white rounded-tr-none' 
                : 'bg-white/5 text-slate-300 border border-white/5 rounded-tl-none'
              }`}>
                {msg.text}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white/5 p-6 rounded-[2rem] rounded-tl-none border border-white/5">
                <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                    <div className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                    <div className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-8 bg-white/5 border-t border-white/5 shrink-0">
          <div className="flex gap-3 p-3 bg-slate-900 border border-white/5 rounded-[1.5rem] focus-within:border-primary-500/30 transition-all duration-500">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask for style reasoning..."
              className="flex-1 bg-transparent border-none outline-none text-sm text-slate-200 px-4 font-bold placeholder:text-slate-700"
            />
            <button 
              onClick={handleSendMessage}
              disabled={!input.trim()}
              className="p-4 bg-white hover:bg-primary-500 text-slate-950 hover:text-white rounded-2xl transition-all disabled:opacity-20 active:scale-95 shadow-xl"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>

      </div>
    </>
  );
};

export default AIStylist;
