"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldAlert, Wind, TrendingUp, Thermometer, Clock } from "lucide-react";

export default function TestCricketPage() {
  const [matchData, setMatchData] = useState<any>(null);
  const [isVideoPlaying, setIsVideoPlaying] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8001/api/matches/1/test-center");
        if (response.ok) {
          const data = await response.json();
          setMatchData(data);
        }
      } catch (error) {
        console.error("Failed to fetch test center data:", error);
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

  const handleSkip = () => {
    if (videoRef.current) videoRef.current.pause();
    setIsVideoPlaying(false);
  };

  if (!matchData) {
    return <div className="min-h-screen bg-[#0A1A12] flex items-center justify-center text-white">Loading Test Data...</div>;
  }

  const { match_info, sessions, pitch_diagnostics, battle_zone } = matchData;
  const t1Score = match_info.team1_score.split('&');
  const t2Score = match_info.team2_score.split('&');

  return (
    <div className="relative min-h-screen bg-[#0A1A12] overflow-hidden text-[#E8F0E5] font-sans pt-20 pb-10 px-8">
      
      {/* CINEMATIC WELCOME VIDEO */}
      <AnimatePresence>
        {isVideoPlaying && (
          <motion.div 
            initial={{ opacity: 1 }}
            exit={{ opacity: 0, transition: { duration: 1.5 } }}
            className="fixed inset-0 z-50 bg-black flex flex-col justify-center items-center cursor-pointer"
            onClick={handleSkip}
          >
            <video ref={videoRef} autoPlay muted playsInline onEnded={() => setIsVideoPlaying(false)} className="w-full h-full object-cover opacity-80">
              <source src="/the_test_cricket.mp4" type="video/mp4" />
            </video>
            <div className="absolute bottom-10 flex flex-col items-center">
              <span className="text-white text-xs tracking-[0.3em] uppercase mb-2">Click to Enter</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="max-w-[1500px] mx-auto relative z-10">
        
        {/* Header */}
        <header className="mb-10 flex justify-between items-end border-b border-[#E8F0E5]/10 pb-6">
          <div>
            <h1 className="text-5xl font-serif font-black tracking-tight text-white mb-2">
              <span className="text-[#8B1E1E]">Test</span> Match Center
            </h1>
            <p className="text-[#E8F0E5]/60 font-serif text-lg tracking-widest uppercase">
              {match_info.tournament} • {match_info.status_message}
            </p>
          </div>
          <div className="flex items-center gap-2 bg-[#8B1E1E]/20 text-[#FF4C4C] px-5 py-2 rounded-full border border-[#8B1E1E]/50 shadow-[0_0_15px_rgba(139,30,30,0.4)]">
            <span className="w-2 h-2 rounded-full bg-[#FF4C4C] animate-pulse" /> Live Now
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Main Scoreboard & Partnership Matrix - 8 cols */}
          <div className="lg:col-span-8 space-y-8">
            
            {/* Massive Scoreboard */}
            <div className="bg-[#050D09] border border-[#143021] rounded-3xl p-12 relative overflow-hidden shadow-2xl">
              <div className="absolute top-0 right-0 w-64 h-64 bg-[#143021] opacity-40 blur-[120px]"></div>
              
              <div className="flex justify-between items-center mb-8 border-b border-[#143021] pb-6">
                <span className="text-[#E8F0E5]/50 tracking-[0.2em] text-xs uppercase font-bold">Current Score</span>
                <span className="text-[#8B1E1E] font-black text-sm uppercase tracking-widest bg-[#8B1E1E]/10 px-3 py-1 rounded-sm">{match_info.status_text}</span>
              </div>
              
              <div className="grid grid-cols-3 items-center gap-4 text-center">
                <div className="flex flex-col items-center justify-center">
                  <h2 className="text-4xl font-serif text-white mb-4">{match_info.team1}</h2>
                  <p className="text-5xl font-black text-[#E8F0E5]">{t1Score[0]}</p>
                  <p className="text-lg text-[#E8F0E5]/50 mt-2">{t1Score[1]?.trim()}</p>
                </div>
                
                <div className="flex flex-col items-center justify-center relative">
                  <div className="absolute inset-y-0 left-1/2 w-px bg-gradient-to-b from-transparent via-[#143021] to-transparent -translate-x-1/2"></div>
                  <div className="bg-[#0A1A12] p-4 rounded-xl border border-[#143021] relative z-10 w-full mx-4 shadow-xl">
                    <p className="text-[10px] text-[#E8F0E5]/40 uppercase tracking-[0.2em] mb-1">Target</p>
                    <p className="text-3xl font-serif text-white">{match_info.target}</p>
                  </div>
                </div>
                
                <div className="flex flex-col items-center justify-center opacity-70">
                  <h2 className="text-4xl font-serif text-[#E8F0E5]/70 mb-4">{match_info.team2}</h2>
                  <p className="text-4xl font-bold text-[#E8F0E5]/50">{t2Score[0]}</p>
                  <p className="text-sm text-[#E8F0E5]/40 mt-2">{t2Score[1]?.trim()}</p>
                </div>
              </div>
            </div>

            {/* Partnership Matrix */}
            <div className="bg-[#050D09] border border-[#143021] rounded-3xl p-10 relative overflow-hidden">
              <h3 className="text-white font-serif text-2xl mb-8 flex items-center gap-3">
                <TrendingUp className="text-[#8B1E1E]" /> Partnership Matrix
              </h3>
              
              <div className="flex items-center justify-between mb-8">
                <div>
                  <p className="text-4xl font-black text-white">{match_info.partnership}</p>
                  <p className="text-xs text-[#E8F0E5]/50 uppercase tracking-[0.2em] mt-2">Current Partnership</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-black text-[#E8F0E5]/80">142 Balls</p>
                  <p className="text-xs text-[#E8F0E5]/50 uppercase tracking-[0.2em] mt-2">Time Survived</p>
                </div>
              </div>

              {/* Simulated Graph */}
              <div className="h-40 w-full border-b border-l border-[#143021] relative">
                {/* Grid Lines */}
                <div className="absolute top-1/4 w-full border-t border-[#143021] opacity-30"></div>
                <div className="absolute top-2/4 w-full border-t border-[#143021] opacity-30"></div>
                <div className="absolute top-3/4 w-full border-t border-[#143021] opacity-30"></div>
                
                {/* SVG Graph Path */}
                <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 100 100">
                  <path d="M0,90 Q10,85 20,70 T40,65 T60,40 T80,30 T100,10" fill="none" stroke="#E8F0E5" strokeWidth="2" />
                  <path d="M0,100 L0,90 Q10,85 20,70 T40,65 T60,40 T80,30 T100,10 L100,100 Z" fill="url(#grad)" opacity="0.1" />
                  <defs>
                    <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#E8F0E5" />
                      <stop offset="100%" stopColor="transparent" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>
            
          </div>

          {/* Side Panel: Pitch Degradation & Sessions - 4 cols */}
          <div className="lg:col-span-4 space-y-8">
            
            {/* Pitch Degradation Engine */}
            <div className="bg-[#050D09] border border-[#8B1E1E]/30 rounded-3xl p-8 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-[#8B1E1E] opacity-10 blur-3xl"></div>
              
              <h3 className="text-[#E8F0E5] font-serif text-xl mb-6 flex items-center gap-3">
                <ShieldAlert className="text-[#8B1E1E]" /> Pitch Degradation
              </h3>
              
              <div className="space-y-6">
                <div className="bg-[#0A1A12] p-4 rounded-xl border border-[#143021]">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-[#E8F0E5]/60 text-xs uppercase tracking-widest">Surface Wear</span>
                    <span className="text-[#FF4C4C] font-bold text-sm">Critical</span>
                  </div>
                  <div className="w-full bg-[#143021] rounded-full h-1">
                    <div className="bg-[#FF4C4C] h-1 rounded-full w-[85%]"></div>
                  </div>
                  <p className="text-white text-lg mt-3">{pitch_diagnostics.surface_wear}</p>
                </div>

                <div className="bg-[#0A1A12] p-4 rounded-xl border border-[#143021]">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-[#E8F0E5]/60 text-xs uppercase tracking-widest">Spin Deviation</span>
                    <span className="text-[#E8F0E5] font-bold text-sm">High (4.2°)</span>
                  </div>
                  <div className="w-full bg-[#143021] rounded-full h-1">
                    <div className="bg-white h-1 rounded-full w-[70%]"></div>
                  </div>
                  <p className="text-white text-lg mt-3">{pitch_diagnostics.spin_deviation}</p>
                </div>
                
                <div className="flex items-center gap-4 bg-[#0A1A12] p-4 rounded-xl border border-[#143021]">
                  <Thermometer className="text-[#E8F0E5]/50" />
                  <div>
                    <span className="text-[#E8F0E5]/60 text-xs uppercase tracking-widest block mb-1">Weather Context</span>
                    <span className="text-white">{pitch_diagnostics.weather}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Session Timeline */}
            <div className="bg-[#050D09] border border-[#143021] rounded-3xl p-8">
              <h3 className="text-white font-serif text-xl mb-6 flex items-center gap-3">
                <Clock className="text-[#E8F0E5]/50" /> Session Timeline
              </h3>
              <div className="relative border-l border-[#143021] ml-3 space-y-8 pb-4">
                {sessions.map((session: any, idx: number) => (
                  <div key={idx} className="relative pl-6">
                    <div className={`absolute -left-1.5 top-1.5 w-3 h-3 rounded-full ${session.is_live ? 'bg-[#8B1E1E] shadow-[0_0_10px_rgba(139,30,30,0.8)]' : 'bg-[#143021]'}`}></div>
                    <p className={`text-xs uppercase tracking-widest font-bold mb-1 ${session.is_live ? 'text-[#8B1E1E]' : 'text-[#E8F0E5]/50'}`}>
                      {session.name}
                    </p>
                    <p className={`text-xl font-serif ${session.is_live ? 'text-white' : 'text-[#E8F0E5]/70'}`}>{session.score}</p>
                    {session.status && (
                      <p className={`text-sm mt-1 ${session.status_color === 'red' ? 'text-[#FF4C4C]' : 'text-[#E8F0E5]/50'}`}>
                        {session.status}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
