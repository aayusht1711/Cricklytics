"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Search, ChevronRight, Activity, Target, GitPullRequest, SearchIcon } from "lucide-react";
import Navbar from "@/components/Navbar";
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid 
} from "recharts";

export default function PlayersPage() {
  const [players, setPlayers] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPlayer, setSelectedPlayer] = useState<any>(null);
  
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonPlayer, setComparisonPlayer] = useState<any>(null);
  const [compareSearch, setCompareSearch] = useState("");

  const [activeFormat, setActiveFormat] = useState<"Test" | "ODI" | "T20">("Test");

  useEffect(() => {
    fetch("http://127.0.0.1:8001/api/players/")
      .then(res => res.json())
      .then(data => setPlayers(data.players))
      .catch(err => console.error(err));
  }, []);

  const fetchPlayerProfile = async (id: string, isCompare: boolean = false) => {
    try {
      const res = await fetch(`http://127.0.0.1:8001/api/players/${id}`);
      const data = await res.json();
      if (isCompare) {
        setComparisonPlayer(data);
      } else {
        setSelectedPlayer(data);
        setIsComparing(false);
        setComparisonPlayer(null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const filteredPlayers = players.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.team.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const compareFilteredPlayers = players.filter(p => 
    p.id !== selectedPlayer?.id &&
    (p.name.toLowerCase().includes(compareSearch.toLowerCase()) || p.team.toLowerCase().includes(compareSearch.toLowerCase()))
  );

  // Dynamic Theme Logic
  const theme = {
    Test: {
      bg: "bg-[#0B3D2E]",
      border: "border-red-500/30",
      glow: "bg-red-600",
      accent: "text-red-500",
      chartColor: "#ef4444"
    },
    ODI: {
      bg: "bg-[#0A192F]",
      border: "border-blue-500/20",
      glow: "bg-blue-600",
      accent: "text-cyan-400",
      chartColor: "#22d3ee"
    },
    T20: {
      bg: "bg-black",
      border: "border-red-500/20",
      glow: "bg-red-700",
      accent: "text-red-500",
      chartColor: "#ef4444"
    }
  }[activeFormat];

  const getRadarData = (player: any) => [
    { subject: 'Control %', A: player.technique.control_percentage, fullMark: 100 },
    { subject: 'Middle Bat', A: player.technique.middle_of_bat, fullMark: 100 },
    { subject: 'Power', A: player.t20_stats.boundary_impact, fullMark: 100 },
    { subject: 'Defensive', A: player.test_stats.defensive_solidity, fullMark: 100 },
    { subject: 'Rotation', A: player.odi_stats.strike_rotation, fullMark: 100 },
  ];

  const renderStats = (player: any) => {
    if (!player) return null;
    
    let formatStats;
    if (activeFormat === "Test") formatStats = player.test_stats;
    if (activeFormat === "ODI") formatStats = player.odi_stats;
    if (activeFormat === "T20") formatStats = player.t20_stats;

    return (
      <div className="space-y-6 mt-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white/5 border border-white/10 p-4 rounded-2xl text-center">
            <div className="text-xs text-gray-400 uppercase font-bold mb-1">Matches</div>
            <div className="text-2xl font-black text-white">{formatStats.matches}</div>
          </div>
          <div className="bg-white/5 border border-white/10 p-4 rounded-2xl text-center">
            <div className="text-xs text-gray-400 uppercase font-bold mb-1">Runs</div>
            <div className="text-2xl font-black text-white">{formatStats.runs}</div>
          </div>
          <div className="bg-white/5 border border-white/10 p-4 rounded-2xl text-center">
            <div className={`text-xs ${theme.accent} uppercase font-bold mb-1`}>Average</div>
            <div className="text-2xl font-black text-white">{formatStats.average}</div>
          </div>
          <div className="bg-white/5 border border-white/10 p-4 rounded-2xl text-center">
            <div className={`text-xs ${theme.accent} uppercase font-bold mb-1`}>
              {activeFormat === "Test" ? "100s" : "Strike Rate"}
            </div>
            <div className={`text-2xl font-black ${theme.accent}`}>
              {activeFormat === "Test" ? formatStats["100s"] : formatStats.strike_rate}
            </div>
          </div>
        </div>

        {/* Advanced Features */}
        <div className={`bg-black/60 border ${theme.border} p-6 rounded-3xl`}>
          <h3 className={`text-lg font-bold text-white mb-4 flex items-center gap-2`}>
            <Activity className={theme.accent} size={20}/> 
            {activeFormat} Advanced Analytics
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {activeFormat === "Test" && (
              <>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="text-xs text-gray-400 mb-1">Defensive Solidity Index</div>
                  <div className={`text-xl font-bold ${theme.accent}`}>{formatStats.defensive_solidity}%</div>
                </div>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="text-xs text-gray-400 mb-1">Home vs Away Avg</div>
                  <div className="flex gap-4">
                    <span className="text-xl font-bold text-white">H: {formatStats.home_average}</span>
                    <span className="text-xl font-bold text-gray-400">A: {formatStats.away_average}</span>
                  </div>
                </div>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="text-xs text-gray-400 mb-1">Session Dominance</div>
                  <div className="text-lg font-bold text-white">{formatStats.session_average}</div>
                </div>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="text-xs text-gray-400 mb-1">Partnership Value</div>
                  <div className="text-lg font-bold text-white">{formatStats.partnership_value}</div>
                </div>
              </>
            )}

            {activeFormat === "ODI" && (
              <>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="text-xs text-gray-400 mb-1">Phase Pacing SR</div>
                  <div className="text-sm font-bold text-white">{formatStats.phase_pacing}</div>
                </div>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="text-xs text-gray-400 mb-1">Strike Rotation Efficiency</div>
                  <div className={`text-xl font-bold ${theme.accent}`}>{formatStats.strike_rotation}%</div>
                </div>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="text-xs text-gray-400 mb-1">Run Chase Average</div>
                  <div className="text-xl font-bold text-white">{formatStats.chase_average}</div>
                </div>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="text-xs text-gray-400 mb-1">50 to 100 Conversion</div>
                  <div className="text-xl font-bold text-white">{formatStats.conversion_rate}</div>
                </div>
              </>
            )}

            {activeFormat === "T20" && (
              <>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="text-xs text-gray-400 mb-1">Entry Intent (First 10 Balls SR)</div>
                  <div className="text-xl font-bold text-white">{formatStats.entry_intent_sr}</div>
                </div>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="text-xs text-gray-400 mb-1">Boundary Impact</div>
                  <div className={`text-xl font-bold ${theme.accent}`}>{formatStats.boundary_impact}% of runs</div>
                </div>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="text-xs text-gray-400 mb-1">Match-Up Dominance SR</div>
                  <div className="text-sm font-bold text-white">{formatStats.matchup_dominance}</div>
                </div>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                  <div className="text-xs text-gray-400 mb-1">Death Overs SR (16-20)</div>
                  <div className="text-xl font-bold text-white">{formatStats.death_sr}</div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Visual Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          
          <div className="bg-black/40 border border-white/10 p-6 rounded-3xl flex flex-col items-center">
            <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2 self-start">
              <Target className={theme.accent} size={16}/> 
              Player Radar Profile
            </h3>
            <div className="w-full h-48">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={getRadarData(player)}>
                  <PolarGrid stroke="#333" />
                  <PolarAngleAxis dataKey="subject" tick={{fill: '#888', fontSize: 10}} />
                  <Radar name={player.name} dataKey="A" stroke={theme.chartColor} fill={theme.chartColor} fillOpacity={0.4} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-black/40 border border-white/10 p-6 rounded-3xl flex flex-col justify-center">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Edge Percentage</span>
                <span className="text-sm font-bold text-white">{player.technique.edge_percentage}%</span>
              </div>
              <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
                <div className={`h-full bg-white`} style={{ width: `${player.technique.edge_percentage}%` }}></div>
              </div>

              <div className="flex justify-between items-center pt-2">
                <span className="text-sm text-gray-400">Strongest Zone</span>
                <span className="text-sm font-bold text-white">{player.technique.strong_zone}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    );
  };

  return (
    <div className={`min-h-screen ${theme.bg} font-sans text-white transition-colors duration-700`}>
      <Navbar />

      {/* Dynamic Background Ambience */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className={`absolute top-[20%] left-[10%] w-[40%] h-[40%] ${theme.glow} opacity-10 blur-[150px] rounded-full transition-colors duration-700`} />
        <div className={`absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] ${theme.glow} opacity-10 blur-[150px] rounded-full transition-colors duration-700`} />
      </div>

      <div className="relative z-10 pt-32 pb-20 px-8 max-w-[1400px] mx-auto">
        <div className="flex flex-col lg:flex-row gap-8">
          
          {/* Left Sidebar: Player List */}
          <div className="w-full lg:w-80 flex-shrink-0">
            <div className="sticky top-32 bg-black/60 backdrop-blur-xl border border-white/10 rounded-[2rem] p-6 shadow-2xl">
              <h2 className="text-2xl font-black text-white mb-6">Database</h2>
              
              <div className="relative mb-6">
                <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                <input 
                  type="text" 
                  placeholder="Search player..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-full py-3 pl-12 pr-4 text-sm text-white focus:outline-none"
                />
              </div>

              <div className="space-y-2 max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
                {filteredPlayers.map((player) => (
                  <div 
                    key={player.id}
                    onClick={() => fetchPlayerProfile(player.id)}
                    className={`flex items-center gap-4 p-3 rounded-2xl cursor-pointer transition-all ${selectedPlayer?.id === player.id ? 'bg-white/10 border border-white/20' : 'hover:bg-white/5 border border-transparent'}`}
                  >
                    <div className="w-12 h-12 rounded-full overflow-hidden bg-gray-800 border border-white/10">
                      <img src={player.image} alt={player.name} className="w-full h-full object-cover" />
                    </div>
                    <div className="flex-1">
                      <div className="font-bold text-white text-sm">{player.name}</div>
                      <div className="text-xs text-gray-400">{player.team}</div>
                    </div>
                    {selectedPlayer?.id === player.id && <ChevronRight size={16} className={theme.accent} />}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Area: Player Profile & Comparison */}
          <div className="flex-1 min-w-0">
            {!selectedPlayer ? (
              <div className="h-[70vh] flex flex-col items-center justify-center text-center bg-black/40 border border-white/10 rounded-[2rem] p-10 backdrop-blur-xl">
                <div className={`w-24 h-24 ${theme.glow} bg-opacity-20 rounded-full flex items-center justify-center mb-6 border border-white/10`}>
                  <Search size={40} className="text-white" />
                </div>
                <h2 className="text-3xl font-black text-white mb-2">Select a Player</h2>
                <p className="text-gray-400 max-w-md">Browse the database and select a player to view dynamic analytical profiles and visual radar charts.</p>
              </div>
            ) : (
              <div className="space-y-6">
                
                {/* Format Toggle & Compare Button */}
                <div className="flex flex-col sm:flex-row justify-between items-center gap-4 bg-black/60 backdrop-blur-xl border border-white/10 rounded-full p-2">
                  <div className="flex gap-2">
                    {["Test", "ODI", "T20"].map(format => (
                      <button
                        key={format}
                        onClick={() => setActiveFormat(format as any)}
                        className={`px-6 py-2 rounded-full text-sm font-bold transition-all ${activeFormat === format ? `${theme.glow} text-white` : 'text-gray-400 hover:text-white hover:bg-white/10'}`}
                      >
                        {format}
                      </button>
                    ))}
                  </div>
                  
                  <button 
                    onClick={() => setIsComparing(!isComparing)}
                    className={`flex items-center gap-2 px-6 py-2 rounded-full text-sm font-bold transition-all ${isComparing ? 'bg-red-500/20 text-red-400 border border-red-500/50' : 'bg-white text-black hover:bg-gray-200'}`}
                  >
                    <GitPullRequest size={16} />
                    {isComparing ? "Cancel Comparison" : "Compare Player"}
                  </button>
                </div>

                <div className={`grid gap-6 ${isComparing ? 'grid-cols-1 xl:grid-cols-2' : 'grid-cols-1'}`}>
                  
                  {/* Player 1 Profile */}
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-black/60 backdrop-blur-xl border border-white/10 rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden"
                  >
                    <div className="flex items-center gap-6 mb-8 relative z-10">
                      <div className={`w-24 h-24 rounded-full overflow-hidden border-4 ${theme.border}`}>
                        <img src={selectedPlayer.image} alt={selectedPlayer.name} className="w-full h-full object-cover" />
                      </div>
                      <div>
                        <h1 className="text-4xl font-black text-white">{selectedPlayer.name}</h1>
                        <div className="flex items-center gap-3 mt-2 text-sm font-bold text-gray-400 uppercase tracking-widest">
                          <span className={theme.accent}>{selectedPlayer.team}</span>
                          <span>•</span>
                          <span>{selectedPlayer.role}</span>
                        </div>
                      </div>
                    </div>

                    {renderStats(selectedPlayer)}
                  </motion.div>

                  {/* Player 2 Comparison */}
                  {isComparing && (
                    <motion.div 
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="bg-black/60 backdrop-blur-xl border border-white/10 rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden flex flex-col"
                    >
                      {!comparisonPlayer ? (
                        <div className="flex-1 flex flex-col items-center justify-center text-center">
                          <h3 className="text-xl font-bold text-white mb-4">Select opponent to compare</h3>
                          <div className="relative w-full max-w-sm mb-6">
                            <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                            <input 
                              type="text" 
                              placeholder="Search database..." 
                              value={compareSearch}
                              onChange={(e) => setCompareSearch(e.target.value)}
                              className="w-full bg-white/5 border border-white/10 rounded-full py-3 pl-12 pr-4 text-sm text-white focus:outline-none"
                            />
                          </div>
                          
                          <div className="w-full max-w-sm space-y-2 max-h-[40vh] overflow-y-auto custom-scrollbar">
                            {compareFilteredPlayers.map((player) => (
                              <div 
                                key={player.id}
                                onClick={() => fetchPlayerProfile(player.id, true)}
                                className="flex items-center gap-4 p-3 rounded-2xl cursor-pointer hover:bg-white/5 border border-transparent transition-all"
                              >
                                <div className="w-10 h-10 rounded-full overflow-hidden bg-gray-800 border border-white/10">
                                  <img src={player.image} alt={player.name} className="w-full h-full object-cover" />
                                </div>
                                <div className="flex-1 text-left">
                                  <div className="font-bold text-white text-sm">{player.name}</div>
                                  <div className="text-xs text-gray-400">{player.team}</div>
                                </div>
                                <ChevronRight size={16} className="text-gray-500" />
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <>
                          <div className="flex items-center gap-6 mb-8 relative z-10">
                            <div className={`w-24 h-24 rounded-full overflow-hidden border-4 ${theme.border}`}>
                              <img src={comparisonPlayer.image} alt={comparisonPlayer.name} className="w-full h-full object-cover" />
                            </div>
                            <div>
                              <h1 className="text-4xl font-black text-white">{comparisonPlayer.name}</h1>
                              <div className="flex items-center gap-3 mt-2 text-sm font-bold text-gray-400 uppercase tracking-widest">
                                <span className={theme.accent}>{comparisonPlayer.team}</span>
                                <span>•</span>
                                <span>{comparisonPlayer.role}</span>
                              </div>
                            </div>
                            <button 
                              onClick={() => setComparisonPlayer(null)}
                              className="ml-auto text-xs text-gray-500 hover:text-white underline"
                            >
                              Change
                            </button>
                          </div>

                          {renderStats(comparisonPlayer)}
                        </>
                      )}
                    </motion.div>
                  )}

                </div>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
