"use client";
import { motion } from "framer-motion";
import { useState } from "react";

export default function MediaStudioPage() {
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const [response, setResponse] = useState("");

  const handleGenerate = async () => {
    setIsGenerating(true);
    setResponse("");
    try {
      const res = await fetch("http://localhost:8081/ai/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: prompt, module: "Media-Studio" }),
      });
      const data = await res.json();
      setResponse(data.response || data.detail || "Generation complete.");
    } catch (err) {
      setResponse("ERROR: CONNECTION REFUSED OR BLOCKED.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="pt-[100px] px-12 max-w-[1400px] mx-auto min-h-screen text-slate-300">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-12"
      >
        <h1 className="text-4xl font-bold tracking-tight text-white mb-2 font-mono">
          MEDIA <span className="text-sx-cyan">STUDIO</span>
        </h1>
        <p className="text-slate-500 font-mono text-xs uppercase tracking-widest">
          AI Diffusion Matrix // Modules 10 & 11
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Control Panel */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-1 border border-white/5 bg-[#020206]/50 p-6 backdrop-blur-sm"
        >
          <div className="space-y-6">
            <div>
              <label className="block font-mono text-[10px] text-sx-cyan uppercase tracking-widest mb-3">
                Generation Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the visual or simulation environment..."
                className="w-full bg-white/5 border border-white/10 p-4 font-mono text-sm h-32 focus:outline-none focus:border-sx-cyan/50 transition-colors resize-none"
              />
            </div>

            <div>
              <label className="block font-mono text-[10px] text-sx-cyan uppercase tracking-widest mb-3">
                Reference Matrix (Drag & Drop)
              </label>
              <div className="border-2 border-dashed border-white/10 h-32 flex items-center justify-center hover:border-white/20 transition-colors cursor-pointer group">
                <span className="font-mono text-xs text-slate-500 group-hover:text-slate-400">
                  + Upload Reference Image
                </span>
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt}
              className="w-full bg-gradient-to-r from-sx-cyan to-indigo-500 text-black font-bold font-mono text-xs uppercase tracking-widest py-4 hover:opacity-90 disabled:opacity-50 transition-opacity"
            >
              {isGenerating ? "Synthesizing..." : "Initialize Diffusion"}
            </button>
          </div>
        </motion.div>

        {/* Output Viewport */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2 border border-white/5 bg-black/40 min-h-[600px] relative overflow-hidden flex items-center justify-center"
        >
          {isGenerating ? (
            <div className="flex flex-col items-center gap-6">
              <div className="w-16 h-16 border-4 border-sx-cyan/20 border-t-sx-cyan rounded-full animate-spin" />
              <div className="font-mono text-xs text-sx-cyan animate-pulse tracking-widest">
                PROCESSING NEURAL NETWORKS...
              </div>
            </div>
          ) : response ? (
            <div className="font-mono text-xs text-sx-cyan tracking-widest uppercase p-12 text-center whitespace-pre-wrap max-w-full overflow-y-auto max-h-[500px]">
              {response}
            </div>
          ) : (
            <div className="font-mono text-xs text-slate-600 tracking-widest uppercase">
              [ Viewport Awaiting Data ]
            </div>
          )}

          {/* Grid Overlay */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />
        </motion.div>
      </div>
    </div>
  );
}
