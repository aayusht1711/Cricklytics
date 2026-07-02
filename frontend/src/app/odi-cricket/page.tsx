"use client";

import { useState, useEffect } from "react";
import { Activity, BarChart2, PieChart, FastForward } from "lucide-react";
import { motion } from "framer-motion";

export default function ODICricketPage() {
  const [matchData, setMatchData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8001/api/matches/odi-center");
        if (response.ok) {
          const data = await response.json();
          setMatchData(data);
        }
      } catch (error) {
        console.error("Failed to fetch odi center data:", error);
      }
    };

    fetchData();

    // WebSocket connection for true 0-latency updates
    const ws = new WebSocket("ws://127.0.0.1:8001/ws/live");
    
    ws.onmessage = (event) => {
      if (event.data === "UPDATE") {
        fetchData();
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  if (!matchData) {
    return <div className="min-h-screen bg-[#020813] flex items-center justify-center text-white">Loading ODI Data...</div>;
  }

  const { match_info, phase_analytics, strike_rotation } = matchData;
  const t1Score = match_info.team1_score.split('&');
  const t2Score = match_info.team2_score.split('&');

  return (
    <div className="min-h-screen bg-[#020813] text-[#E2E8F0] font-sans pt-24 pb-12 px-8 overflow-hidden relative">
      
      {/* Background Ambience */}
      <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-[#0E3B66] opacity-20 blur-[150px] rounded-full mix-blend-screen pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-[#0088CC] opacity-10 blur-[150px] rounded-full mix-blend-screen pointer-events-none" />

      <div className="max-w-[1500px] mx-auto relative z-10">
        
        {/* Header */}
        <header className="mb-12 flex justify-between items-end border-b border-[#0E3B66]/50 pb-6">
          <div>
            <h1 className="text-5xl font-black tracking-tight text-white mb-2">
              <span className="text-[#00A3FF]">ODI</span> Match Center
            </h1>
            <p className="text-[#94A3B8] text-lg uppercase tracking-widest font-bold">
              {match_info.tournament} • {match_info.status_text}
            </p>
          </div>
          <div className="flex gap-4">
            <div className="text-right bg-[#051124] border border-[#0E3B66] px-6 py-2 rounded-xl">
              <p className="text-[10px] text-[#94A3B8] uppercase tracking-widest mb-1">Required Rate</p>
              <p className="text-2xl font-black text-[#00A3FF]">{match_info.required_rate}</p>
            </div>
            <div className="text-right bg-[#051124] border border-[#0E3B66] px-6 py-2 rounded-xl">
              <p className="text-[10px] text-[#94A3B8] uppercase tracking-widest mb-1">Current Rate</p>
              <p className="text-2xl font-black text-white">{match_info.current_rate}</p>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Main Scoreboard - 8 cols */}
          <div className="lg:col-span-8 space-y-8">
            
            {/* The Scoreboard */}
            <div className="bg-[#051124] border border-[#0E3B66]/60 rounded-3xl p-10 flex justify-between items-center relative overflow-hidden shadow-[0_0_40px_rgba(0,163,255,0.05)]">
              <div className="w-1/3">
                <h2 className="text-3xl font-black text-white mb-2">{match_info.team1}</h2>
                <p className="text-5xl font-black text-[#00A3FF]">{t1Score[0]}</p>
                <p className="text-lg text-[#94A3B8] mt-2 font-bold">{t1Score[1]?.trim()}</p>
              </div>
              
              <div className="w-1/3 flex flex-col items-center">
                <span className="text-[#38BDF8] font-black italic text-3xl">VS</span>
              </div>
              
              <div className="w-1/3 text-right">
                <h2 className="text-3xl font-black text-[#94A3B8] mb-2">{match_info.team2}</h2>
                <p className="text-4xl font-bold text-[#64748B]">{t2Score[0]}</p>
                <p className="text-sm text-[#475569] mt-2 font-bold">{t2Score[1]?.trim()}</p>
              </div>
            </div>

            {/* Run Rate Worm Graph (Simulated) */}
            <div className="bg-[#051124] border border-[#0E3B66]/60 rounded-3xl p-10 relative overflow-hidden">
              <h3 className="text-white font-bold text-xl mb-8 flex items-center gap-3">
                <Activity className="text-[#00A3FF]" /> Run Rate Worm
              </h3>
              
              <div className="h-64 w-full border-b border-l border-[#1E293B] relative">
                {/* Y-axis labels */}
                <div className="absolute left-[-30px] top-0 text-[10px] text-[#64748B]">300</div>
                <div className="absolute left-[-30px] top-[33%] text-[10px] text-[#64748B]">200</div>
                <div className="absolute left-[-30px] top-[66%] text-[10px] text-[#64748B]">100</div>
                <div className="absolute left-[-20px] bottom-0 text-[10px] text-[#64748B]">0</div>
                
                {/* X-axis labels */}
                <div className="absolute bottom-[-25px] left-[20%] text-[10px] text-[#64748B]">10</div>
                <div className="absolute bottom-[-25px] left-[40%] text-[10px] text-[#64748B]">20</div>
                <div className="absolute bottom-[-25px] left-[60%] text-[10px] text-[#64748B]">30</div>
                <div className="absolute bottom-[-25px] left-[80%] text-[10px] text-[#64748B]">40</div>
                <div className="absolute bottom-[-25px] right-0 text-[10px] text-[#64748B]">50</div>
                
                {/* Graph Grid */}
                <div className="absolute inset-0 grid grid-cols-5 grid-rows-3 opacity-20 pointer-events-none">
                  {[...Array(15)].map((_, i) => (
                    <div key={i} className="border-r border-t border-[#334155]"></div>
                  ))}
                </div>

                {/* SVG Graph Paths */}
                <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 100 100">
                  {/* Target Worm */}
                  <path d="M0,100 L20,80 L40,60 L60,40 L80,20 L100,0" fill="none" stroke="#334155" strokeWidth="2" strokeDasharray="5,5" />
                  {/* Current Score Worm */}
                  <path d="M0,100 Q10,95 20,85 T40,65 T60,45" fill="none" stroke="#00A3FF" strokeWidth="3" />
                </svg>
              </div>
              <div className="flex gap-6 mt-8 justify-center">
                <div className="flex items-center gap-2"><div className="w-3 h-1 bg-[#00A3FF]"></div><span className="text-xs text-[#94A3B8]">Current Score</span></div>
                <div className="flex items-center gap-2"><div className="w-3 h-1 bg-[#334155] border-t border-dashed"></div><span className="text-xs text-[#94A3B8]">Target (312)</span></div>
              </div>
            </div>
          </div>

          {/* Side Panel - 4 cols */}
          <div className="lg:col-span-4 space-y-8">
            
            {/* Phase Analytics */}
            <div className="bg-[#051124] border border-[#0E3B66]/60 rounded-3xl p-8 relative overflow-hidden">
              <h3 className="text-white font-bold text-xl mb-6 flex items-center gap-3">
                <FastForward className="text-[#38BDF8]" /> Phase Analytics
              </h3>
              
              <div className="space-y-4">
                {phase_analytics.map((phase: any, idx: number) => (
                  <div key={idx} className={`p-4 rounded-xl border ${phase.runs === 'TBD' ? 'bg-[#030812] border-[#0F172A] opacity-50' : 'bg-[#0B1B36] border-[#1E3A8A]'}`}>
                    <p className="text-[10px] uppercase tracking-widest text-[#94A3B8] font-bold mb-2">{phase.phase}</p>
                    <div className="flex justify-between items-end">
                      <div>
                        <span className="text-3xl font-black text-white">{phase.runs}</span>
                        <span className="text-sm text-[#64748B] ml-1">runs</span>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-[#00A3FF] font-bold mb-1">RR: {phase.run_rate}</p>
                        <p className="text-xs text-[#EF4444] font-bold">{phase.wickets} Wickets</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Strike Rotation Heatmap */}
            <div className="bg-[#051124] border border-[#0E3B66]/60 rounded-3xl p-8">
              <h3 className="text-white font-bold text-xl mb-6 flex items-center gap-3">
                <PieChart className="text-[#00A3FF]" /> Strike Rotation
              </h3>
              
              <div className="flex items-center justify-between mb-8 border-b border-[#1E293B] pb-6">
                <div>
                  <p className="text-3xl font-black text-[#00A3FF]">{strike_rotation.rotation_efficiency}</p>
                  <p className="text-[10px] uppercase tracking-widest text-[#94A3B8] mt-1">Efficiency Rating</p>
                </div>
                <div className="w-16 h-16 rounded-full border-4 border-[#00A3FF] border-t-[#0F172A] transform rotate-45 flex items-center justify-center shadow-[0_0_15px_rgba(0,163,255,0.3)]">
                  <Activity size={24} className="text-[#00A3FF] -rotate-45" />
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-xs font-bold mb-1">
                    <span className="text-[#94A3B8]">Singles/Twos</span>
                    <span className="text-white">{strike_rotation.singles}</span>
                  </div>
                  <div className="w-full bg-[#0F172A] rounded-full h-2">
                    <div className="bg-[#38BDF8] h-2 rounded-full w-[65%]"></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs font-bold mb-1">
                    <span className="text-[#94A3B8]">Dot Balls</span>
                    <span className="text-white">{strike_rotation.dot_balls}</span>
                  </div>
                  <div className="w-full bg-[#0F172A] rounded-full h-2">
                    <div className="bg-[#EF4444] h-2 rounded-full w-[25%]"></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs font-bold mb-1">
                    <span className="text-[#94A3B8]">Boundaries</span>
                    <span className="text-white">{strike_rotation.boundaries}</span>
                  </div>
                  <div className="w-full bg-[#0F172A] rounded-full h-2">
                    <div className="bg-[#F59E0B] h-2 rounded-full w-[10%]"></div>
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
