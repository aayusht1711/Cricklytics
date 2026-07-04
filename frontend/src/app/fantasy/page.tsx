"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Cpu, Zap, Star, Shield, Target, Award, Play } from "lucide-react";
import Navbar from "@/components/Navbar";

// Mock Perfect XI Data
const FANTASY_XI = [
  { id: "1", name: "Rishabh Pant", role: "WK", team: "IND", points: 84.5, isCaptain: false, isViceCaptain: false },
  { id: "2", name: "Virat Kohli", role: "BAT", team: "IND", points: 112.0, isCaptain: false, isViceCaptain: true },
  { id: "3", name: "Steve Smith", role: "BAT", team: "AUS", points: 94.0, isCaptain: false, isViceCaptain: false },
  { id: "4", name: "Rohit Sharma", role: "BAT", team: "IND", points: 88.5, isCaptain: false, isViceCaptain: false },
  { id: "5", name: "Travis Head", role: "BAT", team: "AUS", points: 76.0, isCaptain: false, isViceCaptain: false },
  { id: "6", name: "Hardik Pandya", role: "AR", team: "IND", points: 145.5, isCaptain: true, isViceCaptain: false },
  { id: "7", name: "Glenn Maxwell", role: "AR", team: "AUS", points: 92.0, isCaptain: false, isViceCaptain: false },
  { id: "8", name: "Pat Cummins", role: "BOWL", team: "AUS", points: 81.5, isCaptain: false, isViceCaptain: false },
  { id: "9", name: "Jasprit Bumrah", role: "BOWL", team: "IND", points: 104.0, isCaptain: false, isViceCaptain: false },
  { id: "10", name: "Mitchell Starc", role: "BOWL", team: "AUS", points: 79.0, isCaptain: false, isViceCaptain: false },
  { id: "11", name: "Kuldeep Yadav", role: "BOWL", team: "IND", points: 72.5, isCaptain: false, isViceCaptain: false },
];

export default function FantasyOptimizer() {
  const [team1, setTeam1] = useState("IND");
  const [team2, setTeam2] = useState("AUS");
  const [isGenerating, setIsGenerating] = useState(false);
  const [showTeam, setShowTeam] = useState(false);

  const handleGenerate = () => {
    setIsGenerating(true);
    setShowTeam(false);
    setTimeout(() => {
      setIsGenerating(false);
      setShowTeam(true);
    }, 2500); // 2.5s dramatic calculation
  };

  const wk = FANTASY_XI.filter(p => p.role === "WK");
  const bats = FANTASY_XI.filter(p => p.role === "BAT");
  const ars = FANTASY_XI.filter(p => p.role === "AR");
  const bowls = FANTASY_XI.filter(p => p.role === "BOWL");

  const totalProjected = FANTASY_XI.reduce((acc, curr) => acc + curr.points, 0);

  const PlayerNode = ({ player }: { player: any }) => (
    <motion.div 
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="flex flex-col items-center relative"
    >
      <div className={`w-12 h-12 md:w-16 md:h-16 rounded-full border-2 flex items-center justify-center font-bold text-xs md:text-sm bg-black/80 backdrop-blur-sm relative z-10
        ${player.team === "IND" ? "border-blue-500 text-blue-400" : "border-yellow-500 text-yellow-400"}
      `}>
        {player.name.split(" ").map((n: string) => n[0]).join("")}
        
        {player.isCaptain && (
          <div className="absolute -top-2 -right-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-black w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-black border-2 border-black z-20 shadow-[0_0_10px_rgba(250,204,21,0.8)]">
            C
          </div>
        )}
        {player.isViceCaptain && (
          <div className="absolute -top-2 -right-2 bg-gradient-to-r from-gray-300 to-white text-black w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-black border-2 border-black z-20 shadow-[0_0_10px_rgba(255,255,255,0.8)]">
            VC
          </div>
        )}
      </div>
      <div className="mt-2 text-center bg-black/60 px-2 py-1 rounded backdrop-blur-sm border border-white/10">
        <p className="text-[10px] md:text-xs font-bold text-white whitespace-nowrap">{player.name}</p>
        <p className="text-[9px] md:text-[10px] font-mono text-cyan-400">{player.points.toFixed(1)} pts</p>
      </div>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-[#020202] text-[#F5F0E6] font-sans pb-20">
      <Navbar />

      <div className="pt-32 px-4 md:px-8 max-w-[1400px] mx-auto relative z-10">
        
        {/* Header */}
        <header className="mb-12 flex flex-col md:flex-row justify-between items-start md:items-end border-b border-purple-900/30 pb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Star className="text-purple-400" size={32} />
              <h1 className="text-4xl font-black tracking-tighter">Fantasy AI Optimizer</h1>
              <span className="bg-purple-950/50 text-purple-400 border border-purple-500/30 text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-sm shadow-[0_0_15px_rgba(168,85,247,0.3)]">
                DREAM11 ENGINE
              </span>
            </div>
            <p className="text-gray-400 font-light text-lg">Machine Learning Pitch & Matchup Analysis to generate the mathematically perfect XI.</p>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Controls - 4 cols */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-[#050B14] border border-purple-500/20 rounded-3xl p-8 relative overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.5)]">
              <h3 className="text-purple-400 font-bold uppercase tracking-[0.2em] text-xs mb-6 flex items-center gap-2">
                <Target size={14} /> Match Selection
              </h3>

              <div className="space-y-6">
                <div className="flex justify-between items-center gap-4">
                  <div className="flex-1">
                    <label className="text-[10px] text-gray-400 uppercase tracking-widest font-bold mb-2 block">Team 1</label>
                    <select 
                      value={team1} 
                      onChange={e => setTeam1(e.target.value)}
                      className="w-full bg-black/50 border border-white/10 rounded-xl p-3 text-white focus:outline-none focus:border-purple-500 transition-colors font-bold"
                    >
                      <option value="IND">India (IND)</option>
                      <option value="ENG">England (ENG)</option>
                      <option value="SA">South Africa (SA)</option>
                    </select>
                  </div>
                  <div className="pt-6 font-black text-purple-500 text-sm uppercase tracking-widest">VS</div>
                  <div className="flex-1">
                    <label className="text-[10px] text-gray-400 uppercase tracking-widest font-bold mb-2 block">Team 2</label>
                    <select 
                      value={team2} 
                      onChange={e => setTeam2(e.target.value)}
                      className="w-full bg-black/50 border border-white/10 rounded-xl p-3 text-white focus:outline-none focus:border-purple-500 transition-colors font-bold"
                    >
                      <option value="AUS">Australia (AUS)</option>
                      <option value="PAK">Pakistan (PAK)</option>
                      <option value="NZ">New Zealand (NZ)</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="text-[10px] text-gray-400 uppercase tracking-widest font-bold mb-2 block">Venue Logic</label>
                  <select className="w-full bg-black/50 border border-white/10 rounded-xl p-3 text-white focus:outline-none focus:border-purple-500 transition-colors">
                    <option>Wankhede Stadium (Batting Paradise)</option>
                    <option>Chepauk Stadium (Spin Track)</option>
                    <option>Perth Stadium (Pace & Bounce)</option>
                  </select>
                </div>

                <button 
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-500 hover:to-pink-400 text-white font-black uppercase tracking-widest py-4 rounded-xl transition-all shadow-[0_0_20px_rgba(168,85,247,0.4)] disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isGenerating ? (
                    <><Cpu className="animate-spin" size={18}/> Synthesizing Perfect XI...</>
                  ) : (
                    <><Zap size={18}/> Generate AI Squad</>
                  )}
                </button>
              </div>
            </div>

            {showTeam && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-black/40 border border-green-500/30 rounded-3xl p-6"
              >
                <div className="flex items-center gap-3 mb-4">
                  <Award className="text-green-400" size={24} />
                  <div>
                    <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Projected Output</p>
                    <p className="text-2xl font-black text-white font-mono">{totalProjected.toFixed(1)} <span className="text-sm text-green-400 font-sans">Pts</span></p>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center bg-white/5 px-4 py-2 rounded-lg border border-white/5">
                    <span className="text-xs text-gray-400 uppercase font-bold tracking-widest">AI Captain</span>
                    <span className="font-bold text-yellow-400">Hardik Pandya (IND)</span>
                  </div>
                  <div className="flex justify-between items-center bg-white/5 px-4 py-2 rounded-lg border border-white/5">
                    <span className="text-xs text-gray-400 uppercase font-bold tracking-widest">AI Vice-Captain</span>
                    <span className="font-bold text-gray-300">Virat Kohli (IND)</span>
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Results - 8 cols */}
          <div className="lg:col-span-8">
            <div className="h-full bg-black/40 border border-white/10 rounded-[2.5rem] p-4 md:p-8 relative overflow-hidden flex flex-col justify-center min-h-[600px]">
              
              {!showTeam && !isGenerating && (
                <div className="text-center">
                  <div className="w-24 h-24 bg-purple-900/20 rounded-full flex items-center justify-center mx-auto mb-6 border border-purple-500/20">
                    <Shield size={40} className="text-purple-400" />
                  </div>
                  <h2 className="text-3xl font-black text-white mb-2">Build Your Empire</h2>
                  <p className="text-gray-400 max-w-md mx-auto">Select a matchup and venue. Our neural network will cross-reference 50,000 historical data points to build the statistically optimal 11-man squad.</p>
                </div>
              )}

              {isGenerating && (
                <div className="text-center flex flex-col items-center justify-center h-full space-y-6">
                  <motion.div 
                    animate={{ rotate: 360 }}
                    transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                    className="w-32 h-32 border-4 border-purple-900/50 border-t-pink-400 rounded-full"
                  />
                  <div className="space-y-2">
                    <h3 className="text-2xl font-black text-white tracking-widest uppercase">Crunching Matchups</h3>
                    <p className="text-pink-400 font-mono text-sm">Evaluating bowler vs batter variance...</p>
                  </div>
                </div>
              )}

              {showTeam && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="w-full h-full relative"
                >
                  {/* Grass Pitch Background */}
                  <div className="absolute inset-0 bg-[#3b5e2b] rounded-2xl border-[4px] border-white/30 overflow-hidden shadow-inner">
                    {/* Pitch Stripes */}
                    <div className="w-full h-full flex flex-col">
                      {[1,2,3,4,5,6,7,8].map(i => (
                        <div key={i} className={`w-full flex-1 ${i % 2 === 0 ? 'bg-white/5' : ''}`}></div>
                      ))}
                    </div>
                    {/* Central 30 yard circle (mocked as oval) */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[70%] border border-white/30 rounded-[100%] pointer-events-none"></div>
                    {/* The Pitch in middle */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-32 bg-[#c2b280]/80 rounded border border-white/20 pointer-events-none"></div>
                  </div>

                  {/* Players Layout overlaying the pitch */}
                  <div className="relative z-10 w-full h-full flex flex-col justify-between py-8 px-4">
                    
                    {/* Wicket Keeper Row (Top) */}
                    <div className="flex justify-center w-full">
                      {wk.map(p => <PlayerNode key={p.id} player={p} />)}
                    </div>

                    {/* Batsmen Row */}
                    <div className="flex justify-around w-full px-4">
                      {bats.map(p => <PlayerNode key={p.id} player={p} />)}
                    </div>

                    {/* All Rounders Row */}
                    <div className="flex justify-center gap-16 w-full">
                      {ars.map(p => <PlayerNode key={p.id} player={p} />)}
                    </div>

                    {/* Bowlers Row (Bottom) */}
                    <div className="flex justify-around w-full">
                      {bowls.map(p => <PlayerNode key={p.id} player={p} />)}
                    </div>

                  </div>

                </motion.div>
              )}

            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
