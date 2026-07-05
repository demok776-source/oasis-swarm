"use client";
import { useEffect, useState } from "react";
import Navbar from "@/components/layout/Navbar";
import { Activity, Server, Database } from "lucide-react";

/**
 * Interface representing the telemetry payload from the App-Tier backend.
 */
export interface TelemetryData {
  status: string;
  cpu_usage: number;
  ram_usage: number;
  db_size_kb: number;
  ws_connections: number;
  contacts_count: number;
  events_count: number;
  redis_status: string;
  qdrant_status: string;
}

export default function Dashboard() {
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);

  useEffect(() => {
    const fetchTelemetry = async () => {
      try {
        const res = await fetch("http://localhost:8081/health/telemetry");
        const data = await res.json();
        setTelemetry(data);
      } catch (err) {
        console.error("Failed to fetch telemetry", err);
      }
    };
    
    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 2000); // fetch every 2s
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen flex flex-col pt-24 px-12 relative bg-[#020206]">
      <Navbar />
      <div className="max-w-7xl mx-auto w-full z-10 relative">
        <h1 className="font-mono text-2xl text-white mb-8 border-b border-white/10 pb-4 flex items-center gap-3">
          <Activity className="text-[#00a2e8]" />
          Compute Dashboard
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="border border-white/10 bg-white/5 p-6 backdrop-blur-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-[#00a2e8] scale-y-0 group-hover:scale-y-100 transition-transform origin-top" />
            <h3 className="font-mono text-xs text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Server className="w-4 h-4" /> CPU Usage
            </h3>
            <div className="text-4xl font-bold text-white transition-all duration-300">
              {telemetry ? `${telemetry.cpu_usage}%` : "OFFLINE"}
            </div>
          </div>
          
          <div className="border border-white/10 bg-white/5 p-6 backdrop-blur-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500 scale-y-0 group-hover:scale-y-100 transition-transform origin-top" />
            <h3 className="font-mono text-xs text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Database className="w-4 h-4" /> Memory Fabric DB
            </h3>
            <div className="text-4xl font-bold text-[#00a2e8] transition-all duration-300">
              {telemetry ? `${telemetry.db_size_kb} KB` : "OFFLINE"}
            </div>
          </div>
          
          <div className="border border-white/10 bg-white/5 p-6 backdrop-blur-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-[#76b900] scale-y-0 group-hover:scale-y-100 transition-transform origin-top" />
            <h3 className="font-mono text-xs text-slate-400 uppercase tracking-widest mb-4">App-Tier Status</h3>
            <div className={`text-2xl font-bold ${telemetry && telemetry.status === 'ONLINE' ? 'text-[#76b900]' : 'text-[#cc0000]'}`}>
              {telemetry ? telemetry.status : "DISCONNECTED"}
            </div>
            {telemetry && (
              <div className="text-[10px] text-slate-500 mt-3 font-mono border-t border-white/10 pt-3">
                Redis: <span className={telemetry.redis_status === 'ONLINE' ? 'text-[#76b900]' : 'text-slate-400'}>{telemetry.redis_status}</span> | 
                Qdrant: <span className={telemetry.qdrant_status === 'ONLINE' ? 'text-[#76b900]' : 'text-slate-400'}>{telemetry.qdrant_status}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
