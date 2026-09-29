"use client";

import { useState, useEffect } from 'react';

export default function LiveMatchPage() {
  const [matchData, setMatchData] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const WS_URL = (process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000')
      .replace('http://', 'ws://')
      .replace('https://', 'wss://');

    const ws = new WebSocket(`${WS_URL}/ws/live-match`);

    ws.onopen = () => {
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setMatchData(data);
      } catch (err) {
        console.error('Error parsing live WS payload:', err);
      }
    };

    ws.onclose = () => {
      setConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-8 py-12">
      <div className="border-b border-white/10 pb-6 mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-black text-white">0-Latency Live Match Tracker</h1>
          <p className="text-gray-400 mt-2">Real-time WebSocket broadcast feed</p>
        </div>
        <div className={`px-4 py-2 rounded-full border text-xs font-bold uppercase tracking-wider flex items-center gap-2 ${
          connected ? 'bg-green-500/20 text-green-400 border-green-500/40' : 'bg-red-500/20 text-red-400 border-red-500/40'
        }`}>
          <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          {connected ? 'WebSocket Connected' : 'Connecting...'}
        </div>
      </div>

      {matchData ? (
        <div className="bg-gradient-to-br from-[#0f0c29] via-[#302b63] to-[#24243e] border border-purple-500/30 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
          <div className="flex justify-between items-center mb-8">
            <span className="text-[#C9A227] font-bold text-xs uppercase tracking-widest border border-[#C9A227]/40 px-4 py-1.5 rounded-full bg-black/40">
              {matchData.tournament}
            </span>
            <span className="text-red-400 font-bold text-sm">
              {matchData.status_text}
            </span>
          </div>

          <div className="bg-black/40 rounded-2xl p-6 border border-white/10 flex justify-between items-center mb-8">
            <div>
              <h2 className="text-3xl font-black text-white mb-1">{matchData.team1}</h2>
              <p className="text-3xl font-bold text-yellow-400">{matchData.team1_score}</p>
            </div>
            <div className="text-center px-4">
              <span className="text-xs text-gray-500 font-black tracking-widest block mb-1">VS</span>
              <span className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-gray-300 text-lg mx-auto">⚡</span>
            </div>
            <div className="text-right">
              <h2 className="text-3xl font-black text-gray-300 mb-1">{matchData.team2}</h2>
              <p className="text-3xl font-bold text-cyan-400">{matchData.team2_score}</p>
            </div>
          </div>

          {/* Live Ball Ticker */}
          <div className="bg-black/60 rounded-2xl p-4 border border-white/10 flex justify-between items-center mb-6">
            <span className="text-xs font-bold uppercase text-gray-400">Last Ball Outcome</span>
            <span className="w-8 h-8 rounded-full bg-yellow-500 text-black font-black text-sm flex items-center justify-center">
              {matchData.recent_ball}
            </span>
          </div>

          <div className="bg-white/5 p-4 rounded-xl border border-white/5 text-xs text-gray-300 italic">
            💬 {matchData.commentary}
          </div>
        </div>
      ) : (
        <div className="text-center py-20 text-gray-500 font-mono text-sm uppercase">Waiting for live WebSocket feed...</div>
      )}
    </div>
  );
}
