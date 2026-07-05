"use client";
import { motion } from "framer-motion";

export default function SecurityPage() {
  return (
    <div className="pt-[100px] px-12 max-w-[1400px] mx-auto min-h-screen text-slate-300">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-12">
        <h1 className="text-4xl font-bold tracking-tight text-white mb-2 font-mono">
          SECURITY <span className="text-red-500">FIREWALL</span>
        </h1>
        <p className="text-slate-500 font-mono text-xs uppercase tracking-widest">DPI Evasion & Defense</p>
      </motion.div>
      <div className="border border-red-500/20 bg-black/40 h-[600px] flex items-center justify-center relative overflow-hidden">
        <div className="font-mono text-xs text-red-500 animate-pulse tracking-widest">[ SECURE TUNNEL ESTABLISHED ]</div>
        <div className="absolute inset-0 bg-[linear-gradient(rgba(239,68,68,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(239,68,68,0.02)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />
      </div>
    </div>
  );
}
