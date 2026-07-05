"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [initializing, setInitializing] = useState(false);

  const handleInit = () => {
    if (initializing) return;
    setInitializing(true);
    setTimeout(() => setInitializing(false), 3000);
  };

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-[500] h-[65px] flex items-center justify-between px-12 border-b transition-colors duration-300 ${scrolled ? 'border-white/10 bg-[#020206]/80 backdrop-blur-xl' : 'border-white/5 bg-transparent'}`}>
      <div className="flex items-center gap-3 font-mono text-[11px] tracking-[0.25em] text-white font-bold">
        <div className="w-[7px] h-[7px] rounded-full bg-nv-green shadow-[0_0_8px_rgba(118,185,0,0.6)] animate-pulse" />
        OASIS_CORE
      </div>
      <ul className="flex gap-4 lg:gap-6 list-none flex-wrap justify-center">
        {['Memory', 'Compute', 'Aerospace', 'Noteboard', 'Master-Plan', 'Media-Studio', 'Telemetrics', 'Swarm-Control', 'Security', 'Quantum-Ops', 'Diagnostics', 'Nexus', 'Settings'].map((item, index) => (
          <motion.li 
            key={item}
            initial={{ opacity: 0, y: -15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + index * 0.05, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            <Link href={`/${item.toLowerCase()}`} className="font-mono text-[10px] tracking-[0.15em] uppercase text-slate-400 hover:text-white transition-colors relative group">
              {item}
              <span className="absolute -bottom-1 left-0 right-0 h-[1px] bg-sx-cyan scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300" />
            </Link>
          </motion.li>
        ))}
      </ul>
      <button 
        onClick={handleInit}
        className="font-mono text-[9.5px] tracking-[0.16em] uppercase text-black bg-gradient-to-br from-sx-cyan to-indigo-500 py-2.5 px-6 font-bold hover:opacity-90 hover:-translate-y-[1px] transition-all relative overflow-hidden" 
        style={{ clipPath: "polygon(8px 0, 100% 0, calc(100% - 8px) 100%, 0 100%)" }}
      >
        {initializing ? "Booting..." : "System Init"}
      </button>

      <AnimatePresence>
        {initializing && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }} 
            animate={{ opacity: 1, y: 0 }} 
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-[80px] right-12 bg-[#00a2e8]/10 border border-[#00a2e8]/30 px-6 py-3 font-mono text-[10px] text-[#00a2e8] uppercase tracking-widest backdrop-blur-md flex items-center gap-3 shadow-[0_0_15px_rgba(0,162,232,0.2)]"
          >
            <div className="w-2 h-2 rounded-full bg-[#00a2e8] animate-ping" />
            Initializing 13-Module Core...
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
