"use client";
import { useEffect, useState } from "react";
import Navbar from "@/components/layout/Navbar";
import { Plane, Navigation, Wifi, Compass } from "lucide-react";
import { motion } from "framer-motion";

export default function Aerospace() {
  const [telemetry, setTelemetry] = useState({ alt: 42000, speed: 850, heading: 145 });

  useEffect(() => {
    const interval = setInterval(() => {
      setTelemetry(prev => ({
        alt: prev.alt + (Math.random() * 10 - 5),
        speed: prev.speed + (Math.random() * 4 - 2),
        heading: (prev.heading + (Math.random() * 2 - 1)) % 360
      }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen flex flex-col pt-24 px-12 relative bg-[#020206] overflow-hidden">
      <Navbar />
      
      {/* Background Grid */}
      <div className="absolute inset-0 z-0 opacity-10" style={{ backgroundImage: 'linear-gradient(#00a2e8 1px, transparent 1px), linear-gradient(90deg, #00a2e8 1px, transparent 1px)', backgroundSize: '50px 50px' }} />

      <div className="max-w-7xl mx-auto w-full z-10 relative">
        <h1 className="font-mono text-2xl text-white mb-8 border-b border-white/10 pb-4 flex items-center gap-3">
          <Plane className="text-sx-cyan" />
          Aerospace Telemetry Link
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 h-[600px]">
          {/* Main Map Simulation */}
          <div className="md:col-span-8 border border-sx-cyan/20 bg-black/60 backdrop-blur-md relative overflow-hidden flex items-center justify-center group">
            <div className="absolute top-0 left-0 w-full h-1 bg-sx-cyan scale-x-0 group-hover:scale-x-100 transition-transform origin-left" />
            
            <motion.div 
              animate={{ rotate: telemetry.heading }} 
              transition={{ ease: "linear", duration: 1 }}
              className="relative w-48 h-48 rounded-full border-2 border-sx-cyan/30 flex items-center justify-center before:absolute before:inset-0 before:border-t-2 before:border-sx-cyan before:rounded-full before:animate-spin"
            >
              <Navigation className="w-12 h-12 text-white absolute transform -translate-y-2" />
              <div className="absolute w-full h-[1px] bg-sx-cyan/20" />
              <div className="absolute h-full w-[1px] bg-sx-cyan/20" />
            </motion.div>

            <div className="absolute bottom-4 left-4 font-mono text-[10px] text-sx-cyan uppercase tracking-widest bg-black/50 p-2 border border-sx-cyan/20">
              Live Satellite Feed [Simulated]
            </div>
          </div>

          {/* Telemetry Stats */}
          <div className="md:col-span-4 flex flex-col gap-6">
            <div className="border border-white/10 bg-white/5 p-6 backdrop-blur-md flex-1">
              <h3 className="font-mono text-xs text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2 border-b border-white/10 pb-3">
                <Wifi className="w-4 h-4 text-[#76b900]" /> Uplink Status
              </h3>
              
              <div className="space-y-6">
                <div>
                  <span className="block font-mono text-[10px] text-slate-500 uppercase tracking-widest mb-1">Altitude (ft)</span>
                  <span className="font-mono text-3xl text-white">{telemetry.alt.toFixed(0)}</span>
                </div>
                <div>
                  <span className="block font-mono text-[10px] text-slate-500 uppercase tracking-widest mb-1">Airspeed (kts)</span>
                  <span className="font-mono text-3xl text-white">{telemetry.speed.toFixed(0)}</span>
                </div>
                <div>
                  <span className="block font-mono text-[10px] text-slate-500 uppercase tracking-widest mb-1">Heading (deg)</span>
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-3xl text-white">{telemetry.heading.toFixed(1)}°</span>
                    <Compass className="w-5 h-5 text-sx-cyan" />
                  </div>
                </div>
              </div>
            </div>

            <div className="border border-white/10 bg-white/5 p-6 backdrop-blur-md flex-none h-32 flex items-center justify-center">
               <button className="font-mono text-[10px] tracking-[0.18em] uppercase text-white bg-red-600/20 py-4 px-11 font-bold border border-red-600/50 hover:bg-red-600/40 transition-colors w-full">
                ABORT MISSION
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
