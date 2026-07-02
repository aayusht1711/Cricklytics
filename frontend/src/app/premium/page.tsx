"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Activity, Cpu, Crosshair, TrendingUp, Zap, Target, AlertTriangle } from "lucide-react";

export default function PremiumDashboard() {
  return (
    <div className="min-h-screen bg-[#020202] text-[#F5F0E6] font-sans pt-24 pb-20 px-8">
      <div className="max-w-[1600px] mx-auto">
        
        {/* Premium Header */}
        <header className="mb-12 flex justify-between items-end border-b border-blue-900/30 pb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-4xl font-black tracking-tighter">Premium Scouting</h1>
              <span className="bg-gradient-to-r from-blue-600 to-cyan-500 text-white text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-full shadow-[0_0_15px_rgba(59,130,246,0.5)]">
                PRO
              </span>
            </div>
            <p className="text-gray-400 font-light text-lg">AI-Powered Predictive Analytics • Live Match Engine v4.2</p>
          </div>
          <div className="flex items-center gap-2 bg-blue-950/30 border border-blue-500/20 px-4 py-2 rounded-full">
            <Cpu size={16} className="text-blue-400 animate-pulse" />
            <span className="text-blue-300 text-xs font-bold uppercase tracking-widest">Model Online</span>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Main ML Prediction Engine - 8 cols */}
          <div className="lg:col-span-8 space-y-8">
            
            <div className="bg-[#050B14] border border-blue-500/20 rounded-3xl p-10 relative overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.8)]">
              <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600 opacity-10 blur-[100px] rounded-full"></div>
              
              <h3 className="text-blue-400 font-bold uppercase tracking-[0.2em] text-xs mb-8 flex items-center gap-2">
                <Zap size={14} /> Win Probability Engine
              </h3>
              
              <div className="flex justify-between items-end mb-4">
                <div>
                  <p className="text-6xl font-black text-white">68.4%</p>
                  <p className="text-gray-400 mt-2">Los Angeles Knight Riders</p>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-black text-gray-500">31.6%</p>
                  <p className="text-gray-500 mt-2">Washington Freedom</p>
                </div>
              </div>
              
              <div className="w-full bg-gray-900 rounded-full h-3 mt-6 flex overflow-hidden border border-white/5">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: "68.4%" }}
                  transition={{ duration: 1.5, ease: "easeOut" }}
                  className="bg-gradient-to-r from-blue-600 to-cyan-400 h-full"
                />
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: "31.6%" }}
                  transition={{ duration: 1.5, ease: "easeOut" }}
                  className="bg-gray-800 h-full"
                />
              </div>

              <div className="grid grid-cols-3 gap-6 mt-10 border-t border-blue-900/30 pt-8">
                <div>
                  <p className="text-gray-500 text-xs uppercase tracking-widest mb-2 font-bold">Key Driver</p>
                  <p className="text-blue-300 font-medium">Top Order Collapse (WAF)</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs uppercase tracking-widest mb-2 font-bold">Projected Score</p>
                  <p className="text-white font-black text-xl">185 - 192</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs uppercase tracking-widest mb-2 font-bold">Confidence</p>
                  <p className="text-green-400 font-bold flex items-center gap-1"><TrendingUp size={14} /> High (92%)</p>
                </div>
              </div>
            </div>

            {/* AI Commentary */}
            <div className="bg-[#050505] border border-white/10 rounded-3xl p-8">
              <h3 className="text-gray-400 font-bold uppercase tracking-[0.2em] text-xs mb-6">AI Strategic Insights</h3>
              <div className="space-y-4">
                <div className="bg-white/5 p-4 rounded-xl border border-white/5 flex gap-4">
                  <div className="bg-yellow-500/20 p-3 rounded-lg h-fit">
                    <AlertTriangle size={20} className="text-yellow-500" />
                  </div>
                  <div>
                    <h4 className="text-white font-bold mb-1">Spin Vulnerability Detected</h4>
                    <p className="text-sm text-gray-400 leading-relaxed">Washington Freedom's middle order is currently showing a 42% higher false-shot percentage against left-arm orthodox compared to their tournament average. Recommending immediate introduction of spin.</p>
                  </div>
                </div>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5 flex gap-4 opacity-70">
                  <div className="bg-blue-500/20 p-3 rounded-lg h-fit">
                    <Crosshair size={20} className="text-blue-400" />
                  </div>
                  <div>
                    <h4 className="text-white font-bold mb-1">Pacing Optimal</h4>
                    <p className="text-sm text-gray-400 leading-relaxed">LAKR is currently tracking 12 runs ahead of the par score for this venue at this stage. Risk-taking should be minimized until the 16th over.</p>
                  </div>
                </div>
              </div>
            </div>
            
          </div>

          {/* Player Profiling - 4 cols */}
          <div className="lg:col-span-4 space-y-8">
            
            <div className="bg-gradient-to-b from-[#0A1128] to-black border border-blue-500/20 rounded-3xl p-8 relative overflow-hidden">
              <h3 className="text-blue-400 font-bold uppercase tracking-[0.2em] text-xs mb-8 flex items-center gap-2">
                <Target size={14} /> Striker Profiling
              </h3>

              <div className="flex items-center gap-4 mb-8">
                <div className="w-16 h-16 bg-blue-900/50 rounded-full flex items-center justify-center border-2 border-blue-400">
                  <span className="text-2xl font-black text-white">AD</span>
                </div>
                <div>
                  <h4 className="text-2xl font-black text-white">A. Russell</h4>
                  <p className="text-blue-300 text-sm font-medium">Aggressive Finisher</p>
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-xs mb-2 font-bold uppercase tracking-wider">
                    <span className="text-gray-400">Pace Hitting</span>
                    <span className="text-white">94 / 100</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-1.5">
                    <div className="bg-gradient-to-r from-blue-600 to-cyan-400 h-1.5 rounded-full w-[94%] shadow-[0_0_10px_rgba(59,130,246,0.8)]"></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-2 font-bold uppercase tracking-wider">
                    <span className="text-gray-400">Spin Rotation</span>
                    <span className="text-white">62 / 100</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-1.5">
                    <div className="bg-blue-600 h-1.5 rounded-full w-[62%]"></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-2 font-bold uppercase tracking-wider">
                    <span className="text-gray-400">Death Overs Impact</span>
                    <span className="text-white">98 / 100</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-1.5">
                    <div className="bg-gradient-to-r from-blue-600 to-cyan-400 h-1.5 rounded-full w-[98%] shadow-[0_0_10px_rgba(59,130,246,0.8)]"></div>
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-blue-900/30">
                <p className="text-gray-500 text-xs uppercase tracking-widest mb-3 font-bold">Hot Zones</p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-white/5 rounded-lg p-3 text-center border border-white/5">
                    <p className="text-white font-bold">Deep Mid Wicket</p>
                    <p className="text-xs text-gray-400 mt-1">42% of boundaries</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3 text-center border border-white/5">
                    <p className="text-white font-bold">Long On</p>
                    <p className="text-xs text-gray-400 mt-1">28% of boundaries</p>
                  </div>
                </div>
              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  );
}
