"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, X, Terminal, Cpu } from "lucide-react";
import { useStore } from "@/store/useStore";

export default function JarvisChat({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([
    { role: "system", content: "JARVIS Autonomous Omni-Eternity Layer activated. How can I assist you today?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setInput("");
    setIsLoading(true);

    try {
      const { apiKey } = useStore.getState();
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (apiKey) headers["x-api-key"] = apiKey;

      const response = await fetch("http://localhost:8081/ai/query", {
        method: "POST",
        headers,
        body: JSON.stringify({ query: userMessage, module: "JarvisChat" })
      });
      const data = await response.json();
      
      let replyText = "Connection established but no response.";
      if (data.response) {
        replyText = data.response;
      } else if (data.detail) {
        replyText = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      }
      
      setMessages(prev => [...prev, { role: "system", content: replyText }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: "system", content: "ОШИБКА: Не удалось подключиться к уровню приложений. Работает ли бэкенд на порту 8081?" }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          initial={{ opacity: 0, y: 100, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 100, scale: 0.95 }}
          transition={{ type: "spring", stiffness: 300, damping: 25 }}
          className="fixed bottom-10 right-10 w-[450px] h-[600px] bg-[#020206]/90 backdrop-blur-2xl border border-[#00a2e8]/30 z-[1000] flex flex-col font-mono shadow-[0_0_40px_rgba(0,162,232,0.15)] rounded-sm"
        >
          <div className="flex items-center justify-between p-4 border-b border-[#00a2e8]/30 bg-[#00a2e8]/5">
            <div className="flex items-center gap-3">
              <Cpu className="w-5 h-5 text-[#00a2e8]" />
              <span className="text-[#00a2e8] font-bold tracking-widest text-xs uppercase">JARVIS Agent Terminal</span>
            </div>
            <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors cursor-none">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-3 text-xs leading-relaxed ${
                  msg.role === 'user' 
                    ? 'bg-indigo-600/20 text-indigo-100 border border-indigo-500/30 rounded-l-md rounded-tr-md' 
                    : 'bg-[#00a2e8]/10 text-[#00a2e8] border border-[#00a2e8]/20 rounded-r-md rounded-tl-md'
                }`}>
                  {msg.role === 'system' && <span className="block text-[8px] text-[#00a2e8]/50 mb-1">SYSTEM_RESPONSE</span>}
                  {msg.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[85%] p-3 text-xs bg-[#00a2e8]/10 text-[#00a2e8] border border-[#00a2e8]/20 animate-pulse rounded-r-md rounded-tl-md">
                  Processing via LangGraph Agent...
                </div>
              </div>
            )}
          </div>
          
          <form onSubmit={sendMessage} className="p-4 border-t border-[#00a2e8]/30 bg-black/40 flex gap-3">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter command..." 
              className="flex-1 bg-transparent border-b border-[#00a2e8]/50 text-white text-xs px-2 py-2 focus:outline-none focus:border-[#00a2e8] placeholder-slate-600 cursor-none"
            />
            <button type="submit" disabled={isLoading} className="bg-[#00a2e8]/20 text-[#00a2e8] p-2 hover:bg-[#00a2e8]/40 transition-colors cursor-none disabled:opacity-50 rounded-sm">
              <Send className="w-4 h-4" />
            </button>
          </form>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
