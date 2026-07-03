"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { Home, PlayCircle, Trophy, BarChart2, Video, Users, Monitor, Star, Crosshair } from "lucide-react";

const NAV_ITEMS = [
  { name: "Home", path: "/", icon: Home },
  { name: "Test", path: "/test-cricket", icon: Video },
  { name: "ODI", path: "/odi-cricket", icon: BarChart2 },
  { name: "T20", path: "/t20-cricket", icon: Trophy },
  { name: "Players", path: "/players", icon: Users },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="fixed top-0 left-0 w-full z-50 px-8 py-4 bg-black/20 backdrop-blur-xl border-b border-white/10 shadow-[0_4px_30px_rgba(0,0,0,0.1)] supports-[backdrop-filter]:bg-white/5">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-[#C9A227]">
            CRICKLYTICS
          </h1>
          <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest border border-white/10 px-2 py-0.5 rounded-full">
            V2.0
          </span>
        </div>

        {/* Navigation Links */}
        <div className="hidden lg:flex items-center gap-2 text-sm font-bold bg-white/5 p-1 rounded-full border border-white/10 backdrop-blur-md">
          <Link 
            href="/" 
            className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${pathname === "/" ? "bg-white text-black" : "text-gray-300 hover:text-white hover:bg-white/10"}`}
          >
            <Home size={16} /> Home
          </Link>
          <Link 
            href="/test-cricket" 
            className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${pathname === "/test-cricket" ? "bg-white text-black" : "text-gray-300 hover:text-white hover:bg-white/10"}`}
          >
            <Monitor size={16} /> Test
          </Link>
          <Link 
            href="/odi-cricket" 
            className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${pathname === "/odi-cricket" ? "bg-white text-black" : "text-gray-300 hover:text-white hover:bg-white/10"}`}
          >
            <BarChart2 size={16} /> ODI
          </Link>
          <Link 
            href="/t20-cricket" 
            className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${pathname === "/t20-cricket" ? "bg-white text-black" : "text-gray-300 hover:text-white hover:bg-white/10"}`}
          >
            <Trophy size={16} /> T20
          </Link>
          <Link 
            href="/players" 
            className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${pathname === "/players" ? "bg-yellow-500 text-black shadow-[0_0_15px_rgba(234,179,8,0.5)]" : "text-yellow-500 hover:text-yellow-400 hover:bg-yellow-500/10"}`}
          >
            <Users size={16} /> Players
          </Link>
          <Link 
            href="/biomechanics" 
            className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${pathname === "/biomechanics" ? "bg-cyan-500 text-black shadow-[0_0_15px_rgba(6,182,212,0.5)]" : "text-cyan-400 hover:text-cyan-300 hover:bg-cyan-500/10"}`}
          >
            <Monitor size={16} /> Biomechanics
          </Link>
          <Link 
            href="/fantasy" 
            className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${pathname === "/fantasy" ? "bg-purple-500 text-black shadow-[0_0_15px_rgba(168,85,247,0.5)]" : "text-purple-400 hover:text-purple-300 hover:bg-purple-500/10"}`}
          >
            <Star size={16} /> Fantasy AI
          </Link>
          <Link 
            href="/tactics" 
            className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${pathname === "/tactics" ? "bg-red-500 text-black shadow-[0_0_15px_rgba(239,68,68,0.5)]" : "text-red-500 hover:text-red-400 hover:bg-red-500/10"}`}
          >
            <Crosshair size={16} /> Tactics
          </Link>
        </div>

        {/* Right Action */}
        <div className="flex items-center gap-4">
          <Link href="/sign-in">
            <button className="hidden md:flex px-6 py-2 bg-white/10 hover:bg-white/20 text-white text-sm font-bold rounded-full transition-all border border-white/20 backdrop-blur-md">
              Go Premium
            </button>
          </Link>
        </div>
      </div>
    </header>
  );
}
