"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import JarvisChat from "@/components/JarvisChat";

export default function Hero() {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden z-10 pt-20">
      <div className="text-center px-10 max-w-5xl z-10">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-3 font-mono text-[9px] tracking-[0.3em] uppercase text-sx-cyan border border-sx-cyan/30 bg-sx-cyan/5 px-6 py-2 mb-9 backdrop-blur-md"
        >
          <div className="w-1.5 h-1.5 rounded-full bg-sx-cyan animate-pulse shadow-[0_0_6px_rgba(0,162,232,0.6)]" />
          Autonomous Omni-Eternity Layer
        </motion.div>
        
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="font-bold text-5xl md:text-7xl lg:text-[120px] leading-[0.88] tracking-tighter text-white mb-5"
        >
          SYSTEM <span className="bg-gradient-to-br from-white via-sx-cyan to-oa-purple bg-clip-text text-transparent bg-[length:200%_200%] animate-gradient">CORE</span>
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="font-mono text-[10px] md:text-xs tracking-[0.4em] text-slate-500 uppercase mb-11"
        >
          SpaceX × OpenAI × NVIDIA × Tesla Workstation
        </motion.p>
        
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-12 leading-relaxed"
        >
          A fully decoupled 13-module autonomous ecosystem bridging game physics, real-time sync networks, aerospace drone telemetry, and long-term memory fabrics.
        </motion.p>
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="flex justify-center gap-5 flex-wrap"
        >
          <button onClick={() => setChatOpen(true)} className="group font-mono text-[10px] tracking-[0.18em] uppercase text-white bg-gradient-to-br from-indigo-600 to-indigo-500 py-4 px-11 font-bold relative overflow-hidden transition-transform cursor-none hover:shadow-[0_0_20px_rgba(79,70,229,0.4)]" style={{ clipPath: "polygon(12px 0, 100% 0, calc(100% - 12px) 100%, 0 100%)" }}>
            <span className="relative z-10">Initialize Jarvis</span>
            <div className="absolute inset-0 bg-white/20 translate-y-[100%] group-hover:translate-y-[0%] transition-transform duration-300 ease-out" />
          </button>
          <Link href="/compute" className="group inline-block font-mono text-[10px] tracking-[0.18em] uppercase text-slate-300 border border-white/15 bg-transparent py-4 px-11 hover:border-sx-cyan hover:text-white transition-all cursor-none hover:shadow-[0_0_20px_rgba(0,162,232,0.2)]" style={{ clipPath: "polygon(12px 0, 100% 0, calc(100% - 12px) 100%, 0 100%)" }}>
            <span className="relative z-10">Enter Workspace</span>
            <div className="absolute inset-0 bg-sx-cyan/10 translate-x-[-100%] group-hover:translate-x-[0%] transition-transform duration-300 ease-out" />
          </Link>
        </motion.div>
      </div>
      <JarvisChat isOpen={chatOpen} onClose={() => setChatOpen(false)} />
    </section>
  );
}
