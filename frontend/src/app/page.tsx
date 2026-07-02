"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { BookOpen, LogIn, Activity, Clock, Trophy, BarChart2, ChevronDown } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const [liveMatches, setLiveMatches] = useState<any[]>([]);

  useEffect(() => {
    // Initial fetch
    const fetchMatches = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8001/api/matches/live");
        if (response.ok) {
          const data = await response.json();
          setLiveMatches(data.matches);
        }
      } catch (error) {
        console.error("Failed to fetch matches:", error);
      }
    };

    fetchMatches();

    // WebSocket connection for true 0-latency updates
    const ws = new WebSocket("ws://127.0.0.1:8001/ws/live");
    
    ws.onmessage = (event) => {
      if (event.data === "UPDATE") {
        fetchMatches(); // Immediately fetch fresh data when backend signals
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  const testMatch = liveMatches.find(m => m.format === "Test");
  const t20Match = liveMatches.find(m => m.format === "T20");
  const scrollToScores = () => {
    document.getElementById('live-scores')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans pb-20">
      
      {/* FULL SCREEN CINEMATIC HERO */}
      <section className="relative w-full h-screen flex flex-col items-center justify-center overflow-hidden group">
        
        {/* Animated Background Image - Optimized for performance */}
        <motion.div 
          animate={{ scale: [1, 1.15, 1] }}
          transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
          style={{ willChange: "transform", transformOrigin: "center" }}
          className="absolute inset-0 z-0 bg-[url('https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?q=80&w=2000')] bg-cover bg-center opacity-70"
        />
        
        {/* Gradients for text readability and premium feel */}
        <div className="absolute inset-0 z-0 bg-gradient-to-b from-black/80 via-black/40 to-[#050505]" />
        <div className="absolute inset-0 z-0 bg-blue-900/10 mix-blend-overlay" />
        
        <div className="relative z-10 flex flex-col items-center text-center px-8 w-full max-w-5xl mt-[-5%]">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            <h1 className="text-6xl md:text-8xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-b from-white via-gray-200 to-gray-500 mb-6 drop-shadow-[0_10px_30px_rgba(0,0,0,0.8)]">
              Welcome to <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-[#C9A227]">Cricklytics</span>
            </h1>
            <p className="text-gray-300 text-xl md:text-2xl leading-relaxed mb-10 max-w-3xl mx-auto font-light">
              The world's most advanced, premium cricket analytics platform. Powered by AI, designed for the obsessed.
            </p>
            
            <div className="flex flex-col sm:flex-row justify-center items-center gap-6">
              <Link href="/sign-in" className="w-full sm:w-auto">
                <button className="flex items-center justify-center gap-2 bg-[#C9A227] hover:bg-[#a6821e] text-black px-10 py-5 rounded-full font-black text-lg transition-all shadow-[0_0_40px_rgba(201,162,39,0.4)] hover:scale-105 w-full sm:w-auto">
                  <LogIn size={24} /> Sign In to Premium
                </button>
              </Link>
              <button 
                onClick={scrollToScores}
                className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 backdrop-blur-xl border border-white/20 px-10 py-5 rounded-full font-bold text-lg transition-all hover:scale-105 text-white w-full sm:w-auto"
              >
                <Activity size={24} /> View Live Scores
              </button>
            </div>
          </motion.div>
        </div>

        {/* Scroll Indicator */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2, duration: 1 }}
          className="absolute bottom-10 z-10 flex flex-col items-center text-gray-400 cursor-pointer hover:text-white transition-colors"
          onClick={scrollToScores}
        >
          <span className="text-xs tracking-widest uppercase mb-2 font-bold">Scroll Down</span>
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
          >
            <ChevronDown size={24} />
          </motion.div>
        </motion.div>
      </section>

      {/* QUICK GUIDE SECTION */}
      <section className="relative z-20 w-full max-w-7xl mx-auto px-8 -mt-20 mb-20">
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="bg-[#0a0a0a]/90 border border-white/10 p-8 md:p-12 rounded-3xl backdrop-blur-2xl shadow-2xl flex flex-col md:flex-row justify-between items-center gap-10"
        >
          <div className="md:w-1/3">
            <h3 className="text-[#C9A227] font-black text-3xl mb-4 flex items-center gap-3"><BookOpen size={32}/> How to Use</h3>
            <p className="text-gray-400">Master the Cricklytics platform in three simple steps to unlock game-changing insights.</p>
          </div>
          <div className="md:w-2/3 grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="bg-white/5 p-6 rounded-2xl border border-white/5">
              <span className="text-[#C9A227] font-black text-4xl opacity-50 block mb-2">01</span>
              <h4 className="font-bold text-white mb-2">Select Format</h4>
              <p className="text-xs text-gray-400 leading-relaxed">Use the sidebar to switch between global Live Scores and the cinematic Test Cricket view.</p>
            </div>
            <div className="bg-white/5 p-6 rounded-2xl border border-white/5">
              <span className="text-[#C9A227] font-black text-4xl opacity-50 block mb-2">02</span>
              <h4 className="font-bold text-white mb-2">Analyze Zones</h4>
              <p className="text-xs text-gray-400 leading-relaxed">Dive deep into Player vs Player Battle Zones in the Test Match Center.</p>
            </div>
            <div className="bg-white/5 p-6 rounded-2xl border border-white/5">
              <span className="text-[#C9A227] font-black text-4xl opacity-50 block mb-2">03</span>
              <h4 className="font-bold text-white mb-2">Go Premium</h4>
              <p className="text-xs text-gray-400 leading-relaxed">Sign in to unlock powerful ML predictions and AI-generated commentators.</p>
            </div>
          </div>
        </motion.div>
      </section>

      {/* LIVE SCORES SECTION */}
      <section id="live-scores" className="w-full max-w-7xl mx-auto px-8">
        {/* Global Live Scores Header */}
        <div className="flex justify-between items-end border-b border-white/10 pb-6 mb-10">
          <div>
            <h2 className="text-4xl font-black tracking-tight">Global Live Scores</h2>
            <p className="text-gray-400 mt-2 text-lg">Matches happening around the world right now</p>
          </div>
          <div className="flex items-center gap-2 bg-red-500/20 text-red-400 px-5 py-2 rounded-full font-bold text-sm uppercase tracking-widest">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" /> Live Now
          </div>
        </div>

        {/* Live Scores Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Card 1: TEST CRICKET STYLE */}
          {testMatch && (
            <motion.div 
              whileHover={{ scale: 1.02 }}
              className="bg-gradient-to-br from-[#0B3D2E] to-black border border-[#C9A227]/30 rounded-3xl p-8 shadow-2xl relative overflow-hidden cursor-pointer"
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-[#C9A227] opacity-10 blur-3xl"></div>
              <div className="flex justify-between items-center mb-8">
                <span className="text-[#C9A227] font-serif font-bold tracking-widest text-xs uppercase border border-[#C9A227]/50 px-4 py-1.5 rounded-full">
                  {testMatch.format} Match
                </span>
                <span className="text-gray-300 font-serif text-sm">
                  {testMatch.status_text}
                </span>
              </div>
              
              <div className="space-y-8">
                <div className="flex justify-between items-end">
                  <div>
                    <h3 className="text-4xl font-serif text-white mb-2">{testMatch.team1}</h3>
                    <p className="text-3xl text-gray-300">{testMatch.team1_score}</p>
                  </div>
                  <div className="text-right">
                    <h3 className="text-4xl font-serif text-gray-500 mb-2">{testMatch.team2}</h3>
                    <p className="text-3xl text-gray-500">{testMatch.team2_score}</p>
                  </div>
                </div>
                
                <div className="border-t border-[#C9A227]/20 pt-6 flex justify-between text-sm text-[#F5F0E6]">
                  <div className="text-center">
                    <p className="text-[#C9A227] text-xs mb-2 uppercase tracking-wider font-bold">Target</p>
                    <p className="font-bold text-xl">{testMatch.target}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-[#C9A227] text-xs mb-2 uppercase tracking-wider font-bold">Partnership</p>
                    <p className="font-bold text-xl">{testMatch.partnership}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-[#C9A227] text-xs mb-2 uppercase tracking-wider font-bold">Status</p>
                    <p className="font-bold text-xl text-white">{testMatch.status_message}</p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Card 2: T20 STYLE */}
          {t20Match && (
            <motion.div 
              whileHover={{ scale: 1.02 }}
              className="bg-[#0f0c29] bg-gradient-to-tr from-[#0f0c29] via-[#302b63] to-[#24243e] border border-blue-500/30 rounded-3xl p-8 shadow-2xl relative overflow-hidden cursor-pointer"
            >
              <div className="absolute -top-10 -right-10 w-40 h-40 bg-pink-500 opacity-20 blur-3xl rounded-full"></div>
              <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-cyan-500 opacity-20 blur-3xl rounded-full"></div>
              
              <div className="flex justify-between items-center mb-8 relative z-10">
                <span className="bg-gradient-to-r from-pink-500 to-purple-500 text-white font-black italic tracking-widest text-xs uppercase px-4 py-1.5 rounded-sm transform -skew-x-12">
                  {t20Match.tournament}
                </span>
                <span className="text-cyan-300 font-bold text-sm flex items-center gap-1">
                  <Activity size={16}/> {t20Match.status_text}
                </span>
              </div>
              
              <div className="space-y-8 relative z-10">
                <div className="flex justify-between items-center bg-black/40 rounded-2xl p-6 border border-white/5">
                  <div>
                    <h3 className="text-3xl font-black text-white mb-2">{t20Match.team1}</h3>
                    <p className="text-4xl font-black text-pink-400">{t20Match.team1_score}</p>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="text-sm text-gray-400 font-bold uppercase tracking-widest mb-2">vs</div>
                    <div className="w-10 h-10 rounded-full border-2 border-white/20 flex items-center justify-center bg-black text-lg">
                      ⚡
                    </div>
                  </div>
                  <div className="text-right">
                    <h3 className="text-3xl font-black text-gray-400 mb-2">{t20Match.team2}</h3>
                    <p className="text-4xl font-black text-cyan-400">{t20Match.team2_score}</p>
                  </div>
                </div>
                
                <div className="flex justify-between items-center text-sm px-2">
                  <div>
                    <p className="text-gray-400 text-xs mb-2 uppercase font-bold tracking-wider">Required Rate</p>
                    <p className="font-black text-2xl text-white">{t20Match.required_rate}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-gray-400 text-xs mb-2 uppercase font-bold tracking-wider">Equation</p>
                    <p className="font-black text-2xl text-yellow-400">{t20Match.equation}</p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

        </div>
      </section>
    </div>
  );
}
