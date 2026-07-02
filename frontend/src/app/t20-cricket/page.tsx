"use client";

import { useState, useEffect } from "react";
import { Zap, Crosshair, TrendingUp, AlertTriangle } from "lucide-react";

export default function T20CricketPage() {
  const [matchData, setMatchData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8001/api/matches/t20-center");
        if (response.ok) {
          const data = await response.json();
          setMatchData(data);
        }
      } catch (error) {
        console.error("Failed to fetch t20 center data:", error);
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
    return <div className="min-h-screen bg-black flex items-center justify-center text-white font-mono uppercase">Loading T20 Data...</div>;
  }

  const { match_info, boundary_impact, matchup_predictor, momentum } = matchData;
  const t1Score = match_info.team1_score.split('&');
  const t2Score = match_info.team2_score.split('&');

  return (
    <div className="min-h-screen bg-black text-white font-sans pt-24 pb-12 px-8 overflow-hidden">
      
      <div className="max-w-[1500px] mx-auto">
        
        {/* Header - Aggressive Crimson & Black */}
        <header className="mb-12 flex justify-between items-end border-b-8 border-[#DC2626] pb-6">
          <div>
            <h1 className="text-7xl font-black tracking-tighter text-white mb-2 uppercase">
              T20 <span className="text-[#DC2626]">Sprint</span>
            </h1>
            <p className="text-gray-400 text-xl uppercase tracking-[0.4em] font-black">
              {match_info.tournament} // {match_info.status_text}
            </p>
          </div>
          <div className="bg-[#DC2626] text-white px-8 py-3 font-black text-2xl tracking-widest uppercase transform skew-x-12">
            <span className="block transform -skew-x-12">Action Live</span>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Main Content - 8 cols */}
          <div className="lg:col-span-8 space-y-8">
            
            {/* The Scoreboard */}
            <div className="bg-[#111111] border-4 border-[#222222] p-10 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-full h-3 bg-gradient-to-r from-transparent via-[#DC2626] to-transparent"></div>
              
              <div className="flex justify-between items-center mb-8 border-b-4 border-[#222222] pb-6">
                <span className="text-gray-500 tracking-[0.4em] text-sm uppercase font-black">Current Equation</span>
                <span className="text-white font-black text-2xl uppercase tracking-widest bg-[#DC2626] px-6 py-2">{match_info.equation}</span>
              </div>
              
              <div className="flex justify-between items-center bg-black p-8 border-4 border-[#333333]">
                <div className="w-2/5">
                  <h2 className="text-4xl font-black text-white mb-2 uppercase">{match_info.team1}</h2>
                  <p className="text-7xl font-black text-[#DC2626]">{t1Score[0]}</p>
                  <p className="text-2xl text-gray-500 mt-2 font-black">{t1Score[1]?.trim()}</p>
                </div>
                
                <div className="w-1/5 flex justify-center">
                  <div className="w-20 h-20 bg-[#DC2626] flex items-center justify-center transform rotate-45">
                    <span className="text-white font-black italic text-4xl transform -rotate-45">VS</span>
                  </div>
                </div>
                
                <div className="w-2/5 text-right">
                  <h2 className="text-4xl font-black text-gray-500 mb-2 uppercase">{match_info.team2}</h2>
                  <p className="text-6xl font-black text-white">{t2Score[0]}</p>
                  <p className="text-xl text-gray-600 mt-2 font-black">{t2Score[1]?.trim()}</p>
                </div>
              </div>
            </div>

            {/* Boundary Impact Radar */}
            <div className="grid grid-cols-2 gap-8">
              <div className="bg-[#111111] border-4 border-[#222222] p-8">
                <h3 className="text-white font-black text-3xl uppercase tracking-wider mb-8 flex items-center gap-3">
                  <Zap className="text-[#DC2626]" size={36} /> Impact Ratio
                </h3>
                
                <div className="space-y-8">
                  <div>
                    <div className="flex justify-between text-lg font-black uppercase tracking-widest mb-2">
                      <span className="text-gray-400">Boundaries (4s/6s)</span>
                      <span className="text-white">{boundary_impact.four_percentage + boundary_impact.six_percentage}%</span>
                    </div>
                    <div className="w-full bg-[#222222] h-6">
                      <div className="bg-[#DC2626] h-6" style={{ width: `${boundary_impact.four_percentage + boundary_impact.six_percentage}%` }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-lg font-black uppercase tracking-widest mb-2">
                      <span className="text-gray-400">Dot Balls</span>
                      <span className="text-white">{boundary_impact.dot_percentage}%</span>
                    </div>
                    <div className="w-full bg-[#222222] h-6">
                      <div className="bg-[#555555] h-6" style={{ width: `${boundary_impact.dot_percentage}%` }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-lg font-black uppercase tracking-widest mb-2">
                      <span className="text-gray-400">Strike Rotation</span>
                      <span className="text-white">{boundary_impact.rotation_percentage}%</span>
                    </div>
                    <div className="w-full bg-[#222222] h-6">
                      <div className="bg-[#777777] h-6" style={{ width: `${boundary_impact.rotation_percentage}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Momentum Dial */}
              <div className="bg-[#DC2626] p-8 flex flex-col justify-center items-center text-center">
                <h3 className="text-white font-black text-3xl uppercase tracking-wider mb-4 flex items-center gap-2">
                  <TrendingUp size={36} /> Momentum Shift
                </h3>
                <p className="text-black font-black uppercase tracking-[0.3em] text-lg mb-10">Last 12 Deliveries</p>
                
                <div className="relative w-56 h-56 border-[12px] border-black rounded-full flex items-center justify-center bg-[#991B1B]">
                  <div className="absolute inset-2 border-[6px] border-dashed border-[#7F1D1D] rounded-full"></div>
                  <div className="text-center relative z-10">
                    <p className="text-7xl font-black text-white">{momentum}</p>
                    <p className="text-lg font-black uppercase tracking-[0.3em] text-black mt-2">Index</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Side Panel - 4 cols */}
          <div className="lg:col-span-4 space-y-8">
            
            {/* Match-Up Predictor */}
            <div className="bg-[#111111] border-4 border-[#222222] p-8 h-full">
              <h3 className="text-white font-black text-3xl uppercase tracking-wider mb-10 flex items-center gap-3 border-b-4 border-[#222222] pb-6">
                <Crosshair className="text-[#DC2626]" size={36} /> Match-Up AI
              </h3>
              
              <div className="bg-black border-l-8 border-[#DC2626] p-8 mb-10">
                <p className="text-gray-500 text-sm font-black uppercase tracking-[0.3em] mb-3">Striker</p>
                <p className="text-3xl font-black text-white uppercase">{matchup_predictor.batsman}</p>
              </div>
              
              <div className="text-center my-6">
                <span className="text-gray-600 font-black italic text-2xl">VERSUS</span>
              </div>
              
              <div className="bg-black border-l-8 border-gray-600 p-8 mb-10">
                <p className="text-gray-500 text-sm font-black uppercase tracking-[0.3em] mb-3">Bowler</p>
                <p className="text-3xl font-black text-white uppercase">{matchup_predictor.bowler}</p>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="bg-black p-6 text-center border-4 border-[#222222]">
                  <p className="text-gray-500 text-xs uppercase font-black tracking-widest mb-3">Wicket Prob</p>
                  <p className="text-4xl font-black text-white">{matchup_predictor.wicket_probability}</p>
                </div>
                <div className="bg-[#DC2626] p-6 text-center">
                  <p className="text-black text-xs uppercase font-black tracking-widest mb-3">Boundary Prob</p>
                  <p className="text-4xl font-black text-white">{matchup_predictor.boundary_probability}</p>
                </div>
              </div>
              
              <div className="mt-10 flex items-start gap-4 bg-black border-4 border-[#222222] p-6">
                <AlertTriangle className="text-[#DC2626] flex-shrink-0" size={28} />
                <p className="text-sm text-gray-400 font-black leading-loose uppercase">
                  Data suggests bowling full and wide outside off stump. Striker has a 42% boundary rate on leg side vs this bowler type.
                </p>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
