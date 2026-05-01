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
      text: "Hello! I'm your Aetherstore AI Stylist. Based on 15 million fashion trends, I can help you find the perfect outfit. What are you looking for today?",
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
      // In a real app, this calls an LLM or our recommendation engine
      // For now, we simulate the intelligent response from the backend
      const response = await axios.post('http://localhost:8000/api/ai/stylist-chat', {
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
      console.error('Chat failed:', error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm having trouble connecting to the fashion grid. Please try again in a moment.",
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
        className={`fixed bottom-8 right-8 p-4 bg-primary-600 text-white rounded-full shadow-2xl shadow-primary-900/40 hover:bg-primary-500 transition-all z-50 group ${isOpen ? 'scale-0' : 'scale-100'}`}
      >
        <MessageSquare className="w-6 h-6 group-hover:rotate-12 transition-transform" />
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 border-2 border-slate-950 rounded-full animate-pulse" />
      </button>

      {/* Chat Window */}
      <div className={`fixed bottom-8 right-8 w-full max-w-[400px] h-[600px] bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl flex flex-col overflow-hidden z-50 transition-all duration-500 ${isOpen ? 'scale-100 opacity-100 translate-y-0' : 'scale-90 opacity-0 translate-y-12 pointer-events-none'}`}>
        
        {/* Header */}
        <div className="p-6 bg-gradient-to-r from-primary-600 to-indigo-600 flex justify-between items-center shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h4 className="text-white font-bold text-sm">AI Fashion Stylist</h4>
              <p className="text-primary-100 text-[10px] font-medium uppercase tracking-wider">Powered by SHIFT15M Intelligence</p>
            </div>
          </div>
          <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-white/10 rounded-full transition-colors">
            <X className="w-5 h-5 text-white" />
          </button>
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] bg-fixed">
          {messages.map(msg => (
            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed ${
                msg.sender === 'user' 
                ? 'bg-primary-600 text-white rounded-tr-none' 
                : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-none shadow-lg'
              }`}>
                {msg.text}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-slate-800 p-4 rounded-2xl rounded-tl-none shadow-lg border border-slate-700">
                <Loader2 className="w-4 h-4 text-primary-400 animate-spin" />
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 bg-slate-900 border-t border-slate-800 shrink-0">
          <div className="flex gap-2 p-2 bg-slate-800 border border-slate-700 rounded-2xl focus-within:border-primary-500/50 transition-all">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask for style advice..."
              className="flex-1 bg-transparent border-none outline-none text-sm text-slate-200 px-2"
            />
            <button 
              onClick={handleSendMessage}
              disabled={!input.trim()}
              className="p-2 bg-primary-600 hover:bg-primary-500 text-white rounded-xl transition-all disabled:opacity-50 disabled:grayscale"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>

      </div>
    </>
  );
};

export default AIStylist;
