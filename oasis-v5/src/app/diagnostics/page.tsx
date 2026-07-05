"use client";
import { motion } from "framer-motion";

export default function DiagnosticsPage() {
  return (
    <div className="pt-[100px] px-12 max-w-[1400px] mx-auto min-h-screen text-slate-300">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-12">
        <h1 className="text-4xl font-bold tracking-tight text-white mb-2 font-mono">
          SYSTEM <span className="text-yellow-500">DIAGNOSTICS</span>
        </h1>
        <p className="text-slate-500 font-mono text-xs uppercase tracking-widest">Self-Healing Event Logs</p>
      </motion.div>
      <div className="border border-yellow-500/20 bg-black/40 h-[600px] flex items-center justify-center relative overflow-hidden">
        <div className="font-mono text-xs text-yellow-500 animate-pulse tracking-widest">[ ZERO ANOMALIES DETECTED ]</div>
        <div className="absolute inset-0 bg-[linear-gradient(rgba(234,179,8,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(234,179,8,0.02)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />
      </div>
    </div>
  );
}
