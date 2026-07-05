"use client";
import { useEffect, useState } from "react";
import Navbar from "@/components/layout/Navbar";
import { Database, Network, Search, HardDrive } from "lucide-react";

export default function Memory() {
  const [dbStats, setDbStats] = useState({ size: 0, contacts: 0, events: 0 });

  useEffect(() => {
    const fetchTelemetry = async () => {
      try {
        const res = await fetch("http://localhost:8081/health/telemetry");
        const data = await res.json();
        setDbStats({ size: data.db_size_kb, contacts: data.contacts_count, events: data.events_count });
      } catch (err) {}
    };
    
    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen flex flex-col pt-24 px-12 relative bg-[#020206]">
      <Navbar />
      <div className="max-w-7xl mx-auto w-full z-10 relative">
        <h1 className="font-mono text-2xl text-white mb-8 border-b border-white/10 pb-4 flex items-center gap-3">
          <Database className="text-oa-purple" />
          Memory Fabric (Vector & Relation)
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="border border-white/10 bg-white/5 p-6 backdrop-blur-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-oa-purple scale-y-0 group-hover:scale-y-100 transition-transform origin-top" />
            <h3 className="font-mono text-xs text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-oa-purple" /> SQL Relational Storage
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-end border-b border-white/10 pb-2">
                <span className="font-mono text-[10px] text-slate-500 uppercase tracking-widest">Database Size</span>
                <span className="font-mono text-xl text-white">{dbStats.size} KB</span>
              </div>
              <div className="flex justify-between items-end border-b border-white/10 pb-2">
                <span className="font-mono text-[10px] text-slate-500 uppercase tracking-widest">Stored Contacts</span>
                <span className="font-mono text-xl text-white">{dbStats.contacts}</span>
              </div>
              <div className="flex justify-between items-end">
                <span className="font-mono text-[10px] text-slate-500 uppercase tracking-widest">Sync Events</span>
                <span className="font-mono text-xl text-white">{dbStats.events}</span>
              </div>
            </div>
          </div>

          <div className="border border-white/10 bg-white/5 p-6 backdrop-blur-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-[#00a2e8] scale-y-0 group-hover:scale-y-100 transition-transform origin-top" />
            <h3 className="font-mono text-xs text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Network className="w-4 h-4 text-[#00a2e8]" /> Qdrant Vector Store
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-end border-b border-white/10 pb-2">
                <span className="font-mono text-[10px] text-slate-500 uppercase tracking-widest">Collection</span>
                <span className="font-mono text-sm text-white">oasis_docs</span>
              </div>
              <div className="flex justify-between items-end border-b border-white/10 pb-2">
                <span className="font-mono text-[10px] text-slate-500 uppercase tracking-widest">Vector Dimension</span>
                <span className="font-mono text-xl text-white">1536</span>
              </div>
              <div className="flex justify-between items-end">
                <span className="font-mono text-[10px] text-slate-500 uppercase tracking-widest">Distance Metric</span>
                <span className="font-mono text-sm text-[#00a2e8]">Cosine</span>
              </div>
            </div>
          </div>
        </div>

        <div className="border border-white/10 bg-white/5 p-6 backdrop-blur-md">
          <h3 className="font-mono text-xs text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
            <Search className="w-4 h-4" /> Vector Search Simulation
          </h3>
          <div className="flex gap-4">
            <input 
              type="text" 
              placeholder="Query semantic memory..." 
              className="flex-1 bg-black/50 border border-white/10 text-white font-mono text-sm px-4 py-3 focus:outline-none focus:border-oa-purple transition-colors"
            />
            <button className="bg-oa-purple/20 text-oa-purple px-8 font-mono text-xs uppercase tracking-widest border border-oa-purple/50 hover:bg-oa-purple/40 transition-colors">
              Search
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
