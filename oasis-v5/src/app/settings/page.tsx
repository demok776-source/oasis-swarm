"use client";
import { useState, useEffect } from "react";
import Navbar from "@/components/layout/Navbar";
import { Settings as SettingsIcon, Key, Zap, Shield, Save } from "lucide-react";
import { useStore } from "@/store/useStore";
import { motion } from "framer-motion";

export default function Settings() {
  const { apiKey, setApiKey, simulationMode, setSimulationMode } = useStore();
  const [localKey, setLocalKey] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setLocalKey(apiKey);
  }, [apiKey]);

  const handleSave = () => {
    setApiKey(localKey);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <main className="min-h-screen flex flex-col pt-24 px-12 relative bg-[#020206]">
      <Navbar />
      <div className="max-w-4xl mx-auto w-full z-10 relative">
        <h1 className="font-mono text-2xl text-white mb-8 border-b border-white/10 pb-4 flex items-center gap-3">
          <SettingsIcon className="text-[#00a2e8]" />
          System Configuration
        </h1>

        <div className="grid grid-cols-1 gap-6">
          {/* API Configuration */}
          <div className="border border-white/10 bg-white/5 p-8 backdrop-blur-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-[#00a2e8] scale-y-0 group-hover:scale-y-100 transition-transform origin-top" />
            
            <h3 className="font-mono text-sm text-white uppercase tracking-widest mb-6 flex items-center gap-3">
              <Key className="w-5 h-5 text-[#00a2e8]" /> Neural Net Authentication
            </h3>
            
            <div className="space-y-6">
              <div>
                <label className="block font-mono text-xs text-slate-400 uppercase tracking-widest mb-2">
                  OpenAI API Key
                </label>
                <div className="flex gap-4">
                  <input
                    type="password"
                    value={localKey}
                    onChange={(e) => setLocalKey(e.target.value)}
                    placeholder="sk-..."
                    className="flex-1 bg-black/50 border border-white/10 text-white font-mono text-sm px-4 py-3 focus:outline-none focus:border-[#00a2e8] transition-colors"
                  />
                  <button
                    onClick={handleSave}
                    className="flex items-center gap-2 font-mono text-xs uppercase tracking-widest bg-[#00a2e8]/20 text-[#00a2e8] px-6 py-3 hover:bg-[#00a2e8]/40 transition-colors border border-[#00a2e8]/50"
                  >
                    <Save className="w-4 h-4" /> {saved ? "Saved" : "Save"}
                  </button>
                </div>
                <p className="font-mono text-[10px] text-slate-500 mt-2 flex items-center gap-1">
                  <Shield className="w-3 h-3" /> Key is stored locally in your browser and sent only to the App-Tier.
                </p>
              </div>

              <div className="pt-6 border-t border-white/10">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="block font-mono text-sm text-white uppercase tracking-widest mb-1">
                      Simulation Mode
                    </label>
                    <p className="font-mono text-[10px] text-slate-500">
                      When active, JARVIS operates in a local sandbox without making external API calls.
                    </p>
                  </div>
                  <button
                    onClick={() => setSimulationMode(!simulationMode)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${simulationMode ? 'bg-[#76b900]' : 'bg-slate-700'}`}
                  >
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${simulationMode ? 'translate-x-6' : 'translate-x-1'}`} />
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          {/* System Status Panel */}
          <div className="border border-white/10 bg-white/5 p-8 backdrop-blur-md relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500 scale-y-0 group-hover:scale-y-100 transition-transform origin-top" />
            <h3 className="font-mono text-sm text-white uppercase tracking-widest mb-6 flex items-center gap-3">
              <Zap className="w-5 h-5 text-indigo-500" /> Module Status
            </h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {['App-Tier', 'Memory Fabric', 'Aerospace Node', 'Jarvis Agent'].map((module, i) => (
                <div key={module} className="bg-black/30 p-4 border border-white/5 flex flex-col items-center justify-center text-center">
                  <div className={`w-2 h-2 rounded-full mb-3 shadow-[0_0_8px] ${i === 3 && simulationMode ? 'bg-yellow-500 shadow-yellow-500/50' : 'bg-[#76b900] shadow-[#76b900/50]'}`} />
                  <span className="font-mono text-[10px] uppercase text-slate-400 tracking-wider">{module}</span>
                  <span className="font-mono text-xs text-white font-bold mt-1">
                    {i === 3 && simulationMode ? 'SANDBOX' : 'ONLINE'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
