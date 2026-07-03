"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Target, Search, Crosshair, Map, Info, AlertOctagon } from "lucide-react";
import Navbar from "@/components/Navbar";

// Mock AI output for specific players
const TACTICS_DB: Record<string, any> = {
  "Virat Kohli": {
    weakness: "Outside Off Stump, Good Length",
    fielding: [
      { name: "Deep Point", top: "40%", left: "80%" },
      { name: "Short Third Man", top: "30%", left: "70%" },
      { name: "Slip", top: "15%", left: "45%" }
    ],
    pitchZone: { top: "35%", left: "65%", width: "15%", height: "20%" }, // Mock coordinates on pitch
    strategy: [
      "Deliveries 1-3: Bowl stump-to-stump, back of a length to push him back in the crease.",
      "Delivery 4: Push the line wider outside off stump on a good length. Invite the drive.",
      "Delivery 5: Sudden 140+ km/h inswinging yorker at the toes."
    ]
  },
  "Steve Smith": {
    weakness: "Leg Stump Half-Volley / Short Ball to Ribs",
    fielding: [
      { name: "Leg Gully", top: "25%", left: "40%" },
      { name: "Short Leg", top: "35%", left: "35%" },
      { name: "Deep Square Leg", top: "70%", left: "15%" }
    ],
    pitchZone: { top: "45%", left: "20%", width: "20%", height: "15%" }, 
    strategy: [
      "Deliveries 1-4: Persist with a 4th stump line. Do not bowl at his pads early.",
      "Delivery 5: Bowl a sharp bouncer directly at the left armpit.",
      "Delivery 6: Full, fast swinging delivery tailing into the pads."
    ]
  }
};

export default function TacticalEngine() {
  const [players, setPlayers] = useState<any[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState("Virat Kohli");
  const [isScanning, setIsScanning] = useState(false);
  const [tactic, setTactic] = useState(TACTICS_DB["Virat Kohli"]);

  // Fetch players just to populate dropdown
  useEffect(() => {
    fetch("http://127.0.0.1:8001/api/players/")
      .then(res => res.json())
      .then(data => {
        setPlayers(data.players.filter((p: any) => p.role.includes("Batter")));
      })
      .catch(err => console.error(err));
  }, []);

  const handleScan = (name: string) => {
    setSelectedPlayer(name);
    setIsScanning(true);
    setTimeout(() => {
      // Fallback to Kohli if we don't have mock data for someone
      setTactic(TACTICS_DB[name] || TACTICS_DB["Virat Kohli"]); 
      setIsScanning(false);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-[#070707] text-[#F5F0E6] font-sans pb-20 selection:bg-red-500/30">
      <Navbar />

      <div className="pt-32 px-4 md:px-8 max-w-[1400px] mx-auto relative z-10">
        
        {/* Header */}
        <header className="mb-12 flex flex-col md:flex-row justify-between items-start md:items-end border-b border-red-900/30 pb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Crosshair className="text-red-500" size={32} />
              <h1 className="text-4xl font-black tracking-tighter text-white uppercase">Tactical Attack Engine</h1>
              <span className="bg-red-950/50 text-red-400 border border-red-500/30 text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-sm flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                TARGET LOCKED
              </span>
            </div>
            <p className="text-red-500/60 font-mono text-sm uppercase tracking-widest">Opposition Scouting • Vulnerability Mapping</p>
          </div>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
          
          {/* Controls - 3 cols */}
          <div className="xl:col-span-3 space-y-6">
            <div className="bg-black border border-red-900/50 rounded-2xl p-6 relative overflow-hidden shadow-[0_0_30px_rgba(239,68,68,0.1)]">
              <h3 className="text-red-500 font-mono text-xs uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                <Search size={14} /> Select Target
              </h3>

              <div className="space-y-4">
                {["Virat Kohli", "Steve Smith", "Rohit Sharma"].map(name => (
                  <button
                    key={name}
                    onClick={() => handleScan(name)}
                    className={`w-full text-left px-4 py-3 font-mono text-sm uppercase tracking-wider rounded-xl transition-all border ${selectedPlayer === name && !isScanning ? 'bg-red-900/30 border-red-500 text-white' : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'}`}
                  >
                    {name}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-black border border-red-900/50 rounded-2xl p-6">
               <h3 className="text-red-500 font-mono text-xs uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                <AlertOctagon size={14} /> Primary Weakness
              </h3>
              {isScanning ? (
                <div className="h-16 flex items-center justify-center">
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, ease: "linear", duration: 1 }} className="w-6 h-6 border-2 border-red-900 border-t-red-500 rounded-full" />
                </div>
              ) : (
                <p className="text-white font-bold tracking-wide">{tactic.weakness}</p>
              )}
            </div>
          </div>

          {/* Maps - 9 cols */}
          <div className="xl:col-span-9 grid grid-cols-1 md:grid-cols-2 gap-8">
            
            {/* Pitch Map */}
            <div className="bg-black border border-white/10 rounded-3xl p-8 flex flex-col items-center">
              <h3 className="w-full text-gray-400 font-bold text-xs uppercase tracking-widest mb-6 flex items-center gap-2">
                <Target size={16} className="text-red-500"/> Vulnerability Pitch Map
              </h3>
              
              <div className="relative w-48 h-96 bg-[#c2b280] rounded border-4 border-white/30 shadow-inner">
                {/* Crease Lines */}
                <div className="absolute top-8 left-0 right-0 h-[2px] bg-white/70"></div>
                <div className="absolute bottom-8 left-0 right-0 h-[2px] bg-white/70"></div>
                
                {/* Wickets */}
                <div className="absolute top-2 left-1/2 -translate-x-1/2 flex gap-1">
                  <div className="w-1 h-3 bg-white"></div><div className="w-1 h-3 bg-white"></div><div className="w-1 h-3 bg-white"></div>
                </div>
                <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1">
                  <div className="w-1 h-3 bg-white"></div><div className="w-1 h-3 bg-white"></div><div className="w-1 h-3 bg-white"></div>
                </div>

                {/* AI Target Zone */}
                {!isScanning && (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="absolute bg-red-500/50 border-2 border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.8)] z-10"
                    style={{
                      top: tactic.pitchZone.top,
                      left: tactic.pitchZone.left,
                      width: tactic.pitchZone.width,
                      height: tactic.pitchZone.height,
                    }}
                  >
                    <div className="w-full h-full bg-red-400 opacity-20 animate-pulse"></div>
                  </motion.div>
                )}
                
                {/* Scanning overlay */}
                {isScanning && (
                   <motion.div 
                    className="absolute left-0 right-0 h-1 bg-red-500/80 shadow-[0_0_15px_rgba(239,68,68,1)] z-20"
                    animate={{ top: ["0%", "100%", "0%"] }}
                    transition={{ duration: 1.2, ease: "linear", repeat: Infinity }}
                   />
                )}
              </div>
            </div>

            {/* Field Map */}
            <div className="bg-black border border-white/10 rounded-3xl p-8 flex flex-col">
              <h3 className="w-full text-gray-400 font-bold text-xs uppercase tracking-widest mb-6 flex items-center gap-2">
                <Map size={16} className="text-blue-500"/> Defensive Field Setup
              </h3>
              
              <div className="relative w-full aspect-square bg-[#3b5e2b] rounded-full border-4 border-white/20 shadow-inner overflow-hidden flex items-center justify-center max-w-sm mx-auto">
                {/* 30 Yard Circle */}
                <div className="absolute w-[60%] h-[60%] rounded-full border border-white/30 border-dashed pointer-events-none"></div>
                {/* Pitch */}
                <div className="absolute w-[10%] h-[30%] bg-[#c2b280] rounded border border-white/20"></div>

                {/* Fielders */}
                {!isScanning && tactic.fielding.map((fielder: any, idx: number) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.2 }}
                    className="absolute group"
                    style={{ top: fielder.top, left: fielder.left }}
                  >
                    <div className="w-4 h-4 bg-cyan-400 rounded-full border-2 border-white shadow-[0_0_10px_rgba(34,211,238,0.8)] relative z-10 animate-pulse"></div>
                    <div className="absolute top-6 left-1/2 -translate-x-1/2 bg-black/80 px-2 py-1 rounded text-[10px] font-mono whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity border border-cyan-500/30 z-20">
                      {fielder.name}
                    </div>
                  </motion.div>
                ))}

                 {/* Scanning overlay */}
                 {isScanning && (
                   <div className="absolute inset-0 bg-black/40 flex items-center justify-center z-30">
                      <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, ease: "linear", duration: 2 }}>
                        <Crosshair size={40} className="text-red-500 opacity-50" />
                      </motion.div>
                   </div>
                )}
              </div>

              {/* Execution Strategy Readout */}
              <div className="mt-8 bg-blue-950/20 border border-blue-900/50 rounded-xl p-5">
                <h4 className="text-blue-400 font-mono text-[10px] uppercase tracking-widest mb-3 flex items-center gap-2">
                  <Info size={12} /> Execution Strategy
                </h4>
                {isScanning ? (
                  <div className="space-y-2">
                    <div className="h-4 bg-white/5 rounded w-full animate-pulse"></div>
                    <div className="h-4 bg-white/5 rounded w-5/6 animate-pulse"></div>
                    <div className="h-4 bg-white/5 rounded w-4/6 animate-pulse"></div>
                  </div>
                ) : (
                  <ul className="space-y-2">
                    {tactic.strategy.map((step: string, i: number) => (
                      <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                        <span className="text-blue-500 font-bold font-mono">{(i+1).toString().padStart(2, '0')}</span>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
