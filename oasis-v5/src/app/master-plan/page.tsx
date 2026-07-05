"use client";
import Navbar from "@/components/layout/Navbar";
import { motion } from "framer-motion";

export default function MasterPlanPage() {
  return (
    <main className="min-h-screen bg-void pt-28 pb-10 px-8 lg:px-20 relative overflow-hidden">
      <Navbar />
      
      <div className="max-w-7xl mx-auto relative z-10 flex flex-col gap-8 h-full">
        <header className="mb-8">
          <h1 className="font-bold text-4xl text-white mb-2">MASTER <span className="text-oa-purple">PLAN</span></h1>
          <p className="font-mono text-xs tracking-widest text-slate-500 uppercase">Module 12 // Eternal Roadmap & Media Pipelines</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="group bg-deep border border-white/5 p-8 relative hover:border-white/10 transition-colors"
          >
             <div className="absolute top-0 left-0 w-full h-[2px] bg-oa-purple scale-x-75 group-hover:scale-x-100 origin-left transition-transform duration-500" />
             <h2 className="font-mono text-sm tracking-widest text-white mb-4 uppercase">AI Media Pipelines</h2>
             <p className="text-slate-400 text-sm leading-relaxed mb-6">
                Integration layers for Module 10 (Image Creation Engine) and Module 11 (Video Creation Engine). 
                Autonomous scene rendering nodes are online and pending workload allocation.
             </p>
             <div className="flex gap-4">
               <button className="bg-white/10 hover:bg-white/20 text-white font-mono text-[10px] px-4 py-2 uppercase tracking-widest transition-colors cursor-none">Test Image Gen</button>
               <button className="bg-white/10 hover:bg-white/20 text-white font-mono text-[10px] px-4 py-2 uppercase tracking-widest transition-colors cursor-none">Test Video Gen</button>
             </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="group bg-deep border border-white/5 p-8 relative hover:border-white/10 transition-colors"
          >
             <div className="absolute top-0 left-0 w-full h-[2px] bg-sx-cyan scale-x-75 group-hover:scale-x-100 origin-left transition-transform duration-500" />
             <h2 className="font-mono text-sm tracking-widest text-white mb-4 uppercase">Ecosystem Expansion</h2>
             <ul className="space-y-4">
               <li className="flex items-center gap-3 font-mono text-xs text-slate-400">
                 <div className="w-2 h-2 bg-nv-green rounded-full shadow-[0_0_5px_rgba(118,185,0,0.8)]" />
                 Phase 1-4 Complete (Core, JARVIS, ECS, NoteBoard)
               </li>
               <li className="flex items-center gap-3 font-mono text-xs text-slate-400">
                 <div className="w-2 h-2 bg-sx-cyan rounded-full animate-pulse" />
                 Phase 5 Active (Media Engines)
               </li>
               <li className="flex items-center gap-3 font-mono text-xs text-slate-600">
                 <div className="w-2 h-2 bg-slate-700 rounded-full" />
                 Phase 6 Pending (Full Multi-Node Deployment)
               </li>
             </ul>
          </motion.div>
        </div>
      </div>
    </main>
  );
}
