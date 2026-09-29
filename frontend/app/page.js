"use client";

import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#050505] text-white">
      {/* Hero Section */}
      <section className="relative h-[85vh] flex items-center justify-center overflow-hidden px-8">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-900/10 via-black/60 to-[#050505] z-0 pointer-events-none" />
        
        <div className="relative z-10 max-w-5xl mx-auto text-center">
          <h1 className="text-6xl md:text-8xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-b from-white via-gray-200 to-gray-500 mb-6 drop-shadow-2xl">
            Welcome to <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-[#C9A227]">Cricklytics V2.0</span>
          </h1>
          <p className="text-gray-300 text-xl md:text-2xl leading-relaxed mb-10 max-w-3xl mx-auto font-light">
            Decode every seam, spin, and match-defining duel. Built for players, strategists, and cricket purists.
          </p>

          <div className="flex flex-col sm:flex-row justify-center items-center gap-6">
            <Link href="/tactics">
              <button className="px-10 py-5 bg-[#C9A227] hover:bg-[#a6821e] text-black rounded-full font-black text-lg transition-all shadow-[0_0_30px_rgba(201,162,39,0.4)] hover:scale-105">
                Launch Tactical Simulator &rarr;
              </button>
            </Link>
            <Link href="/live">
              <button className="px-10 py-5 bg-white/10 hover:bg-white/20 text-white rounded-full font-bold text-lg transition-all border border-white/20 hover:scale-105">
                Track Live Match &rarr;
              </button>
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section className="max-w-7xl mx-auto px-8 py-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-xl">
          <span className="text-[#C9A227] text-4xl font-black block mb-4">01</span>
          <h3 className="text-2xl font-bold text-white mb-2">Tactical Duel Simulator</h3>
          <p className="text-gray-400 text-sm leading-relaxed">
            Simulate Batter vs Bowler duels across pitch conditions, match phases, and environmental dew factors.
          </p>
        </div>
        <div className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-xl">
          <span className="text-[#C9A227] text-4xl font-black block mb-4">02</span>
          <h3 className="text-2xl font-bold text-white mb-2">AI Biomechanical Scan</h3>
          <p className="text-gray-400 text-sm leading-relaxed">
            PyTorch deep learning model analyzing video motion vectors to identify head tilt and bat-pad gaps.
          </p>
        </div>
        <div className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-xl">
          <span className="text-[#C9A227] text-4xl font-black block mb-4">03</span>
          <h3 className="text-2xl font-bold text-white mb-2">0-Latency Live Ticker</h3>
          <p className="text-gray-400 text-sm leading-relaxed">
            Real-time ball-by-ball score tracking powered by WebSockets for ongoing international matches.
          </p>
        </div>
      </section>
    </div>
  );
}
