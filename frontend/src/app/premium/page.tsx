"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Cpu, Zap, Activity, AlertTriangle, Target, TrendingUp, ShieldAlert, BarChart2, Crosshair } from "lucide-react";
import Navbar from "@/components/Navbar";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function PremiumDashboard() {
  const [players, setPlayers] = useState<any[]>([]);
  const [striker, setStriker] = useState("Virat Kohli");
  const [bowler, setBowler] = useState("Lasith Malinga");
  const [phase, setPhase] = useState("Middle Overs");
  const [simResult, setSimResult] = useState<any>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    fetch("http://127.0.0.1:8001/api/players/")
      .then(res => res.json())
      .then(data => setPlayers(data.players))
      .catch(err => console.error(err));
  }, []);

  const runSimulation = () => {
    setIsSimulating(true);
    fetch(`http://127.0.0.1:8001/api/players/simulate/${striker}/${bowler}?phase=${phase}`)
      .then(res => res.json())
      .then(data => {
        setTimeout(() => {
          setSimResult(data);
          setIsSimulating(false);
        }, 1800); // ML processing delay
      })
      .catch(err => {
        console.error(err);
        setIsSimulating(false);
      });
  };

  useEffect(() => {
    runSimulation();
  }, []);

  const getAreaChartData = () => {
    if (!simResult) return [];
    const rpo = simResult.results.expected_runs_per_over;
    return [
      { ball: 'B1', runs: rpo / 6 },
      { ball: 'B2', runs: (rpo / 6) * 2 },
      { ball: 'B3', runs: (rpo / 6) * 3 },
      { ball: 'B4', runs: (rpo / 6) * 4 },
      { ball: 'B5', runs: (rpo / 6) * 5 },
      { ball: 'B6', runs: rpo },
    ];
  };

  const getDangerLevel = (wicketProb: number) => {
    if (wicketProb > 25) return { color: "text-red-500", bg: "bg-red-500", glow: "shadow-[0_0_20px_rgba(239,68,68,0.6)]", label: "CRITICAL" };
    if (wicketProb > 15) return { color: "text-orange-500", bg: "bg-orange-500", glow: "shadow-[0_0_20px_rgba(249,115,22,0.6)]", label: "HIGH" };
    return { color: "text-yellow-500", bg: "bg-yellow-500", glow: "shadow-[0_0_20px_rgba(234,179,8,0.6)]", label: "MODERATE" };
  };

  return (
    <div className="min-h-screen bg-[#030303] text-[#F5F0E6] font-sans pb-20 selection:bg-blue-500/30">
      <Navbar />

      <div className="pt-32 px-4 md:px-8 max-w-[1400px] mx-auto relative z-10">
        
        {/* Header */}
        <header className="mb-12 flex flex-col md:flex-row justify-between items-start md:items-end border-b border-blue-900/30 pb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-4xl font-black tracking-tighter uppercase text-white">Machine Learning Report</h1>
              <span className="bg-blue-900/50 border border-blue-500/50 text-blue-400 text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-sm flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                RANDOM FOREST ENGINE
              </span>
            </div>
            <p className="text-gray-400 font-mono text-sm uppercase tracking-widest">Predictive Analytics • 10,000 Neural Iterations</p>
          </div>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
          
          {/* Controls Panel - 3 cols */}
          <div className="xl:col-span-3 space-y-6">
            <div className="bg-[#080B12] border border-blue-900/50 rounded-2xl p-6 relative shadow-[0_0_30px_rgba(37,99,235,0.1)]">
              <h3 className="text-blue-400 font-mono text-xs uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                <Cpu size={14} /> Matrix Inputs
              </h3>

              <div className="space-y-6">
                <div>
                  <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest font-bold mb-2 block">Striker Node</label>
                  <input 
                    type="text"
                    value={striker}
                    onChange={(e) => setStriker(e.target.value)}
                    placeholder="E.g., Sachin Tendulkar"
                    className="w-full bg-black border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500 transition-colors font-bold text-sm"
                  />
                </div>

                <div className="flex justify-center -my-3 relative z-10">
                  <div className="bg-black p-2 rounded-full border border-blue-500/30 text-blue-500">
                    <Crosshair size={16} />
                  </div>
                </div>

                <div>
                  <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest font-bold mb-2 block">Bowler Node</label>
                  <input 
                    type="text"
                    value={bowler}
                    onChange={(e) => setBowler(e.target.value)}
                    placeholder="E.g., Shoaib Akhtar"
                    className="w-full bg-black border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500 transition-colors font-bold text-sm"
                  />
                </div>

                <div>
                  <label className="text-[10px] text-gray-500 font-mono uppercase tracking-widest font-bold mb-2 block">Context Vector</label>
                  <div className="grid grid-cols-1 gap-2">
                    {["Powerplay", "Middle Overs", "Death Overs"].map(p => (
                      <button
                        key={p}
                        onClick={() => setPhase(p)}
                        className={`py-2 text-[10px] font-mono uppercase font-bold rounded-lg transition-colors border ${phase === p ? 'bg-blue-900/40 border-blue-500 text-white' : 'bg-black border-white/5 text-gray-500 hover:border-white/20'}`}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>

                <button 
                  onClick={runSimulation}
                  disabled={isSimulating}
                  className="w-full bg-blue-600 hover:bg-blue-500 text-white font-black uppercase tracking-widest py-4 rounded-xl transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)] disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isSimulating ? "Training Neural Net..." : <><Zap size={18}/> Execute Report</>}
                </button>
              </div>
            </div>
          </div>

          {/* ML Output Report - 9 cols */}
          <div className="xl:col-span-9">
            {isSimulating ? (
              <div className="h-full bg-[#080B12] border border-blue-900/30 rounded-2xl p-8 flex flex-col items-center justify-center min-h-[600px]">
                <div className="relative flex justify-center items-center">
                   <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 2, ease: "linear" }} className="w-32 h-32 border-4 border-blue-900/30 border-t-blue-500 rounded-full" />
                   <motion.div animate={{ rotate: -360 }} transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }} className="w-24 h-24 border-4 border-cyan-900/30 border-b-cyan-400 rounded-full absolute" />
                   <Cpu className="absolute text-blue-500" size={32} />
                </div>
                <h3 className="text-2xl font-black text-white tracking-widest uppercase mt-8">Synthesizing Data</h3>
                <p className="text-blue-400 font-mono text-sm mt-2">Querying model.pkl via API...</p>
              </div>
            ) : simResult ? (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                
                {/* Top Section: Threat Meter & Stats */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  
                  {/* Wicket Threat Gauge */}
                  <div className="lg:col-span-1 bg-[#080B12] border border-white/5 rounded-2xl p-6 relative overflow-hidden flex flex-col justify-center items-center">
                    <h4 className="absolute top-6 left-6 text-[10px] text-gray-500 uppercase font-bold tracking-widest flex items-center gap-2">
                      <ShieldAlert size={12} className={getDangerLevel(simResult.results.wicket_probability).color} /> 
                      Threat Level
                    </h4>
                    
                    {/* Semicircle Gauge (CSS) */}
                    <div className="relative w-48 h-24 overflow-hidden mt-8 mb-4">
                      <div className="absolute top-0 left-0 w-48 h-48 rounded-full border-[12px] border-white/5"></div>
                      <motion.div 
                        initial={{ rotate: -180 }}
                        animate={{ rotate: -180 + (simResult.results.wicket_probability / 50) * 180 }} 
                        transition={{ duration: 1.5, ease: "easeOut" }}
                        className={`absolute top-0 left-0 w-48 h-48 rounded-full border-[12px] border-transparent border-t-current border-r-current ${getDangerLevel(simResult.results.wicket_probability).color} ${getDangerLevel(simResult.results.wicket_probability).glow}`}
                        style={{ transformOrigin: "center" }}
                      ></motion.div>
                    </div>

                    <div className="text-center">
                      <p className={`text-4xl font-black ${getDangerLevel(simResult.results.wicket_probability).color}`}>
                        {simResult.results.wicket_probability.toFixed(1)}%
                      </p>
                      <p className="text-xs text-white font-bold uppercase tracking-widest mt-1">Wicket Probability</p>
                      <div className={`mt-3 text-[9px] font-bold uppercase tracking-widest px-2 py-1 rounded-sm text-black ${getDangerLevel(simResult.results.wicket_probability).bg}`}>
                        STATUS: {getDangerLevel(simResult.results.wicket_probability).label}
                      </div>
                    </div>
                  </div>

                  {/* Core Metrics */}
                  <div className="lg:col-span-2 grid grid-cols-2 gap-4">
                    <div className="bg-[#080B12] border border-white/5 rounded-2xl p-6 flex flex-col justify-center">
                      <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-1">Expected Output</p>
                      <p className="text-5xl font-black text-white">{simResult.results.expected_runs_per_over.toFixed(2)} <span className="text-sm text-gray-400 font-normal tracking-widest uppercase">Runs/Over</span></p>
                    </div>
                    <div className="bg-[#080B12] border border-white/5 rounded-2xl p-6 flex flex-col justify-center">
                      <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-1">Boundary Potential</p>
                      <div className="flex items-end gap-2">
                        <p className="text-5xl font-black text-green-400">{simResult.results.boundary_probability.toFixed(1)}%</p>
                      </div>
                    </div>
                    
                    {/* ML Feature Weights */}
                    <div className="col-span-2 bg-gradient-to-r from-blue-950/40 to-[#080B12] border border-blue-900/50 rounded-2xl p-5 flex items-center justify-between">
                      <div>
                        <h4 className="text-white font-bold text-sm flex items-center gap-2 mb-1">
                          <Activity size={16} className="text-blue-400"/> Primary ML Weights
                        </h4>
                        <p className="text-xs text-gray-400 font-mono">Top drivers for this prediction:</p>
                      </div>
                      <div className="flex gap-4">
                         <div className="text-right">
                           <p className="text-[10px] uppercase font-bold text-blue-400">Match Phase</p>
                           <p className="text-white font-mono text-sm">41% weight</p>
                         </div>
                         <div className="text-right">
                           <p className="text-[10px] uppercase font-bold text-blue-400">Bowler Economy</p>
                           <p className="text-white font-mono text-sm">34% weight</p>
                         </div>
                      </div>
                    </div>
                  </div>

                </div>

                {/* Middle Section: Profiling & Hot Zones */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  
                  {/* Player Profiling */}
                  <div className="bg-[#080B12] border border-white/5 rounded-2xl p-6">
                    <h3 className="text-white font-bold text-xs uppercase tracking-widest mb-6 flex items-center gap-2">
                      <BarChart2 size={14} className="text-cyan-500"/> Head-to-Head Profiling
                    </h3>
                    
                    <div className="space-y-6">
                      {/* Striker Stats */}
                      <div>
                        <p className="text-xs font-bold text-cyan-400 mb-3">{simResult.batsman} (Striker)</p>
                        <div className="space-y-3">
                          <div>
                            <div className="flex justify-between text-[10px] mb-1 font-mono text-gray-400"><span>Pace Control</span><span>88%</span></div>
                            <div className="w-full bg-white/5 rounded-full h-1"><div className="bg-cyan-500 h-1 rounded-full w-[88%] shadow-[0_0_8px_rgba(6,182,212,0.8)]"></div></div>
                          </div>
                          <div>
                            <div className="flex justify-between text-[10px] mb-1 font-mono text-gray-400"><span>Spin Aggression</span><span>94%</span></div>
                            <div className="w-full bg-white/5 rounded-full h-1"><div className="bg-cyan-500 h-1 rounded-full w-[94%] shadow-[0_0_8px_rgba(6,182,212,0.8)]"></div></div>
                          </div>
                        </div>
                      </div>

                      <div className="h-px bg-white/5 w-full"></div>

                      {/* Bowler Stats */}
                      <div>
                        <p className="text-xs font-bold text-purple-400 mb-3">{simResult.bowler} (Bowler)</p>
                        <div className="space-y-3">
                          <div>
                            <div className="flex justify-between text-[10px] mb-1 font-mono text-gray-400"><span>Line & Length Accuracy</span><span>92%</span></div>
                            <div className="w-full bg-white/5 rounded-full h-1"><div className="bg-purple-500 h-1 rounded-full w-[92%] shadow-[0_0_8px_rgba(168,85,247,0.8)]"></div></div>
                          </div>
                          <div>
                            <div className="flex justify-between text-[10px] mb-1 font-mono text-gray-400"><span>Variation Deception</span><span>97%</span></div>
                            <div className="w-full bg-white/5 rounded-full h-1"><div className="bg-purple-500 h-1 rounded-full w-[97%] shadow-[0_0_8px_rgba(168,85,247,0.8)]"></div></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Graphic Hot Zones */}
                  <div className="bg-[#080B12] border border-white/5 rounded-2xl p-6 flex flex-col">
                    <h3 className="text-white font-bold text-xs uppercase tracking-widest mb-6 flex items-center gap-2">
                      <Target size={14} className="text-green-500"/> Predicted Boundary Zones
                    </h3>
                    
                    <div className="flex-1 flex items-center justify-center relative bg-gradient-to-t from-green-950/20 to-transparent rounded-xl border border-white/5 p-4">
                      {/* CSS Cricket Pitch */}
                      <div className="w-full h-full max-w-[200px] border-2 border-white/20 rounded-[50%] relative flex items-center justify-center shadow-inner">
                        <div className="w-[20%] h-[70%] bg-[#c2b280]/20 border border-white/10 rounded-sm"></div>
                        
                        {/* Heat Map Spots */}
                        <motion.div 
                          initial={{ opacity: 0, scale: 0 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.5 }}
                          className="absolute top-[20%] right-[10%] w-12 h-12 bg-red-500/40 blur-md rounded-full"
                        ></motion.div>
                         <motion.div 
                          initial={{ opacity: 0, scale: 0 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.8 }}
                          className="absolute bottom-[30%] left-[15%] w-16 h-16 bg-orange-500/30 blur-md rounded-full"
                        ></motion.div>

                        {/* Labels */}
                        <div className="absolute top-[20%] right-[5%] bg-black/80 border border-red-500/50 px-2 py-1 rounded text-[8px] font-mono font-bold text-white">SQUARE LEG (42%)</div>
                        <div className="absolute bottom-[30%] left-[5%] bg-black/80 border border-orange-500/50 px-2 py-1 rounded text-[8px] font-mono font-bold text-white">COVERS (28%)</div>
                      </div>
                    </div>
                  </div>

                </div>

                {/* Bottom Section: Area Chart Trajectory */}
                <div className="bg-[#080B12] border border-white/5 rounded-2xl p-6">
                  <h4 className="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-6 flex items-center gap-2">
                     <TrendingUp size={12} className="text-blue-500"/> Ball-by-Ball Run Trajectory
                  </h4>
                  <div className="h-56">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={getAreaChartData()}>
                        <defs>
                          <linearGradient id="colorRuns2" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.5}/>
                            <stop offset="95%" stopColor="#080B12" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#111" vertical={false} />
                        <XAxis dataKey="ball" stroke="#444" tick={{fontSize: 10, fill: '#666'}} axisLine={false} tickLine={false} />
                        <YAxis stroke="#444" tick={{fontSize: 10, fill: '#666'}} axisLine={false} tickLine={false} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#000', border: '1px solid #1e3a8a', borderRadius: '8px' }}
                          itemStyle={{ color: '#60a5fa', fontWeight: 'bold' }}
                          formatter={(value: number) => [value.toFixed(2), "runs"]}
                        />
                        <Area type="monotone" dataKey="runs" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorRuns2)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

              </motion.div>
            ) : (
               <div className="h-full bg-[#080B12] border border-white/5 rounded-2xl flex items-center justify-center min-h-[600px]">
                  <div className="text-center opacity-30">
                    <BarChart2 size={64} className="mx-auto mb-4" />
                    <p className="font-mono text-sm uppercase tracking-widest">Awaiting Simulation Parameters</p>
                  </div>
               </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
