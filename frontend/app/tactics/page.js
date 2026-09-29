"use client";

import { useState } from 'react';

export default function TacticsPage() {
  const [batsman, setBatsman] = useState('Virat Kohli');
  const [bowler, setBowler] = useState('Jasprit Bumrah');
  const [format, setFormat] = useState('T20');
  const [pitch, setPitch] = useState('Green Top');
  const [phase, setPhase] = useState('Death Overs');
  const [dew, setDew] = useState(35);

  const [loading, setLoading] = useState(false);
  const [simResult, setSimResult] = useState(null);

  const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  const handleSimulate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSimResult(null);

    try {
      const res = await fetch(`${API_URL}/api/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          batsman_name: batsman,
          bowler_name: bowler,
          format: format,
          pitch_condition: pitch,
          match_phase: phase,
          dew_factor: Number(dew)
        })
      });
      if (res.ok) {
        const data = await res.json();
        setSimResult(data);
      }
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-8 py-12">
      <div className="border-b border-white/10 pb-6 mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-black text-white">Tactical Duel Simulator</h1>
          <p className="text-gray-400 mt-2">Simulate physical matchup probabilities & match-defining tactical duels</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Controls Form - 4 cols */}
        <div className="lg:col-span-4 bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-xl h-fit">
          <form onSubmit={handleSimulate} className="space-y-6">
            <div>
              <label className="text-xs font-bold uppercase text-gray-400 tracking-wider block mb-2">Batsman Name</label>
              <input
                type="text"
                value={batsman}
                onChange={(e) => setBatsman(e.target.value)}
                className="w-full bg-black/60 border border-white/10 rounded-xl p-3 text-white focus:outline-none focus:border-[#C9A227]"
              />
            </div>

            <div>
              <label className="text-xs font-bold uppercase text-gray-400 tracking-wider block mb-2">Bowler Name</label>
              <input
                type="text"
                value={bowler}
                onChange={(e) => setBowler(e.target.value)}
                className="w-full bg-black/60 border border-white/10 rounded-xl p-3 text-white focus:outline-none focus:border-[#C9A227]"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold uppercase text-gray-400 tracking-wider block mb-2">Format</label>
                <select
                  value={format}
                  onChange={(e) => setFormat(e.target.value)}
                  className="w-full bg-black/60 border border-white/10 rounded-xl p-3 text-white focus:outline-none focus:border-[#C9A227]"
                >
                  <option value="T20">T20</option>
                  <option value="ODI">ODI</option>
                  <option value="Test">Test</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-bold uppercase text-gray-400 tracking-wider block mb-2">Pitch Condition</label>
                <select
                  value={pitch}
                  onChange={(e) => setPitch(e.target.value)}
                  className="w-full bg-black/60 border border-white/10 rounded-xl p-3 text-white focus:outline-none focus:border-[#C9A227]"
                >
                  <option value="Green Top">Green Top</option>
                  <option value="Rank Turner">Rank Turner</option>
                  <option value="Flat Deck">Flat Deck</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs font-bold uppercase text-gray-400 tracking-wider block mb-2">Match Phase</label>
              <select
                value={phase}
                onChange={(e) => setPhase(e.target.value)}
                className="w-full bg-black/60 border border-white/10 rounded-xl p-3 text-white focus:outline-none focus:border-[#C9A227]"
              >
                <option value="Powerplay">Powerplay</option>
                <option value="Middle Overs">Middle Overs</option>
                <option value="Death Overs">Death Overs</option>
              </select>
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold uppercase text-gray-400 mb-2">
                <span>Dew Factor</span>
                <span className="text-[#C9A227]">{dew}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={dew}
                onChange={(e) => setDew(e.target.value)}
                className="w-full accent-[#C9A227]"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 bg-[#C9A227] hover:bg-[#a6821e] text-black font-black text-lg rounded-2xl transition-all shadow-[0_0_20px_rgba(201,162,39,0.3)] disabled:opacity-50"
            >
              {loading ? 'Running Simulation...' : 'Execute Tactical Simulation'}
            </button>
          </form>
        </div>

        {/* Results - 8 cols */}
        <div className="lg:col-span-8 space-y-8">
          {simResult && (
            <div className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-xl">
              <div className="flex justify-between items-center border-b border-white/10 pb-4 mb-6">
                <span className="text-xs font-black uppercase text-[#C9A227] tracking-widest">Matchup Intelligence</span>
                <span className="text-sm font-bold text-white bg-green-500/20 text-green-400 px-4 py-1 rounded-full border border-green-500/30">
                  Winner: {simResult.dominant_winner}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-6 text-center mb-8">
                <div className="bg-black/40 p-4 rounded-2xl border border-white/5">
                  <p className="text-xs text-gray-400 font-bold uppercase mb-1">Wicket Prob</p>
                  <p className="text-3xl font-black text-red-400">{simResult.wicket_probability}%</p>
                </div>
                <div className="bg-black/40 p-4 rounded-2xl border border-white/5">
                  <p className="text-xs text-gray-400 font-bold uppercase mb-1">Boundary Prob</p>
                  <p className="text-3xl font-black text-yellow-400">{simResult.boundary_probability}%</p>
                </div>
                <div className="bg-black/40 p-4 rounded-2xl border border-white/5">
                  <p className="text-xs text-gray-400 font-bold uppercase mb-1">Exp RPO</p>
                  <p className="text-3xl font-black text-cyan-400">{simResult.expected_runs_per_over}</p>
                </div>
              </div>

              <div className="bg-black/60 p-4 rounded-2xl border border-white/10 mb-8">
                <p className="text-xs font-bold uppercase text-[#C9A227] mb-1">Toss Analytics Recommendation</p>
                <p className="text-sm text-white font-medium">{simResult.toss_recommendation}</p>
              </div>

              {/* 6-ball sequence */}
              <h3 className="text-lg font-bold text-white mb-4">6-Ball Tactical Over Sequence</h3>
              <div className="space-y-3">
                {simResult.over_sequence.map((ball) => (
                  <div key={ball.ball_number} className="bg-black/40 p-4 rounded-xl border border-white/5 flex justify-between items-center text-sm">
                    <div>
                      <span className="font-bold text-[#C9A227] mr-3">Ball {ball.ball_number}</span>
                      <span className="font-semibold text-white">{ball.delivery_type}</span>
                      <p className="text-xs text-gray-400 mt-1">{ball.tactical_note}</p>
                    </div>
                    <span className="text-xs bg-white/10 text-gray-300 px-3 py-1 rounded-full font-mono">{ball.target_zone}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
