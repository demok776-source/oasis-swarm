"use client";
import { motion } from "framer-motion";

export default function NexusPage() {
  return (
    <div className="pt-[100px] px-12 max-w-[1400px] mx-auto min-h-screen text-slate-300">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-12">
        <h1 className="text-4xl font-bold tracking-tight text-white mb-2 font-mono">
          THE <span className="text-white">NEXUS</span>
        </h1>
        <p className="text-slate-500 font-mono text-xs uppercase tracking-widest">Central Omni-Channel Hub</p>
      </motion.div>
      <div className="border border-white/20 bg-black/40 h-[600px] flex items-center justify-center relative overflow-hidden">
        <div className="font-mono text-xs text-white animate-pulse tracking-widest">[ ALL MODULES SYNCED ]</div>
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />
      </div>
    </div>
  );
}
