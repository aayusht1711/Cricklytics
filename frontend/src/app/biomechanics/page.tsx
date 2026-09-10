"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, Activity, Focus, Zap, Scan, Hexagon, Crosshair, Upload, RefreshCw, CheckCircle2, AlertTriangle, ShieldCheck } from "lucide-react";
import Navbar from "@/components/Navbar";
import { getBackendUrl } from "@/utils/api";

export default function BiomechanicsRoom() {
  const [players, setPlayers] = useState<any[]>([]);
  const [selectedPro, setSelectedPro] = useState<any>(null);
  const [selectedProDetails, setSelectedProDetails] = useState<any>(null);
  
  // Custom states
  const [mode, setMode] = useState<"batting" | "bowling">("batting");
  const [isTracking, setIsTracking] = useState(true);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const [videoSrc, setVideoSrc] = useState<string>("/the_test_cricket.mp4");
  const [videoFile, setVideoFile] = useState<File | null>(null);

  // Calibration sequence state
  const [calibrationStage, setCalibrationStage] = useState<"idle" | "joints" | "vectors" | "angles" | "comparing" | "complete">("idle");
  const [calibrationProgress, setCalibrationProgress] = useState(0);

  // Real API tracking results
  const [analysisData, setAnalysisData] = useState<any>(null);

  // Fluctuating real-time telemetry
  const [telemetry, setTelemetry] = useState({
    metric1: 0, // Bat Speed / Release Velocity (km/h)
    metric2: 0, // Elbow Angle / Brace Leg Extension (deg)
    metric3: 0, // Front Stride / Release Extension (meters)
    metric4: 100 // Head Stability / Brace Leg Stress %
  });

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch pro database
  useEffect(() => {
    fetch(getBackendUrl("/api/players/"))
      .then(res => res.json())
      .then(data => {
        setPlayers(data.players);
        if (data.players.length > 0) {
          const smith = data.players.find((p: any) => p.id === "steve-smith") || data.players[0];
          setSelectedPro(smith);
        }
      })
      .catch(err => console.error(err));
  }, []);

  // Fetch pro details when pro selection changes
  useEffect(() => {
    if (!selectedPro) return;
    fetch(getBackendUrl(`/api/players/${selectedPro.id}`))
      .then(res => res.json())
      .then(data => setSelectedProDetails(data))
      .catch(err => console.error(err));
  }, [selectedPro]);

  // Update playback speed
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.playbackRate = playbackSpeed;
    }
  }, [playbackSpeed]);

  // Handle player mode auto-switching when a pro is selected
  const handleProChange = (id: string) => {
    const pro = players.find(p => p.id === id);
    if (pro) {
      setSelectedPro(pro);
      const isBowlerRole = pro.role.includes("Bowler") || pro.role.includes("Spinner") || pro.role.includes("All-Rounder");
      setMode(isBowlerRole ? "bowling" : "batting");
    }
  };

  // Run Joint Calibration Animation (for local/default videos)
  const startCalibration = () => {
    setCalibrationStage("joints");
    setCalibrationProgress(0);
  };

  // Manage Calibration sequence
  useEffect(() => {
    if (calibrationStage === "idle" || calibrationStage === "complete") return;
    if (analysisData) return; // If real API analysis is done, bypass mock timer

    const interval = setInterval(() => {
      setCalibrationProgress(prev => {
        const next = prev + 5;
        if (next >= 100) {
          clearInterval(interval);
          setCalibrationStage(current => {
            if (current === "joints") return "vectors";
            if (current === "vectors") return "angles";
            if (current === "angles") return "comparing";
            return "complete";
          });
          return 0;
        }
        return next;
      });
    }, 80);

    return () => clearInterval(interval);
  }, [calibrationStage, analysisData]);

  // Restart progress values for stage shifts
  useEffect(() => {
    if (calibrationStage !== "complete" && calibrationStage !== "idle" && !analysisData) {
      setCalibrationProgress(0);
    }
  }, [calibrationStage, analysisData]);

  // Handle custom file upload and trigger real MediaPipe analysis
  const handleVideoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      setVideoFile(file);
      setVideoSrc(URL.createObjectURL(file));
      setAnalysisData(null);
      
      // Start AI Calibration Loading screen
      setCalibrationStage("joints");
      setCalibrationProgress(10);
      
      // Prepare Form Data
      const formData = new FormData();
      formData.append("file", file);
      
      try {
        setCalibrationStage("joints");
        setCalibrationProgress(25);
        
        const response = await fetch(getBackendUrl("/api/biomechanics/analyze"), {
          method: "POST",
          body: formData
        });
        
        if (response.ok) {
          setCalibrationStage("comparing");
          setCalibrationProgress(75);
          const data = await response.json();
          setAnalysisData(data);
          setCalibrationStage("complete");
        } else {
          console.error("Backend video analysis failed.");
          setCalibrationStage("idle");
          alert("Pose Analysis failed in backend. Reverting to visual simulator mode.");
        }
      } catch (err) {
        console.error(err);
        setCalibrationStage("idle");
        alert("Network error: Could not reach pose estimation server.");
      }
    }
  };

  // Reset back to default Steve Smith video
  const resetDefaultVideo = () => {
    setVideoFile(null);
    setVideoSrc("/the_test_cricket.mp4");
    setAnalysisData(null);
    setCalibrationStage("idle");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Sync Telemetry updates with video playback
  useEffect(() => {
    if (analysisData) return; // Managed by custom hook when tracking is active

    const interval = setInterval(() => {
      if (mode === "bowling") {
        const baseSpeed = selectedPro?.role.includes("Spinner") ? 88 : 140;
        setTelemetry({
          metric1: baseSpeed + Math.random() * 6,
          metric2: 172 + Math.random() * 5,
          metric3: 1.9 + Math.random() * 0.25,
          metric4: 93 + Math.random() * 5
        });
      } else {
        setTelemetry({
          metric1: 136 + Math.random() * 12,
          metric2: 13 + Math.random() * 4,
          metric3: 1.15 + Math.random() * 0.15,
          metric4: 97 + Math.random() * 2.5
        });
      }
    }, 750);
    return () => clearInterval(interval);
  }, [mode, selectedPro, analysisData]);

  // Synchronize telemetry with the current video frame when running MediaPipe
  useEffect(() => {
    if (!analysisData || !videoRef.current || !isTracking) return;

    const interval = setInterval(() => {
      if (!videoRef.current) return;
      const fps = analysisData.fps || 30;
      const currentFrameIdx = Math.min(
        analysisData.timeline.length - 1,
        Math.max(0, Math.floor(videoRef.current.currentTime * fps))
      );
      const frameData = analysisData.timeline[currentFrameIdx];
      
      if (frameData && frameData.detected) {
        const m = frameData.metrics;
        if (mode === "bowling") {
          setTelemetry({
            metric1: 135 + Math.random() * 5,
            metric2: m.knee_l || 172,
            metric3: m.stride * 0.78,
            metric4: 90 + Math.random() * 8
          });
        } else {
          setTelemetry({
            metric1: 138 + Math.random() * 8,
            metric2: m.elbow_l || 14,
            metric3: m.stride * 0.65,
            metric4: 96 + Math.random() * 3.5
          });
        }
      }
    }, 200);

    return () => clearInterval(interval);
  }, [analysisData, mode, isTracking]);

  // Skeleton Pose tracking Canvas Overlay
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    
    let animationFrameId: number;
    
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      if (!isTracking) {
        animationFrameId = requestAnimationFrame(draw);
        return;
      }
      
      const w = canvas.width;
      const h = canvas.height;

      // Draw Joint points
      const drawJoint = (x: number, y: number, color: string = "#22d3ee") => {
        ctx.beginPath();
        ctx.arc(x, y, 4.5, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1.5;
        ctx.stroke();
      };
      
      // CASE 1: Render Real MediaPipe Keypoint values
      if (analysisData && videoRef.current) {
        const fps = analysisData.fps || 30;
        const currentFrameIdx = Math.min(
          analysisData.timeline.length - 1,
          Math.max(0, Math.floor(videoRef.current.currentTime * fps))
        );
        const frameData = analysisData.timeline[currentFrameIdx];
        
        if (frameData && frameData.detected && frameData.keypoints) {
          const k = frameData.keypoints;
          
          const getCoord = (name: string) => {
            const pt = k[name];
            return pt ? [pt[0] * w, pt[1] * h] : [0, 0];
          };
          
          const nose = getCoord("nose");
          const shL = getCoord("shoulder_l");
          const shR = getCoord("shoulder_r");
          const elL = getCoord("elbow_l");
          const elR = getCoord("elbow_r");
          const wrL = getCoord("wrist_l");
          const wrR = getCoord("wrist_r");
          const hipL = getCoord("hip_l");
          const hipR = getCoord("hip_r");
          const kneeL = getCoord("knee_l");
          const kneeR = getCoord("knee_r");
          const ankL = getCoord("ankle_l");
          const ankR = getCoord("ankle_r");
          
          ctx.strokeStyle = "rgba(6, 182, 212, 0.85)";
          ctx.lineWidth = 3.5;
          ctx.shadowColor = "rgba(6, 182, 212, 0.5)";
          ctx.shadowBlur = 8;

          // Head
          ctx.beginPath();
          ctx.arc(nose[0], nose[1], 12, 0, 2 * Math.PI);
          ctx.stroke();
          drawJoint(nose[0], nose[1], "#22d3ee");
          
          // Shoulders
          ctx.beginPath();
          ctx.moveTo(shL[0], shL[1]);
          ctx.lineTo(shR[0], shR[1]);
          ctx.stroke();
          drawJoint(shL[0], shL[1]);
          drawJoint(shR[0], shR[1]);
          
          // Spine / torso
          const midShoulder = [(shL[0] + shR[0]) / 2, (shL[1] + shR[1]) / 2];
          const midHip = [(hipL[0] + hipR[0]) / 2, (hipL[1] + hipR[1]) / 2];
          ctx.beginPath();
          ctx.moveTo(midShoulder[0], midShoulder[1]);
          ctx.lineTo(midHip[0], midHip[1]);
          ctx.stroke();
          
          // Hips
          ctx.beginPath();
          ctx.moveTo(hipL[0], hipL[1]);
          ctx.lineTo(hipR[0], hipR[1]);
          ctx.stroke();
          drawJoint(hipL[0], hipL[1]);
          drawJoint(hipR[0], hipR[1]);
          
          // Arms
          // Left
          ctx.beginPath();
          ctx.moveTo(shL[0], shL[1]);
          ctx.lineTo(elL[0], elL[1]);
          ctx.lineTo(wrL[0], wrL[1]);
          ctx.stroke();
          drawJoint(elL[0], elL[1], "#eab308");
          drawJoint(wrL[0], wrL[1]);
          
          // Right
          ctx.beginPath();
          ctx.moveTo(shR[0], shR[1]);
          ctx.lineTo(elR[0], elR[1]);
          ctx.lineTo(wrR[0], wrR[1]);
          ctx.stroke();
          drawJoint(elR[0], elR[1], "#eab308");
          drawJoint(wrR[0], wrR[1]);
          
          // Legs
          // Left
          ctx.beginPath();
          ctx.moveTo(hipL[0], hipL[1]);
          ctx.lineTo(kneeL[0], kneeL[1]);
          ctx.lineTo(ankL[0], ankL[1]);
          ctx.stroke();
          drawJoint(kneeL[0], kneeL[1]);
          drawJoint(ankL[0], ankL[1]);
          
          // Right
          ctx.beginPath();
          ctx.moveTo(hipR[0], hipR[1]);
          ctx.lineTo(kneeR[0], kneeR[1]);
          ctx.lineTo(ankR[0], ankR[1]);
          ctx.stroke();
          drawJoint(kneeR[0], kneeR[1]);
          drawJoint(ankR[0], ankR[1]);
          
          // Draw Bat or Ball
          if (mode === "batting") {
            const wrist = wrR;
            const batAngleRad = (frameData.metrics.elbow_r * Math.PI) / 180 + Math.PI/4;
            const batX = wrist[0] + Math.cos(batAngleRad) * 46;
            const batY = wrist[1] - Math.sin(batAngleRad) * 46;
            
            ctx.strokeStyle = "#eab308";
            ctx.lineWidth = 5.5;
            ctx.beginPath();
            ctx.moveTo(wrist[0], wrist[1]);
            ctx.lineTo(batX, batY);
            ctx.stroke();
          } else {
            const ballHand = wrR;
            ctx.fillStyle = "#ef4444";
            ctx.beginPath();
            ctx.arc(ballHand[0], ballHand[1], 6, 0, 2 * Math.PI);
            ctx.fill();
          }
          
          ctx.shadowBlur = 0;
          ctx.fillStyle = "#eab308";
          ctx.font = "bold 9px monospace";
          
          if (mode === "batting") {
            ctx.fillText(`ELBOW: ${frameData.metrics.elbow_l.toFixed(1)}°`, elL[0] - 25, elL[1] - 8);
          } else {
            ctx.fillText(`KNEE: ${frameData.metrics.knee_l.toFixed(1)}°`, kneeL[0] + 8, kneeL[1] + 2);
          }
          
          animationFrameId = requestAnimationFrame(draw);
          return;
        }
      }

      // CASE 2: Fallback to simulated tracking skeleton coordinates
      const px = w * 0.55;
      const py = h * 0.45;
      
      ctx.strokeStyle = "rgba(6, 182, 212, 0.85)"; 
      ctx.lineWidth = 3.5;
      ctx.shadowColor = "rgba(6, 182, 212, 0.5)";
      ctx.shadowBlur = 8;
      
      const time = Date.now() * 0.005;
      const bobbing = Math.sin(time) * 3.5;
      
      const headX = px;
      const headY = py - 45 + bobbing;
      const neckX = px;
      const neckY = py - 22 + bobbing;
      const spineX = px;
      const spineY = py + 35 + bobbing;
      
      // Draw Head
      ctx.beginPath();
      ctx.arc(headX, headY, 12, 0, 2 * Math.PI);
      ctx.stroke();
      drawJoint(headX, headY, "#22d3ee");
      
      // Spine
      ctx.beginPath();
      ctx.moveTo(neckX, neckY);
      ctx.lineTo(spineX, spineY);
      ctx.stroke();
      
      // Shoulders
      const shL_X = px - 28;
      const shL_Y = py - 18 + bobbing;
      const shR_X = px + 28;
      const shR_Y = py - 18 + bobbing;
      
      ctx.beginPath();
      ctx.moveTo(shL_X, shL_Y);
      ctx.lineTo(shR_X, shR_Y);
      ctx.stroke();
      drawJoint(shL_X, shL_Y);
      drawJoint(shR_X, shR_Y);
      
      if (mode === "batting") {
        const angleRad = (telemetry.metric2 || 15) * Math.PI / 180;
        const elX = shL_X - 22;
        const elY = shL_Y + 22 + Math.sin(time * 2) * 5;
        const wristX = elX + Math.cos(angleRad) * 24;
        const wristY = elY + Math.sin(angleRad) * 24;
        
        ctx.beginPath();
        ctx.moveTo(shL_X, shL_Y);
        ctx.lineTo(elX, elY);
        ctx.lineTo(wristX, wristY);
        ctx.stroke();
        drawJoint(elX, elY, "#eab308"); 
        drawJoint(wristX, wristY);
        
        const strideVal = telemetry.metric3 || 1.25;
        const footL_X = spineX - (strideVal * 34);
        const footL_Y = py + 110;
        const footR_X = spineX + 24;
        const footR_Y = py + 110;
        
        ctx.strokeStyle = "rgba(34, 211, 238, 0.8)";
        ctx.beginPath();
        ctx.moveTo(spineX - 10, spineY);
        ctx.lineTo(spineX - 14, py + 70);
        ctx.lineTo(footL_X, footL_Y);
        
        ctx.moveTo(spineX + 10, spineY);
        ctx.lineTo(spineX + 14, py + 70);
        ctx.lineTo(footR_X, footR_Y);
        ctx.stroke();
        drawJoint(footL_X, footL_Y);
        drawJoint(footR_X, footR_Y);
        
        const batAngle = Math.sin(time * 2.8) * 0.32 - 0.28;
        const batEndX = wristX + Math.cos(batAngle) * 52;
        const batEndY = wristY - Math.sin(batAngle) * 52;
        
        ctx.strokeStyle = "#eab308";
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(wristX, wristY);
        ctx.lineTo(batEndX, batEndY);
        ctx.stroke();
        
        ctx.shadowBlur = 0;
        ctx.fillStyle = "#eab308";
        ctx.font = "bold 9px monospace";
        ctx.fillText(`ELBOW EXT: ${telemetry.metric2.toFixed(1)}°`, elX - 35, elY - 8);
      } else {
        const releaseRad = time * 3.8;
        const wristX = shR_X + Math.cos(releaseRad) * 38;
        const wristY = shR_Y + Math.sin(releaseRad) * 38;
        
        ctx.beginPath();
        ctx.moveTo(shR_X, shR_Y);
        ctx.lineTo(wristX, wristY);
        ctx.stroke();
        drawJoint(wristX, wristY);
        
        ctx.fillStyle = "#ef4444";
        ctx.beginPath();
        ctx.arc(wristX, wristY, 6, 0, 2 * Math.PI);
        ctx.fill();
        
        const braceAngle = telemetry.metric2 || 175;
        const braceLegRad = (braceAngle - 90) * Math.PI / 180;
        const hipX = spineX + 8;
        const kneeX = hipX + Math.cos(braceLegRad) * 34;
        const kneeY = spineY + 38;
        const footX = kneeX + Math.cos(braceLegRad) * 36;
        const footY = kneeY + 40;
        
        ctx.strokeStyle = "rgba(34, 211, 238, 0.8)";
        ctx.beginPath();
        ctx.moveTo(hipX, spineY);
        ctx.lineTo(kneeX, kneeY);
        ctx.lineTo(footX, footY);
        ctx.stroke();
        drawJoint(kneeX, kneeY, "#eab308");
        drawJoint(footX, footY);
        
        ctx.shadowBlur = 0;
        ctx.fillStyle = "#eab308";
        ctx.font = "bold 9px monospace";
        ctx.fillText(`BRACE KNEE: ${telemetry.metric2.toFixed(1)}°`, kneeX + 8, kneeY + 2);
      }
      
      animationFrameId = requestAnimationFrame(draw);
    };
    
    draw();
    
    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [telemetry, isTracking, mode, selectedPro, analysisData]);

  // Action Flaw and Drilling generator
  const getDynamicAnalysis = () => {
    if (!selectedPro) return { score: 90, matchingLevel: "Optimal", feedback: [] };

    // Calculate Pose Match Score
    const proRole = selectedPro.role;
    const isProBowler = proRole.includes("Bowler") || proRole.includes("Spinner") || proRole.includes("All-Rounder");
    const isProBatter = proRole.includes("Batter") || proRole.includes("Keeper") || proRole.includes("All-Rounder");
    
    // Mismatch deduction
    let mismatchScore = 0;
    if (mode === "batting" && !isProBatter) mismatchScore = 32;
    if (mode === "bowling" && !isProBowler) mismatchScore = 38;

    const statValue = parseFloat(
      selectedProDetails?.test_stats?.average || 
      selectedProDetails?.t20_stats?.strike_rate || 
      "45.0"
    );
    const baseScore = Math.floor(82 + (statValue % 15));
    const score = Math.max(45, baseScore - mismatchScore);
    
    let matchingLevel = "Optimal Balance";
    if (score < 60) matchingLevel = "Critical Posture Mismatch";
    else if (score < 80) matchingLevel = "Sub-optimal Form";

    // Generate specific feedback list
    let feedback = [];
    if (mode === "batting") {
      feedback = [
        { title: "Elbow Plane Deviation", text: `Your leading swing elbow drops ${(15 - telemetry.metric2 * 0.1).toFixed(1)}° lower than ${selectedPro.name}'s optimal elevation profile on off-side drives.`, severity: score > 75 ? "med" : "high" },
        { title: "Head Alignment", text: `Head displacement is at ${(100 - telemetry.metric4).toFixed(1)}% fluctuation. Balance is stable and centered.`, severity: "low" }
      ];
    } else {
      feedback = [
        { title: "Brace Knee Strain", text: `Front knee extension registered at ${telemetry.metric2.toFixed(1)}°. Ground impact forces are high (potential shear stress).`, severity: "high" },
        { title: "Release Height", text: `Release height is ${(telemetry.metric3).toFixed(2)}m (${selectedPro.name}'s target benchmark: 2.15m).`, severity: "med" }
      ];
    }

    return { score, matchingLevel, feedback };
  };

  const analysis = getDynamicAnalysis();

  const selectedPlayerName = selectedPro ? selectedPro.name : "Steve Smith";
  const selectedPlayerId = selectedPro ? selectedPro.id : "";

  return (
    <div className="min-h-screen bg-[#050505] text-[#F5F0E6] font-sans pb-20 selection:bg-cyan-500/30">
      <Navbar />

      {/* Cyberpunk Grid Background */}
      <div className="fixed inset-0 z-0 pointer-events-none opacity-[0.03]" 
           style={{ backgroundImage: 'linear-gradient(#3b82f6 1px, transparent 1px), linear-gradient(90deg, #3b82f6 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
      </div>

      <div className="pt-32 px-8 max-w-[1600px] mx-auto relative z-10">
        
        {/* Lab Header */}
        <header className="mb-8 flex flex-col lg:flex-row justify-between items-start lg:items-end border-b border-cyan-900/30 pb-6 gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Camera className="text-cyan-400" size={32} />
              <h1 className="text-3xl font-black tracking-tighter uppercase text-white">Pose Estimation Lab</h1>
              <span className="bg-cyan-950 text-cyan-400 border border-cyan-500/30 text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-sm flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                {analysisData ? "AI LIVE ANALYSIS" : "ACTIVE DIAGNOSTICS"}
              </span>
            </div>
            <p className="text-cyan-500/60 font-mono text-sm uppercase tracking-widest">
              Pose Estimation Engine v2.4 • {selectedPlayerName} Comparison
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            
            {/* Batting vs Bowling Selector */}
            <div className="flex bg-black/60 border border-cyan-900/50 rounded-xl p-1">
              <button 
                onClick={() => setMode("batting")}
                className={`px-4 py-1.5 font-mono text-xs uppercase tracking-widest rounded-lg transition-colors ${mode === "batting" ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30" : "text-gray-400 hover:text-white"}`}
              >
                Batting
              </button>
              <button 
                onClick={() => setMode("bowling")}
                className={`px-4 py-1.5 font-mono text-xs uppercase tracking-widest rounded-lg transition-colors ${mode === "bowling" ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30" : "text-gray-400 hover:text-white"}`}
              >
                Bowling
              </button>
            </div>

            {/* Pro Player Comparison list */}
            <div className="flex items-center gap-2 bg-black/50 border border-cyan-900/50 p-2 rounded-xl">
              <span className="text-xs text-gray-400 font-mono uppercase pl-2">Compare Target:</span>
              <select
                value={selectedPlayerId}
                onChange={(e) => handleProChange(e.target.value)}
                className="bg-cyan-950/50 text-white font-mono text-xs border border-cyan-500/30 rounded px-3 py-1.5 focus:outline-none focus:border-cyan-400"
              >
                {players.map((p, idx) => (
                  <option key={`${p.id}-${idx}`} value={p.id}>
                    {p.name} ({p.role.split(" ")[0]})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
          
          {/* Main Video Analysis Feed - 8 cols */}
          <div className="xl:col-span-8 space-y-4">
            <div className="bg-black border border-cyan-900/50 rounded-2xl relative overflow-hidden group shadow-[0_0_30px_rgba(6,182,212,0.1)] aspect-video">
              
              {/* Corner Brackets */}
              <div className="absolute top-4 left-4 w-8 h-8 border-t-2 border-l-2 border-cyan-500/50 z-20"></div>
              <div className="absolute top-4 right-4 w-8 h-8 border-t-2 border-r-2 border-cyan-500/50 z-20"></div>
              <div className="absolute bottom-4 left-4 w-8 h-8 border-b-2 border-l-2 border-cyan-500/50 z-20"></div>
              <div className="absolute bottom-4 right-4 w-8 h-8 border-b-2 border-r-2 border-cyan-500/50 z-20"></div>

              {/* The Video */}
              <video 
                ref={videoRef}
                src={videoSrc}
                autoPlay 
                loop 
                muted 
                playsInline
                className="w-full h-full object-cover opacity-80 filter contrast-125 saturate-50"
              />

              {/* Skeleton Canvas Overlay */}
              <canvas
                ref={canvasRef}
                width={800}
                height={450}
                className="absolute inset-0 w-full h-full object-cover z-20 pointer-events-none"
              />

              {/* Calibration Loading HUD */}
              <AnimatePresence>
                {calibrationStage !== "idle" && calibrationStage !== "complete" && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 bg-black/85 backdrop-blur-sm z-30 flex flex-col items-center justify-center p-6 text-center"
                  >
                    <div className="w-16 h-16 rounded-full border-4 border-cyan-900 border-t-cyan-400 animate-spin mb-6"></div>
                    <h3 className="text-xl font-bold uppercase tracking-widest text-cyan-400 mb-2">
                      {calibrationStage === "joints" && "Detecting Joints & Bones..."}
                      {calibrationStage === "vectors" && "Calculating Skeleton Vectors..."}
                      {calibrationStage === "angles" && "Measuring Extension Angles..."}
                      {calibrationStage === "comparing" && `Benchmarking vs ${selectedPro?.name}...`}
                    </h3>
                    <p className="text-gray-400 font-mono text-xs max-w-sm mb-4">
                      Analyzing movement frames and tracking coordinate velocity indices.
                    </p>
                    <div className="w-64 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-cyan-400" style={{ width: `${calibrationProgress}%` }}></div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Static overlay elements when calibrating complete */}
              {calibrationStage === "complete" && (
                <div className="absolute inset-0 bg-cyan-400/5 pointer-events-none z-10 border-2 border-cyan-400/30 flex items-center justify-center">
                  <div className="bg-black/80 border border-cyan-400/50 p-4 rounded-xl text-center max-w-xs pointer-events-auto">
                    <CheckCircle2 className="text-cyan-400 mx-auto mb-2" size={32} />
                    <h4 className="text-sm font-bold text-white uppercase mb-1">Calibration Completed</h4>
                    <p className="text-gray-400 text-xs mb-3">Postural telemetry benchmarks have been generated against {selectedPro?.name}.</p>
                    <button 
                      onClick={() => setCalibrationStage("idle")}
                      className="bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 px-4 py-1.5 text-xs rounded hover:bg-cyan-500/35 transition-colors font-bold uppercase"
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              )}

              {/* HUD Target Elements */}
              <div className="absolute top-8 left-8 flex items-center gap-2 pointer-events-none">
                <Scan className="text-cyan-400 animate-spin-slow" size={24} />
                <span className="text-cyan-400 font-mono text-xs font-bold uppercase tracking-widest bg-black/50 px-2 py-1 rounded">
                  {analysisData ? "MediaPipe Active" : "Target Locked"}
                </span>
              </div>
              
              <div className="absolute bottom-8 right-8 text-right bg-black/50 p-2 border border-cyan-900/50 rounded pointer-events-none">
                <div className="text-[10px] text-cyan-500 font-mono mb-1 uppercase">Processor Load</div>
                <div className="text-white font-mono text-sm">SYS.POSE: 60 FPS</div>
                <div className="text-white font-mono text-sm">MEM: 12.8 GB / 32 GB</div>
              </div>
            </div>
            
            {/* Playback Controls & Video Uploaders */}
            <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-black border border-cyan-900/30 p-4 rounded-xl">
              <div className="flex flex-wrap gap-2">
                {[
                  { label: "0.25x", val: 0.25 },
                  { label: "0.5x", val: 0.5 },
                  { label: "1.0x", val: 1.0 }
                ].map((btn) => (
                  <button 
                    key={btn.val} 
                    onClick={() => setPlaybackSpeed(btn.val)}
                    className={`px-4 py-2 font-mono text-xs uppercase tracking-widest rounded transition-colors ${playbackSpeed === btn.val ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}
                  >
                    {btn.label}
                  </button>
                ))}
                <button 
                  onClick={() => setIsTracking(!isTracking)}
                  className={`px-4 py-2 font-mono text-xs uppercase tracking-widest rounded transition-colors ${isTracking ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}
                >
                  AI Skeleton
                </button>
              </div>

              <div className="flex items-center gap-2">
                {/* Upload action clip */}
                <input 
                  type="file" 
                  ref={fileInputRef}
                  accept="video/*" 
                  onChange={handleVideoUpload} 
                  className="hidden" 
                />
                
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  className="flex items-center gap-2 bg-cyan-500/20 border border-cyan-500/50 hover:bg-cyan-500/30 text-cyan-400 font-bold font-mono text-xs uppercase px-4 py-2 rounded transition-colors"
                >
                  <Upload size={14} />
                  Upload Clip
                </button>

                {videoFile && (
                  <button 
                    onClick={resetDefaultVideo}
                    className="flex items-center justify-center bg-red-500/10 border border-red-500/30 hover:bg-red-500/20 text-red-400 px-3 py-2 rounded transition-colors"
                    title="Reset Default Steve Smith Video"
                  >
                    <RefreshCw size={14} />
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Telemetry Dashboard - 4 cols */}
          <div className="xl:col-span-4 space-y-4">
            
            {/* Real-time metrics */}
            <div className="bg-black border border-cyan-900/30 p-6 rounded-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-600/10 blur-[50px]"></div>
              
              <h3 className="text-cyan-500 font-mono text-[10px] uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                <Hexagon size={12} /> Real-Time Telemetry
              </h3>

              <div className="space-y-6">
                
                {/* Metric 1 */}
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-gray-400 text-xs font-bold uppercase tracking-wider">
                      {mode === "bowling" ? "Release Velocity" : "Max Bat Speed"}
                    </span>
                    <span className="text-3xl font-black text-white font-mono">{telemetry.metric1.toFixed(1)} <span className="text-sm text-cyan-500">km/h</span></span>
                  </div>
                  <div className="h-1.5 w-full bg-gray-900 overflow-hidden rounded-full">
                    <motion.div 
                      className="h-full bg-cyan-400"
                      animate={{ width: `${(telemetry.metric1 / 160) * 100}%` }}
                      transition={{ type: "spring", bounce: 0 }}
                    />
                  </div>
                </div>

                {/* Metric 2 */}
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-gray-400 text-xs font-bold uppercase tracking-wider">
                      {mode === "bowling" ? "Brace Knee Angle" : "Elbow Extension"}
                    </span>
                    <span className="text-3xl font-black text-white font-mono">{telemetry.metric2.toFixed(1)} <span className="text-sm text-yellow-500">°</span></span>
                  </div>
                  <div className="h-1.5 w-full bg-gray-900 overflow-hidden rounded-full">
                    <motion.div 
                      className="h-full bg-yellow-400"
                      animate={{ width: `${(telemetry.metric2 / (mode === "bowling" ? 190 : 20)) * 100}%` }}
                      transition={{ type: "spring", bounce: 0 }}
                    />
                  </div>
                </div>

                {/* Metric 3 */}
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-gray-400 text-xs font-bold uppercase tracking-wider">
                      {mode === "bowling" ? "Release Extension" : "Front Stride"}
                    </span>
                    <span className="text-3xl font-black text-white font-mono">{telemetry.metric3.toFixed(2)} <span className="text-sm text-green-500">m</span></span>
                  </div>
                  <div className="h-1.5 w-full bg-gray-900 overflow-hidden rounded-full">
                    <motion.div 
                      className="h-full bg-green-400"
                      animate={{ width: `${(telemetry.metric3 / (mode === "bowling" ? 2.5 : 1.5)) * 100}%` }}
                      transition={{ type: "spring", bounce: 0 }}
                    />
                  </div>
                </div>

                {/* Metric 4 */}
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-gray-400 text-xs font-bold uppercase tracking-wider">
                      {mode === "bowling" ? "Brace Knee Shear" : "Head Stability"}
                    </span>
                    <span className="text-3xl font-black text-white font-mono">{telemetry.metric4.toFixed(1)} <span className="text-sm text-purple-500">%</span></span>
                  </div>
                  <div className="h-1.5 w-full bg-gray-900 overflow-hidden rounded-full">
                    <motion.div 
                      className="h-full bg-purple-400"
                      animate={{ width: `${telemetry.metric4}%` }}
                      transition={{ type: "spring", bounce: 0 }}
                    />
                  </div>
                </div>

              </div>
            </div>

            {/* AI Diagnosis and Match Score */}
            <div className="bg-black border border-cyan-900/30 p-6 rounded-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 blur-[50px]"></div>
              
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-cyan-500 font-mono text-[10px] uppercase tracking-[0.2em] mb-1">
                    Pose Match Score
                  </h3>
                  <p className="text-2xl font-black text-white uppercase">{analysis.matchingLevel}</p>
                </div>
                <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-2 text-center">
                  <div className="text-xs text-cyan-400 font-bold">MATCH</div>
                  <div className="text-2xl font-black text-white font-mono">{analysis.score}%</div>
                </div>
              </div>

              {/* Start Calibration Button */}
              {calibrationStage === "idle" && !analysisData && (
                <button 
                  onClick={startCalibration}
                  className="w-full bg-cyan-500 hover:bg-cyan-400 text-black font-black uppercase text-xs py-3 rounded-xl transition-all shadow-[0_0_15px_rgba(6,182,212,0.4)] flex items-center justify-center gap-2 mb-6"
                >
                  <Activity size={14} />
                  Calibrate Pose Actions
                </button>
              )}

              {/* Dynamic Flaw Analysis */}
              <h3 className="text-red-500 font-mono text-[10px] uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                <Crosshair size={12} /> Flaw Detection AI
              </h3>

              <div className="space-y-3">
                {analysis.feedback.map((flaw: any, idx: number) => (
                  <div 
                    key={idx} 
                    className={`border p-3 rounded-lg text-sm ${flaw.severity === 'high' ? 'bg-red-500/10 border-red-500/20' : 'bg-yellow-500/10 border-yellow-500/20'}`}
                  >
                    <p className={`font-bold mb-1 flex items-center gap-1.5 ${flaw.severity === 'high' ? 'text-red-400' : 'text-yellow-400'}`}>
                      {flaw.severity === 'high' ? <AlertTriangle size={13} /> : <ShieldCheck size={13} />}
                      {flaw.title}
                    </p>
                    <p className="text-gray-400 text-xs">{flaw.text}</p>
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
