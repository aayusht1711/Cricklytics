"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Target, Search, Crosshair, Map, Info, AlertOctagon, Droplets, Wind, 
  ShieldAlert, Cpu, Zap, Compass, ArrowRight, Activity, TrendingUp, Layers,
  Award, Sliders, ChevronDown, ChevronUp, Sparkles, BarChart2, CloudRain,
  FileText, Printer, CheckCircle, RefreshCw, X
} from "lucide-react";
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis 
} from "recharts";
import Navbar from "@/components/Navbar";
import PlayerAvatar from "@/components/PlayerAvatar";
import PitchHeatmap from "@/components/PitchHeatmap";
import { getBackendUrl } from "@/utils/api";

export default function TacticalEngine() {
  const [players, setPlayers] = useState<any[]>([]);
  const [venues, setVenues] = useState<any[]>([]);

  // Matchup Nodes
  const [striker, setStriker] = useState("Virat Kohli");
  const [bowler, setBowler] = useState("Jasprit Bumrah");

  // Venue & Auto Dew Predictor State
  const [selectedVenue, setSelectedVenue] = useState("wankhede-mumbai");
  const [season, setSeason] = useState("Oct-Feb (Winter/Post-Monsoon)");
  const [venueData, setVenueData] = useState<any>(null);
  
  // Live Atmospheric Weather State
  const [weatherData, setWeatherData] = useState<any>(null);
  const [isFetchingWeather, setIsFetchingWeather] = useState(false);
  
  // Environment Context Controls
  const [format, setFormat] = useState("T20");
  const [pitch, setPitch] = useState("Flat / Batting");
  const [timing, setTiming] = useState("Night Match (7:00 PM)");
  const [dewFactor, setDewFactor] = useState(78);
  const [phase, setPhase] = useState("Death Overs");

  // Interactive 6-Ball Planner State
  const [selectedBall, setSelectedBall] = useState(0);

  // Exportable Dossier Modal State
  const [showDossierModal, setShowDossierModal] = useState(false);

  // Tabbed Results Navigation: 'overview' | 'physics' | 'analytics' | 'blueprint' | 'heatmap'
  const [activeTab, setActiveTab] = useState<"overview" | "physics" | "analytics" | "blueprint" | "heatmap">("overview");

  // UI Control Collapsible States
  const [showVenueControls, setShowVenueControls] = useState(true);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [duelResult, setDuelResult] = useState<any>(null);

  // Fetch Live Weather function
  const fetchLiveWeather = (venueKey: string) => {
    setIsFetchingWeather(true);
    fetch(getBackendUrl(`/api/tactics/live-weather?venue_key=${venueKey}`))
      .then(res => res.json())
      .then(data => {
        setWeatherData(data);
        if (data.calculated_dew_factor !== undefined) {
          setDewFactor(data.calculated_dew_factor);
        }
        setIsFetchingWeather(false);
      })
      .catch(err => {
        console.error(err);
        setIsFetchingWeather(false);
      });
  };


  // Fetch Venues & Players
  useEffect(() => {
    fetch(getBackendUrl("/api/tactics/venues"))
      .then(res => res.json())
      .then(data => {
        if (data.venues) setVenues(data.venues);
      })
      .catch(err => console.error(err));

    fetch(getBackendUrl("/api/players/"))
      .then(res => res.json())
      .then(data => {
        if (data.players) setPlayers(data.players);
      })
      .catch(err => console.error(err));
  }, []);

  // Resolve active striker & bowler player objects for photos
  const strikerObj = players.find(p => p.name.toLowerCase() === striker.toLowerCase() || p.id === striker.toLowerCase()) || {
    name: striker,
    image: "/player_photos/2.png",
    team: "India",
    role: "Batter"
  };

  const bowlerObj = players.find(p => p.name.toLowerCase() === bowler.toLowerCase() || p.id === bowler.toLowerCase()) || {
    name: bowler,
    image: "/player_photos/9.png",
    team: "India",
    role: "Bowler"
  };

  // Auto-Predict Dew and Pitch from Venue & Timing
  const autoPredictDewAndPitch = (venueKey: string, timeVal: string, seasonVal: string) => {
    fetch(getBackendUrl("/api/tactics/predict-venue-dew"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        venue_key: venueKey,
        timing: timeVal,
        season: seasonVal
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data && data.predicted_dew_factor !== undefined) {
          setVenueData(data);
          setDewFactor(data.predicted_dew_factor);
          if (data.predicted_pitch_type) setPitch(data.predicted_pitch_type);
        }
      })
      .catch(err => console.error(err));
  };

  useEffect(() => {
    autoPredictDewAndPitch(selectedVenue, timing, season);
  }, [selectedVenue, timing, season]);

  const runAnalysis = () => {
    setIsAnalyzing(true);
    fetch(getBackendUrl("/api/tactics/analyze-duel"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        batsman_id: striker,
        bowler_id: bowler,
        format: format,
        pitch: pitch,
        timing: timing,
        dew_factor: dewFactor,
        phase: phase
      })
    })
      .then(res => res.json())
      .then(data => {
        setTimeout(() => {
          setDuelResult(data);
          setIsAnalyzing(false);
        }, 1000);
      })
      .catch(err => {
        console.error(err);
        setIsAnalyzing(false);
      });
  };

  useEffect(() => {
    runAnalysis();
  }, []);

  // Generate 6-ball over flow chart data
  const getOverChartData = () => {
    if (!duelResult) return [];
    const rpo = duelResult.probabilities.expected_runs_per_over || 9.0;
    const baseRun = rpo / 6.0;
    return [
      { ball: "Ball 1", expectedRuns: Number((baseRun * 0.8).toFixed(2)), wicketThreat: Number((duelResult.probabilities.wicket_probability * 0.9).toFixed(1)) },
      { ball: "Ball 2", expectedRuns: Number((baseRun * 1.0).toFixed(2)), wicketThreat: Number((duelResult.probabilities.wicket_probability * 0.8).toFixed(1)) },
      { ball: "Ball 3", expectedRuns: Number((baseRun * 1.2).toFixed(2)), wicketThreat: Number((duelResult.probabilities.wicket_probability * 1.1).toFixed(1)) },
      { ball: "Ball 4", expectedRuns: Number((baseRun * 0.9).toFixed(2)), wicketThreat: Number((duelResult.probabilities.wicket_probability * 1.2).toFixed(1)) },
      { ball: "Ball 5", expectedRuns: Number((baseRun * 1.4).toFixed(2)), wicketThreat: Number((duelResult.probabilities.wicket_probability * 0.7).toFixed(1)) },
      { ball: "Ball 6", expectedRuns: Number((baseRun * 1.6).toFixed(2)), wicketThreat: Number((duelResult.probabilities.wicket_probability * 1.3).toFixed(1)) },
    ];
  };

  // Generate Radar matchup comparison chart data
  const getRadarData = () => {
    if (!duelResult) return [];
    return [
      { subject: "Control", Batter: 88, Bowler: 70 },
      { subject: "Power / Pace", Batter: 92, Bowler: 85 },
      { subject: "Dew Advantage", Batter: Math.min(98, 50 + dewFactor * 0.4), Bowler: Math.max(20, 80 - dewFactor * 0.5) },
      { subject: "Boundary %", Batter: duelResult.probabilities.boundary_probability * 2.2, Bowler: 40 },
      { subject: "Wicket %", Batter: 30, Bowler: duelResult.probabilities.wicket_probability * 4.0 },
    ];
  };

  return (
    <div className="min-h-screen bg-[#050507] text-[#F5F0E6] font-sans pb-20 selection:bg-red-500/30">
      <Navbar />

      <div className="pt-32 px-4 md:px-8 max-w-[1400px] mx-auto relative z-10">
        
        {/* Clean Header */}
        <header className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-end border-b border-red-900/30 pb-5">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Crosshair className="text-red-500" size={30} />
              <h1 className="text-3xl md:text-4xl font-black tracking-tighter text-white uppercase">Tactical Matchup & Dew Engine</h1>
            </div>
            <p className="text-gray-400 font-mono text-xs md:text-sm">Automated Venue Dew Prediction • Head-to-Head Dominance • Tactical Blueprint</p>
          </div>

          <div className="flex gap-2 mt-4 md:mt-0 font-mono text-xs">
            <span className="bg-red-950/60 text-red-400 border border-red-500/30 px-3 py-1.5 rounded-lg flex items-center gap-2 font-bold">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
              DEW PREDICTOR ACTIVE
            </span>
          </div>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
          
          {/* Left Panel: Streamlined Controls - 4 cols */}
          <div className="xl:col-span-4 space-y-5">
            
            {/* Collapsible Venue Predictor Section */}
            <div className="bg-black/80 border border-cyan-500/40 rounded-2xl overflow-hidden shadow-lg">
              <button 
                onClick={() => setShowVenueControls(!showVenueControls)}
                className="w-full bg-cyan-950/40 px-5 py-4 flex items-center justify-between text-cyan-400 font-mono text-xs uppercase font-bold border-b border-cyan-500/20 hover:bg-cyan-950/60 transition-all"
              >
                <span className="flex items-center gap-2"><Compass size={16}/> 1. Venue & Dew Auto-Predictor</span>
                {showVenueControls ? <ChevronUp size={16}/> : <ChevronDown size={16}/>}
              </button>

              {showVenueControls && (
                <div className="p-5 space-y-4">
                  <div>
                    <label className="text-[10px] text-cyan-300 font-mono uppercase tracking-widest font-bold mb-1 block">Venue / Stadium</label>
                    <select 
                      value={selectedVenue}
                      onChange={(e) => setSelectedVenue(e.target.value)}
                      className="w-full bg-black border border-cyan-500/30 rounded-xl p-3 text-white text-xs font-bold focus:outline-none focus:border-cyan-400"
                    >
                      {venues.length > 0 ? venues.map((v) => (
                        <option key={v.key} value={v.key} className="bg-black">
                          {v.name} ({v.country})
                        </option>
                      )) : (
                        <>
                          <option value="wankhede-mumbai" className="bg-black">Wankhede Stadium, Mumbai (India)</option>
                          <option value="eden-gardens-kolkata" className="bg-black">Eden Gardens, Kolkata (India)</option>
                          <option value="dubai-international" className="bg-black">Dubai International Stadium (UAE)</option>
                          <option value="chinnaswamy-bengaluru" className="bg-black">M. Chinnaswamy, Bengaluru (India)</option>
                          <option value="chepauk-chennai" className="bg-black">MA Chidambaram Chepauk, Chennai (India)</option>
                          <option value="mcg-melbourne" className="bg-black">MCG Melbourne (Australia)</option>
                          <option value="lords-london" className="bg-black">Lord's, London (UK)</option>
                          <option value="gaddafi-lahore" className="bg-black">Gaddafi Stadium, Lahore (Pakistan)</option>
                        </>
                      )}
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-[10px] text-cyan-300 font-mono uppercase tracking-widest font-bold mb-1 block">Start Timing</label>
                      <select 
                        value={timing}
                        onChange={(e) => setTiming(e.target.value)}
                        className="w-full bg-black border border-cyan-500/30 rounded-lg p-2.5 text-xs text-white focus:outline-none"
                      >
                        <option value="Night Match (7:00 PM)" className="bg-black">Night Match (7:00 PM)</option>
                        <option value="Day/Night (2:00 PM)" className="bg-black">Day/Night (2:00 PM)</option>
                        <option value="Day Match (9:30 AM)" className="bg-black">Day Match (9:30 AM)</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-[10px] text-cyan-300 font-mono uppercase tracking-widest font-bold mb-1 block">Season</label>
                      <select 
                        value={season}
                        onChange={(e) => setSeason(e.target.value)}
                        className="w-full bg-black border border-cyan-500/30 rounded-lg p-2.5 text-xs text-white focus:outline-none"
                      >
                        <option value="Oct-Feb (Winter/Post-Monsoon)" className="bg-black">Oct-Feb (Winter)</option>
                        <option value="Mar-Jun (Summer)" className="bg-black">Mar-Jun (Summer)</option>
                      </select>
                    </div>
                  </div>

                  {/* Live Weather Fetch Button */}
                  <button 
                    onClick={() => fetchLiveWeather(selectedVenue)}
                    disabled={isFetchingWeather}
                    className="w-full bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-500/40 text-cyan-300 font-mono text-xs font-bold py-2.5 rounded-xl flex items-center justify-center gap-2 transition-all"
                  >
                    <RefreshCw size={14} className={isFetchingWeather ? "animate-spin text-cyan-400" : "text-cyan-400"} />
                    {isFetchingWeather ? "Contacting Satellite Weather Radar..." : "Sync Live Stadium Weather (Open-Meteo)"}
                  </button>

                  {/* Weather Telemetry Details */}
                  {weatherData && (
                    <div className="bg-cyan-950/40 border border-cyan-500/40 rounded-xl p-3 text-xs space-y-2 font-mono">
                      <div className="flex justify-between items-center text-cyan-300 font-bold border-b border-cyan-500/20 pb-1.5">
                        <span className="flex items-center gap-1.5"><CloudRain size={14} /> Live Atmospheric Radar</span>
                        <span className="text-[10px] text-cyan-400 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-500/30">
                          {weatherData.is_live ? "LIVE SATELLITE" : "HISTORICAL"}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-[11px] text-gray-300">
                        <div>Temp: <span className="text-white font-bold">{weatherData.temperature_c}°C</span></div>
                        <div>Humidity: <span className="text-white font-bold">{weatherData.humidity_pct}%</span></div>
                        <div>Pressure: <span className="text-white font-bold">{weatherData.surface_pressure_hpa} hPa</span></div>
                        <div>Wind: <span className="text-white font-bold">{weatherData.wind_speed_kmh} km/h</span></div>
                      </div>
                    </div>
                  )}

                  {/* Auto Reading Badge */}
                  {venueData && (
                    <div className="bg-cyan-950/30 border border-cyan-500/30 rounded-xl p-3 text-xs space-y-1.5 font-mono">
                      <div className="flex justify-between items-center text-cyan-400 font-bold">
                        <span>Predicted Dew Factor:</span>
                        <span className="text-sm font-black text-white bg-cyan-950 px-2 py-0.5 rounded border border-cyan-500/50">{dewFactor}%</span>
                      </div>
                      <div className="flex justify-between items-center text-gray-300 text-[11px]">
                        <span>Pitch Surface:</span>
                        <span className="text-white font-bold">{pitch}</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Duel Nodes & Pitch Setup Section */}
            <div className="bg-black/80 border border-red-900/50 rounded-2xl p-5 space-y-4 shadow-lg">
              <h3 className="text-red-500 font-mono text-xs uppercase tracking-[0.2em] flex items-center gap-2 border-b border-red-900/30 pb-3 font-bold">
                <Target size={16} /> 2. Compare Any Player vs Player & Pitch Setup
              </h3>

              <div className="space-y-3">
                {/* Batter / Striker Dropdown & Search */}
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-[10px] text-gray-400 font-mono uppercase tracking-widest font-bold">Select Batter (Striker)</label>
                    <span className="text-[10px] text-red-400 font-mono font-bold">{players.length} Players Available</span>
                  </div>
                  <select
                    value={striker}
                    onChange={(e) => setStriker(e.target.value)}
                    className="w-full bg-black border border-red-500/40 rounded-xl p-3 text-white text-xs font-bold focus:outline-none focus:border-red-400"
                  >
                    {players.length > 0 ? (
                      players.map((p) => (
                        <option key={p.id || p.name} value={p.name} className="bg-black">
                          {p.name} ({p.team} • {p.role})
                        </option>
                      ))
                    ) : (
                      <>
                        <option value="Virat Kohli" className="bg-black">Virat Kohli (India • Batter)</option>
                        <option value="Rohit Sharma" className="bg-black">Rohit Sharma (India • Batter)</option>
                        <option value="Suryakumar Yadav" className="bg-black">Suryakumar Yadav (India • Batter)</option>
                        <option value="Steve Smith" className="bg-black">Steve Smith (Australia • Batter)</option>
                        <option value="Babar Azam" className="bg-black">Babar Azam (Pakistan • Batter)</option>
                        <option value="Travis Head" className="bg-black">Travis Head (Australia • Batter)</option>
                        <option value="Heinrich Klaasen" className="bg-black">Heinrich Klaasen (South Africa • Batter)</option>
                      </>
                    )}
                  </select>
                  <input 
                    type="text" 
                    value={striker}
                    onChange={(e) => setStriker(e.target.value)}
                    placeholder="Or type custom player name..."
                    className="w-full bg-white/5 border border-white/10 rounded-lg p-2 mt-1.5 text-white text-xs font-mono focus:outline-none focus:border-red-500"
                  />
                </div>

                {/* Bowler / Attack Dropdown & Search */}
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-[10px] text-gray-400 font-mono uppercase tracking-widest font-bold">Select Bowler (Attack)</label>
                    <span className="text-[10px] text-blue-400 font-mono font-bold">{players.length} Players Available</span>
                  </div>
                  <select
                    value={bowler}
                    onChange={(e) => setBowler(e.target.value)}
                    className="w-full bg-black border border-blue-500/40 rounded-xl p-3 text-white text-xs font-bold focus:outline-none focus:border-blue-400"
                  >
                    {players.length > 0 ? (
                      players.map((p) => (
                        <option key={p.id || p.name} value={p.name} className="bg-black">
                          {p.name} ({p.team} • {p.role})
                        </option>
                      ))
                    ) : (
                      <>
                        <option value="Jasprit Bumrah" className="bg-black">Jasprit Bumrah (India • Bowler)</option>
                        <option value="Mitchell Starc" className="bg-black">Mitchell Starc (Australia • Bowler)</option>
                        <option value="Rashid Khan" className="bg-black">Rashid Khan (Afghanistan • Bowler)</option>
                        <option value="Pat Cummins" className="bg-black">Pat Cummins (Australia • Bowler)</option>
                        <option value="Kagiso Rabada" className="bg-black">Kagiso Rabada (South Africa • Bowler)</option>
                        <option value="Shaheen Afridi" className="bg-black">Shaheen Afridi (Pakistan • Bowler)</option>
                      </>
                    )}
                  </select>
                  <input 
                    type="text" 
                    value={bowler}
                    onChange={(e) => setBowler(e.target.value)}
                    placeholder="Or type custom bowler name..."
                    className="w-full bg-white/5 border border-white/10 rounded-lg p-2 mt-1.5 text-white text-xs font-mono focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Pitch Surface & Match Context Controls */}
              <div className="grid grid-cols-2 gap-3 pt-1">
                <div>
                  <label className="text-[10px] text-gray-400 font-mono uppercase tracking-widest font-bold mb-1 block">Pitch Surface Type</label>
                  <select 
                    value={pitch} 
                    onChange={(e) => setPitch(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-lg p-2.5 text-xs text-white focus:outline-none font-bold"
                  >
                    <option value="Flat / Batting" className="bg-black">Flat / Batting</option>
                    <option value="Green / Seam" className="bg-black">Green / Seam</option>
                    <option value="Dry / Spin" className="bg-black">Dry / Spin</option>
                    <option value="Slow / Low" className="bg-black">Slow / Low</option>
                    <option value="Cracked / Dusty" className="bg-black">Cracked / Dusty</option>
                  </select>
                </div>

                <div>
                  <label className="text-[10px] text-gray-400 font-mono uppercase tracking-widest font-bold mb-1 block">Format</label>
                  <select 
                    value={format} 
                    onChange={(e) => setFormat(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-lg p-2.5 text-xs text-white focus:outline-none font-bold"
                  >
                    <option value="T20" className="bg-black">T20 Sprint</option>
                    <option value="ODI" className="bg-black">ODI Match</option>
                    <option value="Test" className="bg-black">Test Match</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-[10px] text-gray-400 font-mono uppercase tracking-widest font-bold mb-1 block">Match Phase</label>
                <select 
                  value={phase} 
                  onChange={(e) => setPhase(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-2.5 text-xs text-white focus:outline-none font-bold"
                >
                  <option value="Powerplay" className="bg-black">Powerplay (Overs 1-6)</option>
                  <option value="Middle Overs" className="bg-black">Middle Overs (Overs 7-15)</option>
                  <option value="Death Overs" className="bg-black">Death Overs (Overs 16-20)</option>
                </select>
              </div>

              <button 
                onClick={runAnalysis}
                disabled={isAnalyzing}
                className="w-full bg-red-600 hover:bg-red-500 text-white font-black uppercase tracking-widest py-3.5 rounded-xl transition-all shadow-[0_0_20px_rgba(239,68,68,0.3)] disabled:opacity-50 flex items-center justify-center gap-2 text-sm"
              >
                {isAnalyzing ? "Computing Physics..." : <><Zap size={16}/> Calculate Tactical Duel</>}
              </button>

            </div>
          </div>

          {/* Right Display Area: Clean Tabbed Navigation - 8 cols */}
          <div className="xl:col-span-8 space-y-6">
            
            {/* Segmented Navigation Tabs & Action Controls */}
            <div className="flex flex-wrap items-center justify-between gap-3 bg-black/60 border border-white/10 p-2 rounded-2xl backdrop-blur-xl">
              <div className="flex flex-wrap gap-2">
                {[
                  { id: "overview", label: "Overview & Duel", icon: Target },
                  { id: "physics", label: "Dew & Physics", icon: Droplets },
                  { id: "heatmap", label: "2D Pitch Heatmap", icon: Crosshair },
                  { id: "analytics", label: "Graphs & Charts", icon: BarChart2 },
                  { id: "blueprint", label: "How to Tackle Him", icon: ShieldAlert }
                ].map(tab => {
                  const IconComponent = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-xs uppercase tracking-wider transition-all ${
                        isActive 
                          ? "bg-red-600 text-white shadow-[0_0_15px_rgba(239,68,68,0.5)]" 
                          : "text-gray-400 hover:text-white hover:bg-white/5"
                      }`}
                    >
                      <IconComponent size={14} />
                      {tab.label}
                    </button>
                  );
                })}
              </div>

              {/* Export Dossier Button */}
              {duelResult && (
                <button
                  onClick={() => setShowDossierModal(true)}
                  className="bg-white/10 hover:bg-white/20 text-white border border-white/20 px-4 py-2 rounded-xl font-bold font-mono text-xs uppercase flex items-center gap-2 transition-all"
                >
                  <FileText size={14} className="text-red-400" />
                  Export Tactical Dossier (PDF)
                </button>
              )}
            </div>

            {/* Main Content Render */}
            {isAnalyzing ? (
              <div className="h-full min-h-[450px] bg-black/60 border border-red-900/30 rounded-2xl p-8 flex flex-col items-center justify-center backdrop-blur-xl">
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }} className="w-16 h-16 border-4 border-red-900/30 border-t-red-500 rounded-full" />
                <h3 className="text-lg font-black text-white uppercase tracking-widest mt-6">Computing Physics & Matchup</h3>
                <p className="text-red-400 font-mono text-xs mt-2">Simulating dew condensation, spin loss, and tactical plan...</p>
              </div>
            ) : duelResult ? (
              <AnimatePresence mode="wait">
                
                {/* TAB 1: OVERVIEW & DUEL */}
                {activeTab === "overview" && (
                  <motion.div key="overview" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-6">
                    
                    {/* H2H Versus Face-off Card */}
                    <div className="bg-gradient-to-r from-red-950/60 via-black to-blue-950/60 border border-red-500/30 rounded-3xl p-6 relative overflow-hidden shadow-2xl">
                      <div className="flex flex-col md:flex-row items-center justify-between gap-6 relative z-10">
                        
                        {/* Striker Card */}
                        <div className="flex items-center gap-4 bg-black/70 p-4 rounded-2xl border border-white/10 w-full md:w-auto flex-1">
                          <PlayerAvatar name={strikerObj.name} image={strikerObj.image} className="w-16 h-16 border-2 border-red-500" textClassName="text-base font-black" />
                          <div>
                            <span className="text-[10px] font-mono text-red-400 font-bold uppercase tracking-widest">Striker Node</span>
                            <h3 className="text-xl font-black text-white">{strikerObj.name}</h3>
                            <p className="text-xs text-gray-400 font-mono">{strikerObj.team} • {strikerObj.role}</p>
                          </div>
                        </div>

                        {/* VS Badge */}
                        <div className="flex flex-col items-center justify-center">
                          <div className="w-12 h-12 rounded-full bg-gradient-to-r from-red-600 to-blue-600 border-2 border-white flex items-center justify-center font-black text-white text-sm shadow-[0_0_20px_rgba(239,68,68,0.8)]">
                            VS
                          </div>
                          <span className="text-[9px] font-mono text-gray-400 uppercase mt-1 tracking-widest">{format} Duel</span>
                        </div>

                        {/* Bowler Card */}
                        <div className="flex items-center gap-4 bg-black/70 p-4 rounded-2xl border border-white/10 w-full md:w-auto flex-1">
                          <PlayerAvatar name={bowlerObj.name} image={bowlerObj.image} className="w-16 h-16 border-2 border-blue-500" textClassName="text-base font-black" />
                          <div>
                            <span className="text-[10px] font-mono text-blue-400 font-bold uppercase tracking-widest">Bowler Attack</span>
                            <h3 className="text-xl font-black text-white">{bowlerObj.name}</h3>
                            <p className="text-xs text-gray-400 font-mono">{bowlerObj.team} • {bowlerObj.role}</p>
                          </div>
                        </div>

                      </div>

                      {/* Winner & Rationale */}
                      <div className="mt-6 pt-5 border-t border-white/10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div>
                          <span className="text-[10px] font-mono uppercase tracking-widest text-red-400 font-bold block mb-1">
                            {duelResult.h2h_winner.margin}
                          </span>
                          <h2 className="text-2xl font-black text-white">
                            {duelResult.h2h_winner.winner_name} <span className="text-red-500">Overshadows Matchup</span>
                          </h2>
                        </div>

                        <div className="bg-black/70 border border-red-500/30 rounded-xl p-4 max-w-xl text-xs text-gray-300 leading-relaxed font-medium">
                          <span className="text-red-400 font-bold font-mono uppercase block mb-1">Tactical Rationale:</span>
                          {duelResult.h2h_winner.reasoning}
                        </div>
                      </div>
                    </div>

                    {/* NEW FEATURE: Toss Advisor & Match Core Metrics */}
                    <div className="space-y-6">
                      
                      {/* Toss Advisor & Run-Chase Advantage Calculator */}
                      <div className="bg-black/80 border border-yellow-500/30 rounded-3xl p-6 space-y-4 shadow-xl">
                        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-white/10 pb-3 gap-2">
                          <div className="flex items-center gap-2 text-yellow-400 font-mono text-sm font-bold uppercase tracking-wider">
                            <Award size={18} /> Toss Advantage & Run-Chase Impact Calculator
                          </div>
                          <span className="text-xs font-mono bg-yellow-950 text-yellow-300 border border-yellow-500/50 px-3 py-1 rounded-full font-extrabold uppercase">
                            {duelResult.toss_analytics?.recommended_toss || "WIN TOSS & BOWL FIRST"}
                          </span>
                        </div>

                        {/* Toss Win Probability Shift Bar */}
                        <div className="space-y-3 font-mono text-xs">
                          <div className="flex justify-between items-center text-gray-200">
                            <span className="font-bold">Field / Bowl First Win Probability (2nd Innings Dew Impact):</span>
                            <span className="text-emerald-400 font-extrabold text-sm">{duelResult.toss_analytics?.bowl_first_win_prob || 80}% Win Rate</span>
                          </div>

                          <div className="w-full h-4 bg-white/10 rounded-full overflow-hidden flex p-0.5 border border-white/10 shadow-inner">
                            <div className="bg-emerald-500 h-full rounded-l-full transition-all" style={{ width: `${duelResult.toss_analytics?.bowl_first_win_prob || 80}%` }}></div>
                            <div className="bg-red-500 h-full rounded-r-full transition-all" style={{ width: `${duelResult.toss_analytics?.bat_first_win_prob || 20}%` }}></div>
                          </div>

                          <div className="flex justify-between items-center text-[11px] text-gray-400 font-bold">
                            <span className="text-emerald-400">🟢 Bowl / Field First: {duelResult.toss_analytics?.bowl_first_win_prob || 80}%</span>
                            <span className="text-red-400">🔴 Bat First: {duelResult.toss_analytics?.bat_first_win_prob || 20}%</span>
                          </div>
                        </div>

                        <div className="text-xs text-gray-300 font-sans bg-white/5 p-4 rounded-2xl border border-white/5 leading-relaxed font-medium">
                          <span className="text-yellow-400 font-mono font-bold block text-[10px] uppercase mb-1">Strategic Toss Rationale:</span>
                          {duelResult.toss_analytics?.toss_rationale || "Heavy dew factor causes wet ball, reducing spin grip by over 30% in the second innings."}
                        </div>
                      </div>

                      {/* Boundary & Wicket Probabilities Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-black/80 border border-green-500/30 rounded-3xl p-6 flex flex-col justify-between space-y-3 shadow-xl">
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-green-400 font-mono font-bold uppercase tracking-wider">Boundary Potential</span>
                            <span className="text-[10px] font-mono text-gray-400 bg-green-950/50 border border-green-500/30 px-2.5 py-1 rounded-md">HIGH ACCELERATION</span>
                          </div>
                          <div>
                            <p className="text-5xl font-black text-green-400 tracking-tight">{duelResult.probabilities.boundary_probability}%</p>
                            <p className="text-xs text-gray-300 font-mono mt-2 font-bold">Expected Runs / Over: <span className="text-white font-extrabold text-sm">{duelResult.probabilities.expected_runs_per_over} RPO</span></p>
                          </div>
                        </div>

                        <div className="bg-black/80 border border-red-500/30 rounded-3xl p-6 flex flex-col justify-between space-y-3 shadow-xl">
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-red-400 font-mono font-bold uppercase tracking-wider">Wicket Threat Level</span>
                            <span className="text-[10px] font-mono text-gray-400 bg-red-950/50 border border-red-500/30 px-2.5 py-1 rounded-md">BOWLER RISK</span>
                          </div>
                          <div>
                            <p className="text-5xl font-black text-red-500 tracking-tight">{duelResult.probabilities.wicket_probability}%</p>
                            <p className="text-xs text-gray-300 font-mono mt-2 font-bold">Dot Ball Probability: <span className="text-white font-extrabold text-sm">{duelResult.probabilities.dot_ball_probability}%</span></p>
                          </div>
                        </div>
                      </div>

                    </div>

                  </motion.div>
                )}

                {/* TAB 2: DEW & PHYSICS */}
                {activeTab === "physics" && (
                  <motion.div key="physics" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-6">
                    
                    {/* Physics Step Pipeline */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="bg-black/80 border border-cyan-900/50 rounded-2xl p-5">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase">Step 1: Climate</span>
                          <Droplets size={16} className="text-cyan-400" />
                        </div>
                        <p className="text-3xl font-black text-white">{dewFactor}% Dew</p>
                        <p className="text-[11px] text-gray-400 mt-2 font-mono">{timing}</p>
                      </div>

                      <div className="bg-black/80 border border-orange-900/50 rounded-2xl p-5">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-[10px] font-mono text-orange-400 font-bold uppercase">Step 2: Spin Loss</span>
                          <Wind size={16} className="text-orange-400" />
                        </div>
                        <p className="text-3xl font-black text-orange-400">-{duelResult.physics_analytics.spin_reduction_pct}%</p>
                        <p className="text-[11px] text-gray-400 mt-2 font-mono">Finger Spin Friction Penalty</p>
                      </div>

                      <div className="bg-black/80 border border-purple-900/50 rounded-2xl p-5">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-[10px] font-mono text-purple-400 font-bold uppercase">Step 3: Seam Penalty</span>
                          <Activity size={16} className="text-purple-400" />
                        </div>
                        <p className="text-3xl font-black text-purple-400">-{duelResult.physics_analytics.seam_grip_penalty_pct}%</p>
                        <p className="text-[11px] text-gray-400 mt-2 font-mono">Cutter Deviation Reduction</p>
                      </div>

                      <div className="bg-black/80 border border-green-900/50 rounded-2xl p-5">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-[10px] font-mono text-green-400 font-bold uppercase">Step 4: Outfield Speed</span>
                          <TrendingUp size={16} className="text-green-400" />
                        </div>
                        <p className="text-3xl font-black text-green-400">+{duelResult.physics_analytics.outfield_speed_boost_pct}%</p>
                        <p className="text-[11px] text-gray-400 mt-2 font-mono">Wet Grass Acceleration</p>
                      </div>
                    </div>

                    {/* Venue Geographical Insight */}
                    <div className="bg-black/80 border border-white/10 rounded-2xl p-6 space-y-2">
                      <h4 className="text-cyan-400 font-mono text-xs uppercase font-bold tracking-wider flex items-center gap-2">
                        <Compass size={16} /> Venue Geographical & Atmosphere Profile
                      </h4>
                      <p className="text-sm text-gray-300 leading-relaxed">
                        {venueData?.venue_insight || "Coastal humidity and rapid twilight cooling cause moisture to condense heavily on the grass surface after 7:30 PM."}
                      </p>
                    </div>

                  </motion.div>
                )}

                {/* TAB 3: 2D PITCH HEATMAP */}
                {activeTab === "heatmap" && (
                  <motion.div key="heatmap" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                    <PitchHeatmap
                      batsmanName={strikerObj.name}
                      bowlerName={bowlerObj.name}
                      dewFactor={dewFactor}
                      pitchType={pitch}
                      wicketProb={duelResult.probabilities.wicket_probability}
                      boundaryProb={duelResult.probabilities.boundary_probability}
                    />
                  </motion.div>
                )}

                {/* TAB 4: ANALYTICS & CHARTS */}
                {activeTab === "analytics" && (
                  <motion.div key="analytics" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    
                    {/* 6-Ball Over Expectancy Area Chart */}
                    <div className="bg-black/80 border border-white/10 rounded-2xl p-6">
                      <h3 className="text-white font-bold text-xs uppercase tracking-widest mb-4 flex items-center gap-2 font-mono">
                        <Activity size={16} className="text-red-500" /> 6-Ball Over Expectancy & Threat Flow
                      </h3>
                      <div className="h-60 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={getOverChartData()}>
                            <defs>
                              <linearGradient id="runsGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.8}/>
                                <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                              </linearGradient>
                              <linearGradient id="wicketGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                            <XAxis dataKey="ball" stroke="#666" tick={{ fontSize: 10 }} />
                            <YAxis stroke="#666" tick={{ fontSize: 10 }} />
                            <Tooltip contentStyle={{ backgroundColor: "#000", borderColor: "#333", borderRadius: "8px", fontSize: "12px" }} />
                            <Area type="monotone" dataKey="expectedRuns" stroke="#22c55e" fillOpacity={1} fill="url(#runsGrad)" name="Exp. Runs" />
                            <Area type="monotone" dataKey="wicketThreat" stroke="#ef4444" fillOpacity={1} fill="url(#wicketGrad)" name="Wicket Threat %" />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Radar Capability Matrix */}
                    <div className="bg-black/80 border border-white/10 rounded-2xl p-6">
                      <h3 className="text-white font-bold text-xs uppercase tracking-widest mb-4 flex items-center gap-2 font-mono">
                        <Layers size={16} className="text-cyan-400" /> Player Capability Radar Under Dew
                      </h3>
                      <div className="h-60 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <RadarChart data={getRadarData()}>
                            <PolarGrid stroke="#333" />
                            <PolarAngleAxis dataKey="subject" stroke="#aaa" tick={{ fontSize: 10 }} />
                            <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#444" />
                            <Radar name={strikerObj.name} dataKey="Batter" stroke="#ef4444" fill="#ef4444" fillOpacity={0.5} />
                            <Radar name={bowlerObj.name} dataKey="Bowler" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.5} />
                            <Tooltip contentStyle={{ backgroundColor: "#000", borderColor: "#333", borderRadius: "8px", fontSize: "12px" }} />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                  </motion.div>
                )}

                {/* TAB 5: HOW TO TACKLE BLUEPRINT & 6-BALL SEQUENCE */}
                {activeTab === "blueprint" && (
                  <motion.div key="blueprint" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-6">
                    
                    {/* Interactive 6-Ball Execution Planner */}
                    {duelResult.over_sequence && (
                      <div className="bg-black/80 border border-[#1E293B] rounded-2xl p-6 shadow-xl">
                        <div className="flex justify-between items-center mb-4 border-b border-white/10 pb-3">
                          <div>
                            <h3 className="text-lg font-bold text-white flex items-center gap-2">
                              <Zap size={18} className="text-red-500" />
                              Interactive 6-Ball Execution Over Sequence
                            </h3>
                            <p className="text-xs text-gray-400 font-mono mt-0.5">Select each delivery in the over to inspect targeted lines, pace changes, and execution directives.</p>
                          </div>

                          <span className="text-xs bg-red-950 text-red-400 border border-red-500/40 px-3 py-1 rounded-full font-bold font-mono uppercase">
                            Over Plan vs {strikerObj.name}
                          </span>
                        </div>

                        {/* Ball Selector Switcher */}
                        <div className="grid grid-cols-6 gap-2 mb-5">
                          {duelResult.over_sequence.map((bItem: any, idx: number) => {
                            const isSelected = selectedBall === idx;
                            return (
                              <button
                                key={idx}
                                onClick={() => setSelectedBall(idx)}
                                className={`py-3 px-2 rounded-xl text-center font-mono transition-all border ${
                                  isSelected
                                    ? "bg-red-600 border-red-500 text-white font-black shadow-[0_0_15px_rgba(239,68,68,0.5)] scale-105"
                                    : "bg-white/5 border-white/10 text-gray-400 hover:bg-white/10 hover:text-white"
                                }`}
                              >
                                <span className="block text-[10px] uppercase opacity-75">Ball</span>
                                <span className="text-lg font-black">{idx + 1}</span>
                              </button>
                            );
                          })}
                        </div>

                        {/* Active Selected Ball Details Card */}
                        {duelResult.over_sequence[selectedBall] && (
                          <div className="bg-white/5 border border-white/10 rounded-xl p-5 space-y-3">
                            <div className="flex justify-between items-center">
                              <span className="text-xs font-mono text-red-400 font-bold uppercase tracking-wider">
                                {duelResult.over_sequence[selectedBall].title}
                              </span>
                              <span className="text-xs text-cyan-300 font-mono font-bold bg-cyan-950/60 border border-cyan-500/30 px-3 py-1 rounded-lg">
                                Target: {duelResult.over_sequence[selectedBall].target}
                              </span>
                            </div>

                            <p className="text-base font-bold text-white">
                              Delivery Type: <span className="text-red-400">{duelResult.over_sequence[selectedBall].delivery_type}</span>
                            </p>

                            <div className="grid grid-cols-2 gap-3 font-mono text-xs pt-1">
                              <div className="bg-red-950/40 border border-red-500/30 p-2.5 rounded-lg">
                                <span className="text-red-400 text-[10px] block">Wicket Risk:</span>
                                <span className="text-white font-bold text-sm">{duelResult.over_sequence[selectedBall].wicket_risk}%</span>
                              </div>
                              <div className="bg-emerald-950/40 border border-emerald-500/30 p-2.5 rounded-lg">
                                <span className="text-emerald-400 text-[10px] block">Scoring Threat:</span>
                                <span className="text-white font-bold text-sm">{duelResult.over_sequence[selectedBall].scoring_threat}%</span>
                              </div>
                            </div>

                            <div className="bg-black/60 p-3 rounded-lg border border-white/5 text-xs text-gray-300 font-medium font-sans">
                              <span className="text-amber-400 font-bold font-mono block text-[10px] uppercase mb-0.5">Execution Directive:</span>
                              {duelResult.over_sequence[selectedBall].tactical_note}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* 3-Phase Tactical Strategy */}
                    <div className="bg-black/80 border border-red-500/30 rounded-2xl p-6">
                      <h3 className="text-white font-bold text-base uppercase tracking-widest mb-6 flex items-center gap-2">
                        <ShieldAlert size={20} className="text-red-500"/> {duelResult.tackle_strategy.title} Blueprint
                      </h3>
                      
                      <div className="space-y-4">
                        {duelResult.tackle_strategy.blueprint.map((step: string, i: number) => (
                          <div key={i} className="flex items-start gap-4 bg-white/5 p-4 rounded-xl border border-white/5">
                            <span className="bg-red-950 text-red-400 border border-red-500/40 w-8 h-8 rounded-full flex items-center justify-center font-mono font-bold text-sm flex-shrink-0">
                              {i + 1}
                            </span>
                            <div>
                              <span className="text-xs font-mono text-red-400 font-bold uppercase block mb-1">
                                {i === 0 ? "Phase 1: Set-up" : i === 1 ? "Phase 2: Pressure" : "Phase 3: Wicket Ball"}
                              </span>
                              <p className="text-sm text-gray-200 font-medium">{step}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                  </motion.div>
                )}

              </AnimatePresence>
            ) : null}
          </div>

        </div>
      </div>

      {/* EXPORTABLE TACTICAL DOSSIER PRINT MODAL */}
      {showDossierModal && duelResult && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-[#0D1117] border border-red-500/40 rounded-3xl max-w-3xl w-full p-8 space-y-6 text-white shadow-2xl relative">
            
            {/* Modal Header */}
            <div className="flex justify-between items-start border-b border-red-900/40 pb-4">
              <div>
                <span className="text-xs font-mono text-red-400 uppercase font-bold tracking-widest">Cricklytics Professional Match Report</span>
                <h2 className="text-2xl font-black text-white uppercase mt-0.5">Tactical Matchup Dossier</h2>
                <p className="text-xs text-gray-400 font-mono">{strikerObj.name} vs {bowlerObj.name} • {venueData?.venue_name || "Match Stadium"}</p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => window.print()}
                  className="bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded-xl font-bold font-mono text-xs flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(239,68,68,0.5)]"
                >
                  <Printer size={14} /> Print / Save PDF
                </button>
                <button
                  onClick={() => setShowDossierModal(false)}
                  className="text-gray-400 hover:text-white bg-white/5 p-2 rounded-xl border border-white/10"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Dossier Content Sheet */}
            <div className="space-y-5 text-xs font-mono">
              {/* Summary Banner */}
              <div className="bg-gradient-to-r from-red-950/80 via-black to-blue-950/80 p-4 rounded-2xl border border-red-500/30">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-red-400 font-bold uppercase">{duelResult.h2h_winner.margin}</span>
                  <span className="text-cyan-300 font-bold">{timing} • Dew: {dewFactor}%</span>
                </div>
                <h3 className="text-xl font-black text-white">{duelResult.h2h_winner.winner_name} Overshadows Matchup</h3>
                <p className="text-gray-300 font-sans text-xs mt-2">{duelResult.h2h_winner.reasoning}</p>
              </div>

              {/* Match Probabilities & Physics */}
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-white/5 p-3 rounded-xl border border-white/10">
                  <span className="text-gray-400 block text-[10px]">Wicket Threat</span>
                  <span className="text-red-400 font-bold text-lg">{duelResult.probabilities.wicket_probability}%</span>
                </div>
                <div className="bg-white/5 p-3 rounded-xl border border-white/10">
                  <span className="text-gray-400 block text-[10px]">Boundary Rate</span>
                  <span className="text-emerald-400 font-bold text-lg">{duelResult.probabilities.boundary_probability}%</span>
                </div>
                <div className="bg-white/5 p-3 rounded-xl border border-white/10">
                  <span className="text-gray-400 block text-[10px]">Spin Grip Penalty</span>
                  <span className="text-orange-400 font-bold text-lg">-{duelResult.physics_analytics.spin_reduction_pct}%</span>
                </div>
              </div>

              {/* Toss Recommendation */}
              <div className="bg-yellow-950/30 border border-yellow-500/30 p-4 rounded-2xl">
                <span className="text-yellow-400 font-bold block uppercase mb-1">Toss Decision Strategy:</span>
                <p className="text-white font-bold">{duelResult.toss_analytics?.recommended_toss}</p>
                <p className="text-gray-300 font-sans text-xs mt-1">{duelResult.toss_analytics?.toss_rationale}</p>
              </div>

              {/* 3-Phase Tactical Directives */}
              <div className="bg-black/60 border border-white/10 p-4 rounded-2xl space-y-2">
                <span className="text-red-400 font-bold uppercase block mb-2">Tactical Blueprint Sequence:</span>
                {duelResult.tackle_strategy.blueprint.map((bp: string, bIdx: number) => (
                  <div key={bIdx} className="text-gray-300 font-sans flex items-start gap-2">
                    <span className="text-red-500 font-mono font-bold">{bIdx + 1}.</span>
                    <span>{bp}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="pt-2 border-t border-white/10 flex justify-between items-center text-[10px] text-gray-500 font-mono">
              <span>CONFIDENTIAL • CRICKLYTICS ML ENGINE</span>
              <span>Generated on {new Date().toLocaleDateString()}</span>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}

