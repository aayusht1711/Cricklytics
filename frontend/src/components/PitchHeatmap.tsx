"use client";

import React, { useState } from "react";
import { Target, ShieldAlert, Zap, AlertCircle, CircleDot } from "lucide-react";

interface PitchHeatmapProps {
  batsmanName: string;
  bowlerName: string;
  dewFactor: number;
  pitchType: string;
  wicketProb: number;
  boundaryProb: number;
}

interface DeliveryDot {
  id: number;
  ballNum: number;
  meterLength: number; // e.g. 1.2 for Yorker, 4.5 for Full, 6.8 for Good, 8.5 for Hard, 11.0 for Short
  channel: "Wide Off" | "4th Stump" | "Middle / Stumps" | "Leg Line";
  lengthName: "Yorker" | "Full" | "Good" | "Hard" | "Bouncer";
  deliveryName: string;
  speed: string;
  wicketRisk: number;
  boundaryRisk: number;
  directive: string;
  // SVG percentage coordinates for exact positioning on the pitch image
  xPct: number; // 0 to 100 on pitch strip width
  yPct: number; // 0 to 100 on pitch strip height (0% = Batter Crease 0m, 100% = Bowler End 12m+)
}

export default function PitchHeatmap({
  batsmanName,
  bowlerName,
  dewFactor,
  pitchType,
  wicketProb,
  boundaryProb
}: PitchHeatmapProps) {
  
  // Real delivery impact dots measured from Batter Crease at TOP (0m) down to Bowler End (bottom)
  const deliveries: DeliveryDot[] = [
    {
      id: 1,
      ballNum: 1,
      meterLength: 6.8,
      channel: "4th Stump",
      lengthName: "Good",
      deliveryName: "Good Length Out-Swinger (142 km/h)",
      speed: "142 km/h",
      wicketRisk: Number((wicketProb * 1.6).toFixed(1)),
      boundaryRisk: Number((boundaryProb * 0.6).toFixed(1)),
      directive: `Top of off-stump channel (6.8m). Primary wicket zone to test ${batsmanName}'s front-foot commitment.`,
      xPct: 44, // 4th Stump line
      yPct: 58  // 6.8m Good length range (between 6m and 8m)
    },
    {
      id: 2,
      ballNum: 2,
      meterLength: 7.2,
      channel: "Middle / Stumps",
      lengthName: "Good",
      deliveryName: "Seam-In Good Length (139 km/h)",
      speed: "139 km/h",
      wicketRisk: Number((wicketProb * 1.8).toFixed(1)),
      boundaryRisk: Number((boundaryProb * 0.5).toFixed(1)),
      directive: "Attack middle stump (7.2m). Highest LBW & Bowled probability before wet ball dampens seam movement.",
      xPct: 52, // Stumps line
      yPct: 62  // 7.2m Good length range
    },
    {
      id: 3,
      ballNum: 3,
      meterLength: 4.2,
      channel: "Wide Off",
      lengthName: "Full",
      deliveryName: "Full Off-Cutter Slower Ball (124 km/h)",
      speed: "124 km/h",
      wicketRisk: Number((wicketProb * 1.3).toFixed(1)),
      boundaryRisk: Number((boundaryProb * 1.2).toFixed(1)),
      directive: `Full length off-side trap (4.2m). Induce aerial drive into Catching Cover.`,
      xPct: 38, // Off-side channel
      yPct: 38  // 4.2m Full length range (between 2m and 6m)
    },
    {
      id: 4,
      ballNum: 4,
      meterLength: 8.5,
      channel: "Middle / Stumps",
      lengthName: "Hard",
      deliveryName: "Heavy Back of Length (144 km/h)",
      speed: "144 km/h",
      wicketRisk: Number((wicketProb * 1.1).toFixed(1)),
      boundaryRisk: Number((boundaryProb * 0.7).toFixed(1)),
      directive: "Hard length into hip/ribcage (8.5m). Cramp batter on back foot to restrict arms extension.",
      xPct: 48,
      yPct: 73  // 8.5m Hard length range (between 8m and Halfway)
    },
    {
      id: 5,
      ballNum: 5,
      meterLength: 8.9,
      channel: "Middle / Stumps",
      lengthName: "Hard",
      deliveryName: "Bodyline Hard Length (141 km/h)",
      speed: "141 km/h",
      wicketRisk: Number((wicketProb * 1.2).toFixed(1)),
      boundaryRisk: Number((boundaryProb * 0.6).toFixed(1)),
      directive: "Hard length targeting chest/badge (8.9m). Force defensive block into pitch.",
      xPct: 50,
      yPct: 77  // 8.9m Hard length range
    },
    {
      id: 6,
      ballNum: 6,
      meterLength: 1.4,
      channel: "4th Stump",
      lengthName: "Yorker",
      deliveryName: "Wide Toe-Crusher Yorker (145 km/h)",
      speed: "145 km/h",
      wicketRisk: Number((wicketProb * 1.5).toFixed(1)),
      boundaryRisk: Number((boundaryProb * 0.2).toFixed(1)),
      directive: `CREASE LINE YORKER (1.4m)! Spear directly at popping crease line under ${batsmanName}'s bat.`,
      xPct: 42, // Wide Off-Stump Yorker
      yPct: 14  // 1.4m Yorker range (between 0m and 2m)
    },
    {
      id: 7,
      ballNum: 7,
      meterLength: 10.5,
      channel: "Middle / Stumps",
      lengthName: "Bouncer",
      deliveryName: "Surprise Short Bouncer (146 km/h)",
      speed: "146 km/h",
      wicketRisk: Number((wicketProb * 1.4).toFixed(1)),
      boundaryRisk: Number((boundaryProb * 1.1).toFixed(1)),
      directive: "Short ball below halfway (10.5m). Force rushed hook shot into Deep Fine Leg trap.",
      xPct: 49,
      yPct: 89  // 10.5m Bouncer range (below Halfway)
    }
  ];

  const [selectedDot, setSelectedDot] = useState<DeliveryDot>(deliveries[0]);
  const [selectedLengthFilter, setSelectedLengthFilter] = useState<string>("ALL");

  const filteredDeliveries = selectedLengthFilter === "ALL" 
    ? deliveries 
    : deliveries.filter(d => d.lengthName.toUpperCase() === selectedLengthFilter.toUpperCase());

  return (
    <div className="bg-[#0B0F19] border border-[#1E293B] rounded-3xl p-6 shadow-2xl space-y-6">
      
      {/* Component Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-white/10 pb-4 gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <Target className="text-red-500" size={24} />
            <h3 className="text-xl font-black text-white uppercase tracking-tight">
              Real Broadcast Pitch PitchMap (Hawk-Eye / CricViz Standard)
            </h3>
          </div>
          <p className="text-xs text-gray-400 font-mono mt-1">
            0m Batter Stumps at Top down to 12m+ Bouncer Length • Click any delivery dot to inspect telemetry
          </p>
        </div>

        {/* Filter length buttons */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono">
          {["ALL", "Yorker", "Full", "Good", "Hard", "Bouncer"].map((lName) => (
            <button
              key={lName}
              onClick={() => setSelectedLengthFilter(lName)}
              className={`px-3 py-1.5 rounded-lg font-bold transition-all ${
                selectedLengthFilter === lName
                  ? "bg-red-600 text-white shadow-[0_0_12px_rgba(239,68,68,0.5)]"
                  : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
              }`}
            >
              {lName}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* Left Column: Broadcast Standard 2D Pitch Graphic matching User Reference Image */}
        <div className="lg:col-span-6 flex justify-center">
          <div className="relative w-full max-w-[420px] aspect-[4/5] bg-[#2e7d32] rounded-3xl overflow-hidden p-4 border-4 border-[#1b5e20] shadow-2xl">
            
            {/* Darker Outer Green Grass Field */}
            <div className="absolute inset-0 bg-gradient-to-b from-[#1b5e20] via-[#2e7d32] to-[#1b5e20] opacity-90"></div>

            {/* Central Semi-Transparent Pitch Strip */}
            <div className="relative w-7/12 h-full mx-auto bg-[#43a047]/40 border-x-2 border-white/60 flex flex-col justify-between shadow-inner">
              
              {/* TOP: BATTER END STUMPS & POPPING CREASE (0m) */}
              <div className="w-full relative border-b-4 border-white pt-2 pb-1 bg-white/10 flex justify-center shadow-md">
                <div className="flex gap-1.5 justify-center">
                  <div className="w-1.5 h-4 bg-amber-300 rounded-b-sm shadow"></div>
                  <div className="w-1.5 h-4 bg-amber-300 rounded-b-sm shadow"></div>
                  <div className="w-1.5 h-4 bg-amber-300 rounded-b-sm shadow"></div>
                </div>
              </div>

              {/* Pitch SVG Layer containing horizontal zone dividing lines, text labels & delivery landing dots */}
              <div className="relative w-full h-full">
                <svg className="w-full h-full absolute inset-0" viewBox="0 0 100 100" preserveAspectRatio="none">
                  
                  {/* Horizontal White Zone Dividing Lines */}
                  {/* Yorker Line at 2m (y = 22%) */}
                  <line x1="-50" y1="22" x2="150" y2="22" stroke="white" strokeWidth="1.2" opacity="0.8" />
                  
                  {/* Full Line at 6m (y = 48%) */}
                  <line x1="-50" y1="48" x2="150" y2="48" stroke="white" strokeWidth="1.2" opacity="0.8" />
                  
                  {/* Good Line at 8m (y = 68%) */}
                  <line x1="-50" y1="68" x2="150" y2="68" stroke="white" strokeWidth="1.2" opacity="0.8" />
                  
                  {/* Hard / Halfway Line at 10m (y = 84%) */}
                  <line x1="-50" y1="84" x2="150" y2="84" stroke="white" strokeWidth="1.2" opacity="0.8" />

                  {/* Center Line Guideline */}
                  <line x1="50" y1="0" x2="50" y2="100" stroke="white" strokeWidth="0.8" strokeDasharray="2 2" opacity="0.4" />
                </svg>

                {/* Left Side Zone Labels (Outside Pitch Strip on Left Green) */}
                <div className="absolute inset-y-0 -left-20 flex flex-col justify-between text-white font-bold font-sans text-sm pointer-events-none z-10 py-1">
                  <div className="mt-4">Yorker</div>
                  <div className="mt-8">Full</div>
                  <div className="mt-8">Good</div>
                  <div className="mt-6">Hard</div>
                </div>

                {/* Right Side Meter Labels (Outside Pitch Strip on Right Green) */}
                <div className="absolute inset-y-0 -right-20 flex flex-col justify-between text-white font-bold font-sans text-sm pointer-events-none z-10 py-1 text-right">
                  <div className="-mt-1">0m</div>
                  <div className="mt-3">2m</div>
                  <div className="mt-6">4m</div>
                  <div className="mt-6">6m</div>
                  <div className="mt-6">8m</div>
                  <div>Halfway</div>
                </div>

                {/* Magenta / Pink Plotted Delivery Impact Dots */}
                <div className="absolute inset-0 z-20">
                  {deliveries.map((dot) => {
                    const isSelected = selectedDot.id === dot.id;
                    const isFilteredOut = selectedLengthFilter !== "ALL" && dot.lengthName.toUpperCase() !== selectedLengthFilter.toUpperCase();

                    if (isFilteredOut) return null;

                    return (
                      <button
                        key={dot.id}
                        onClick={() => setSelectedDot(dot)}
                        style={{
                          left: `${dot.xPct}%`,
                          top: `${dot.yPct}%`
                        }}
                        className={`absolute -translate-x-1/2 -translate-y-1/2 group transition-all duration-200 ${
                          isSelected ? "z-30 scale-125" : "hover:scale-110"
                        }`}
                      >
                        {/* Outer Glow Ring for Selected Ball */}
                        {isSelected && (
                          <span className="absolute -inset-2 rounded-full bg-[#ff007f] opacity-60 animate-ping"></span>
                        )}
                        
                        {/* The Pink / Magenta Ball Dot */}
                        <div className={`w-4 h-4 rounded-full bg-[#ff007f] border-2 shadow-lg flex items-center justify-center font-bold text-[8px] text-white ${
                          isSelected ? "border-white ring-4 ring-[#ff007f]/50" : "border-pink-200"
                        }`}>
                          {dot.ballNum}
                        </div>

                        {/* Hover Tooltip Badge */}
                        <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-1 hidden group-hover:block bg-black/90 text-white font-mono text-[10px] px-2 py-1 rounded shadow border border-pink-500/40 whitespace-nowrap z-40">
                          Ball {dot.ballNum}: {dot.meterLength}m ({dot.lengthName})
                        </div>
                      </button>
                    );
                  })}
                </div>

              </div>

              {/* BOTTOM: BOWLER END STUMPS */}
              <div className="w-full relative border-t-2 border-white/60 pb-1 pt-1 flex justify-center">
                <div className="flex gap-1.5 justify-center">
                  <div className="w-1.5 h-3 bg-amber-200/80 rounded-t-sm"></div>
                  <div className="w-1.5 h-3 bg-amber-200/80 rounded-t-sm"></div>
                  <div className="w-1.5 h-3 bg-amber-200/80 rounded-t-sm"></div>
                </div>
              </div>

            </div>

          </div>
        </div>

        {/* Right Column: Selected Pink Ball Delivery Telemetry Card */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-black/80 border border-white/10 rounded-2xl p-6 space-y-4 shadow-xl">
            
            {/* Header for Selected Delivery */}
            <div className="flex justify-between items-start border-b border-white/10 pb-4">
              <div>
                <span className="text-[10px] font-mono text-pink-400 font-bold uppercase tracking-widest block mb-1 flex items-center gap-1.5">
                  <CircleDot size={12} className="text-[#ff007f]" /> Ball {selectedDot.ballNum} Pitch Telemetry
                </span>
                <h4 className="text-xl font-black text-white flex items-center gap-2">
                  {selectedDot.deliveryName}
                </h4>
              </div>

              <span className="text-xs px-3 py-1 rounded-full font-black font-mono uppercase bg-pink-950 text-pink-300 border border-pink-500/50 shadow-[0_0_10px_rgba(255,0,127,0.4)]">
                {selectedDot.meterLength}m ({selectedDot.lengthName.toUpperCase()})
              </span>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-3 font-mono text-xs">
              <div className="bg-white/5 p-3.5 rounded-xl border border-white/10">
                <span className="text-gray-400 text-[10px] block uppercase font-bold">Exact Pitch Length</span>
                <span className="text-white font-extrabold text-base mt-0.5 block">{selectedDot.meterLength} meters</span>
              </div>

              <div className="bg-white/5 p-3.5 rounded-xl border border-white/10">
                <span className="text-gray-400 text-[10px] block uppercase font-bold">Target Channel</span>
                <span className="text-cyan-300 font-extrabold text-base mt-0.5 block">{selectedDot.channel}</span>
              </div>

              <div className="bg-red-950/40 p-3.5 rounded-xl border border-red-500/30">
                <span className="text-red-400 text-[10px] block uppercase font-bold">Wicket Risk</span>
                <span className="text-red-300 font-black text-xl mt-0.5 block">{selectedDot.wicketRisk}%</span>
              </div>

              <div className="bg-emerald-950/40 p-3.5 rounded-xl border border-emerald-500/30">
                <span className="text-emerald-400 text-[10px] block uppercase font-bold">Scoring Threat</span>
                <span className="text-emerald-300 font-black text-xl mt-0.5 block">{selectedDot.boundaryRisk}%</span>
              </div>
            </div>

            {/* Dew Physics & Friction Commentary */}
            <div className="bg-cyan-950/40 border border-cyan-500/40 p-4 rounded-xl space-y-1 text-xs">
              <div className="flex items-center gap-2 text-cyan-300 font-mono font-bold text-[11px] uppercase">
                <Zap size={14} className="text-cyan-400" />
                Dew Surface Interaction ({dewFactor}% Dew):
              </div>
              <p className="text-gray-200 font-sans text-xs leading-relaxed">
                {dewFactor > 50 
                  ? `At ${selectedDot.meterLength}m pitch length, wet ball friction reduces seam grip by ~30%, causing ball to skid off surface with lower deviation.`
                  : `At ${selectedDot.meterLength}m length, dry pitch surface produces maximum natural seam deviation into the ${selectedDot.channel} channel.`}
              </p>
            </div>

            {/* Bowler Execution Directive */}
            <div className="bg-white/5 border border-white/10 p-4 rounded-xl space-y-1 text-xs">
              <div className="flex items-center gap-2 text-pink-400 font-mono font-bold text-[11px] uppercase">
                <ShieldAlert size={14} className="text-pink-500" />
                Execution Directive vs {batsmanName}:
              </div>
              <p className="text-gray-200 font-sans text-xs leading-relaxed font-medium">
                {selectedDot.directive}
              </p>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
