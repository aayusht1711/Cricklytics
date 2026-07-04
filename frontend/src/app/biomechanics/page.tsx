"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, Activity, Focus, Zap, Scan, Hexagon, Crosshair } from "lucide-react";
import Navbar from "@/components/Navbar";

export default function BiomechanicsRoom() {
  const [telemetry, setTelemetry] = useState({
    batSpeed: 0,
    elbowAngle: 0,
    strideLength: 0,
    headStability: 100
  });

  // Simulate real-time fluctuating telemetry data
  useEffect(() => {
    const interval = setInterval(() => {
      setTelemetry({
        batSpeed: 135 + Math.random() * 15, // 135-150 km/h
        elbowAngle: 12 + Math.random() * 5, // 12-17 degrees
        strideLength: 1.1 + Math.random() * 0.2, // 1.1-1.3 meters
        headStability: 95 + Math.random() * 4 // 95-99%
      });
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#050505] text-[#F5F0E6] font-sans pb-20 selection:bg-cyan-500/30">
      <Navbar />

      {/* Cyberpunk Grid Background */}
      <div className="fixed inset-0 z-0 pointer-events-none opacity-[0.03]" 
           style={{ backgroundImage: 'linear-gradient(#3b82f6 1px, transparent 1px), linear-gradient(90deg, #3b82f6 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
      </div>

      <div className="pt-32 px-8 max-w-[1600px] mx-auto relative z-10">
        
        {/* Lab Header */}
        <header className="mb-8 flex justify-between items-end border-b border-cyan-900/30 pb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Camera className="text-cyan-400" size={32} />
              <h1 className="text-3xl font-black tracking-tighter uppercase text-white">Biomechanics Lab</h1>
              <span className="bg-cyan-950 text-cyan-400 border border-cyan-500/30 text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-sm flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                LIVE FEED
              </span>
            </div>
            <p className="text-cyan-500/60 font-mono text-sm uppercase tracking-widest">Pose Estimation Engine v2.4 • Steve Smith Analysis</p>
          </div>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          
          {/* Main Video Analysis Feed - 8 cols */}
          <div className="xl:col-span-8">
            <div className="bg-black border border-cyan-900/50 rounded-2xl relative overflow-hidden group shadow-[0_0_30px_rgba(6,182,212,0.1)]">
              
              {/* Corner Brackets for UI feel */}
              <div className="absolute top-4 left-4 w-8 h-8 border-t-2 border-l-2 border-cyan-500/50 z-20"></div>
              <div className="absolute top-4 right-4 w-8 h-8 border-t-2 border-r-2 border-cyan-500/50 z-20"></div>
              <div className="absolute bottom-4 left-4 w-8 h-8 border-b-2 border-l-2 border-cyan-500/50 z-20"></div>
              <div className="absolute bottom-4 right-4 w-8 h-8 border-b-2 border-r-2 border-cyan-500/50 z-20"></div>

              {/* The Video */}
              <video 
                autoPlay 
                loop 
                muted 
                playsInline
                className="w-full h-full object-cover opacity-80 filter contrast-125 saturate-50"
              >
                <source src="/the_test_cricket.mp4" type="video/mp4" />
              </video>

              {/* Simulated AI Overlays */}
              <div className="absolute inset-0 z-10 pointer-events-none">
                
                {/* Scanning Line Animation */}
                <motion.div 
                  className="w-full h-1 bg-cyan-400/50 shadow-[0_0_15px_rgba(34,211,238,0.8)]"
                  animate={{ y: ["0%", "1000%", "0%"] }}
                  transition={{ duration: 4, ease: "linear", repeat: Infinity }}
                />

                {/* Mock Pose Skeleton overlay (Static CSS shapes floating over the batter's approximate position) */}
                <div className="absolute top-1/2 left-[55%] -translate-x-1/2 -translate-y-1/2 w-48 h-64 border border-red-500/30 bg-red-500/10 hidden md:block">
                  <div className="absolute top-2 left-1/2 w-8 h-8 border-2 border-cyan-400 rounded-full flex items-center justify-center">
                    <div className="w-1 h-1 bg-cyan-400 rounded-full"></div>
                  </div>
                  {/* Spine */}
                  <div className="absolute top-10 left-1/2 w-[2px] h-24 bg-cyan-400/80"></div>
                  {/* Shoulders */}
                  <div className="absolute top-12 left-1/4 w-1/2 h-[2px] bg-cyan-400/80"></div>
                  {/* Bat angle tracking line */}
                  <motion.div 
                    animate={{ rotate: [-20, 20, -20] }}
                    transition={{ duration: 0.8, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute top-20 right-[-20%] w-32 h-[2px] bg-yellow-400 origin-left"
                  >
                    <span className="absolute right-0 -top-6 text-[10px] text-yellow-400 font-mono bg-black/50 px-1 border border-yellow-400/30">TRACKING</span>
                  </motion.div>
                </div>

                {/* HUD Elements */}
                <div className="absolute top-8 left-8 flex items-center gap-2">
                  <Scan className="text-cyan-400 animate-spin-slow" size={24} />
                  <span className="text-cyan-400 font-mono text-xs font-bold uppercase tracking-widest bg-black/50 px-2 py-1 rounded">Target Acquired</span>
                </div>
                
                <div className="absolute bottom-8 right-8 text-right bg-black/50 p-2 border border-cyan-900/50 rounded">
                  <div className="text-[10px] text-cyan-500 font-mono mb-1 uppercase">Processor Load</div>
                  <div className="text-white font-mono text-sm">SYS.VOLT: 1.2V</div>
                  <div className="text-white font-mono text-sm">MEM: 14.2 GB / 32 GB</div>
                </div>
              </div>
            </div>
            
            {/* Playback Controls */}
            <div className="mt-4 flex items-center justify-between bg-black border border-cyan-900/30 p-4 rounded-xl">
              <div className="flex gap-2">
                {["0.25x", "0.5x", "1.0x", "AI Tracking"].map((btn, i) => (
                  <button key={i} className={`px-4 py-2 font-mono text-xs uppercase tracking-widest rounded transition-colors ${i === 3 ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}>
                    {btn}
                  </button>
                ))}
              </div>
              <div className="text-cyan-500 font-mono text-xs flex items-center gap-2">
                <Activity size={14} /> FRAME: <span className="text-white font-bold">142,084</span>
              </div>
            </div>
          </div>

          {/* Telemetry Dashboard - 4 cols */}
          <div className="xl:col-span-4 space-y-4">
            
            <div className="bg-black border border-cyan-900/30 p-6 rounded-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-600/10 blur-[50px]"></div>
              
              <h3 className="text-cyan-500 font-mono text-[10px] uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                <Hexagon size={12} /> Real-Time Telemetry
              </h3>

              <div className="space-y-6">
                
                {/* Bat Speed Metric */}
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-gray-400 text-xs font-bold uppercase tracking-wider">Max Bat Speed</span>
                    <span className="text-3xl font-black text-white font-mono">{telemetry.batSpeed.toFixed(1)} <span className="text-sm text-cyan-500">km/h</span></span>
                  </div>
                  <div className="h-1 w-full bg-gray-900 overflow-hidden">
                    <motion.div 
                      className="h-full bg-cyan-400"
                      animate={{ width: `${(telemetry.batSpeed / 160) * 100}%` }}
                      transition={{ type: "spring", bounce: 0 }}
                    />
                  </div>
                </div>

                {/* Elbow Angle */}
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-gray-400 text-xs font-bold uppercase tracking-wider">Elbow Extension</span>
                    <span className="text-3xl font-black text-white font-mono">{telemetry.elbowAngle.toFixed(1)} <span className="text-sm text-yellow-500">°</span></span>
                  </div>
                  <div className="h-1 w-full bg-gray-900 overflow-hidden">
                    <motion.div 
                      className="h-full bg-yellow-400"
                      animate={{ width: `${(telemetry.elbowAngle / 20) * 100}%` }}
                      transition={{ type: "spring", bounce: 0 }}
                    />
                  </div>
                </div>

                {/* Stride Length */}
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-gray-400 text-xs font-bold uppercase tracking-wider">Front Stride</span>
                    <span className="text-3xl font-black text-white font-mono">{telemetry.strideLength.toFixed(2)} <span className="text-sm text-green-500">m</span></span>
                  </div>
                  <div className="h-1 w-full bg-gray-900 overflow-hidden">
                    <motion.div 
                      className="h-full bg-green-400"
                      animate={{ width: `${(telemetry.strideLength / 1.5) * 100}%` }}
                      transition={{ type: "spring", bounce: 0 }}
                    />
                  </div>
                </div>

                {/* Head Stability */}
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-gray-400 text-xs font-bold uppercase tracking-wider">Head Stability</span>
                    <span className="text-3xl font-black text-white font-mono">{telemetry.headStability.toFixed(1)} <span className="text-sm text-purple-500">%</span></span>
                  </div>
                  <div className="h-1 w-full bg-gray-900 overflow-hidden">
                    <motion.div 
                      className="h-full bg-purple-400"
                      animate={{ width: `${telemetry.headStability}%` }}
                      transition={{ type: "spring", bounce: 0 }}
                    />
                  </div>
                </div>

              </div>
            </div>

            {/* AI Diagnosis Panel */}
            <div className="bg-black border border-red-900/50 p-6 rounded-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-red-600/10 blur-[50px]"></div>
              
              <h3 className="text-red-500 font-mono text-[10px] uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                <Crosshair size={12} /> Flaw Detection AI
              </h3>

              <div className="space-y-3">
                <div className="bg-red-500/10 border border-red-500/20 p-3 rounded-lg text-sm">
                  <p className="text-red-400 font-bold mb-1">Trigger Movement Late</p>
                  <p className="text-gray-400 text-xs">Back-and-across motion completing 0.12s after release. Vulnerable to 145+ km/h inswing.</p>
                </div>
                <div className="bg-yellow-500/10 border border-yellow-500/20 p-3 rounded-lg text-sm">
                  <p className="text-yellow-400 font-bold mb-1">Bottom Hand Dominance</p>
                  <p className="text-gray-400 text-xs">Bat face closing early on off-drive attempts (14% deviation from optimal plane).</p>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
