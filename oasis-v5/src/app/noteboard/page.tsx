"use client";
import { useEffect, useState, useRef } from "react";
import Navbar from "@/components/layout/Navbar";
import { motion } from "framer-motion";

type SyncEvent = {
  source: string;
  module: string;
  event: string;
  payload: any;
  timestamp: string;
};

type Task = {
  id: string;
  title: string;
  status: "TODO" | "IN_PROGRESS" | "DONE";
  module: string;
};

const INITIAL_TASKS: Task[] = [
  { id: "1", title: "Initialize Qdrant Vectors", status: "DONE", module: "JARVIS_AI" },
  { id: "2", title: "Establish WebSocket Sync", status: "DONE", module: "SYNC_LAYER" },
  { id: "3", title: "Deploy Noteboard UI", status: "IN_PROGRESS", module: "NOTE_BOARD" },
  { id: "4", title: "Build Unity ECS Engine", status: "TODO", module: "OASIS_PRIME" },
];

export default function NoteBoardPage() {
  const [tasks, setTasks] = useState<Task[]>(INITIAL_TASKS);
  const [events, setEvents] = useState<SyncEvent[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to Sync Layer WebSocket
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8081";
    const wsUrl = apiUrl.replace("http", "ws") + "/sync/ws";
    
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setEvents(prev => [{ ...data, timestamp: new Date().toLocaleTimeString() }, ...prev].slice(0, 50));
      } catch (e) {
        console.error("WS parse error", e);
      }
    };

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const moveTask = (taskId: string, newStatus: Task["status"]) => {
    setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
    // Emit sync event
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        source: "WS-Client-Noteboard",
        module: "NOTE_BOARD",
        event: "TASK_UPDATED",
        payload: { taskId, newStatus }
      }));
    }
  };

  const columns = ["TODO", "IN_PROGRESS", "DONE"] as const;

  return (
    <main className="min-h-screen bg-void pt-28 pb-10 px-8 lg:px-20 relative overflow-hidden">
      <Navbar />
      
      <div className="max-w-7xl mx-auto relative z-10 flex flex-col gap-8 h-full">
        <header className="mb-2">
          <h1 className="font-bold text-4xl text-white mb-2">NOTE <span className="text-sx-cyan">BOARD</span></h1>
          <p className="font-mono text-xs tracking-widest text-slate-500 uppercase">Module 6 // Project Management & Live Sync</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[70vh]">
          {/* Kanban Columns */}
          <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
            {columns.map(status => (
              <div key={status} className="flex flex-col bg-deep border border-white/5 p-4 relative">
                <div className="absolute top-0 left-0 w-full h-[2px] bg-white/10" />
                <h2 className="font-mono text-[10px] tracking-widest text-slate-400 mb-6 uppercase flex items-center gap-2">
                  <div className={`w-1.5 h-1.5 rounded-full ${status === "DONE" ? "bg-nv-green" : status === "IN_PROGRESS" ? "bg-sx-cyan" : "bg-white/30"}`} />
                  {status.replace("_", " ")}
                </h2>
                <div className="flex flex-col gap-3 flex-1">
                  {tasks.filter(t => t.status === status).map((task, index) => (
                    <motion.div 
                      layoutId={task.id}
                      key={task.id} 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1, duration: 0.3 }}
                      className="bg-void border border-white/10 p-4 hover:border-sx-cyan/50 hover:shadow-[0_0_15px_rgba(0,162,232,0.15)] transition-all group cursor-none"
                    >
                      <div className="text-xs font-mono text-sx-cyan mb-2 uppercase">{task.module}</div>
                      <div className="text-sm text-slate-300 mb-4">{task.title}</div>
                      <div className="flex gap-2">
                        {status !== "TODO" && (
                          <button onClick={() => moveTask(task.id, status === "DONE" ? "IN_PROGRESS" : "TODO")} className="text-[9px] font-mono border border-white/10 px-2 py-1 hover:bg-white/10 cursor-none">&lt; MOVE</button>
                        )}
                        {status !== "DONE" && (
                          <button onClick={() => moveTask(task.id, status === "TODO" ? "IN_PROGRESS" : "DONE")} className="text-[9px] font-mono border border-white/10 px-2 py-1 hover:bg-white/10 cursor-none ml-auto">MOVE &gt;</button>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Sync Event Log */}
          <div className="bg-deep border border-white/5 p-4 flex flex-col relative overflow-hidden">
             <div className="absolute top-0 left-0 w-full h-[2px] bg-oa-purple" />
             <h2 className="font-mono text-[10px] tracking-widest text-oa-purple mb-6 uppercase flex items-center gap-2">
               <div className="w-1.5 h-1.5 rounded-full bg-oa-purple animate-pulse" />
               Sync Layer Live Log
             </h2>
             <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-hide">
               {events.length === 0 ? (
                 <div className="text-xs font-mono text-slate-600">Waiting for events...</div>
               ) : (
                 events.map((ev, i) => (
                   <div key={i} className="text-[10px] font-mono border-l-2 border-white/10 pl-3 py-1">
                     <span className="text-slate-500 block mb-1">{ev.timestamp}</span>
                     <span className="text-white block">{ev.module} :: {ev.event}</span>
                   </div>
                 ))
               )}
             </div>
          </div>
        </div>
      </div>
    </main>
  );
}
