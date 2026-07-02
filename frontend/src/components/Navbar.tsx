"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { Home, PlayCircle, Trophy, BarChart2, Video, Users } from "lucide-react";

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
        <nav className="hidden lg:flex items-center gap-2 bg-black/40 p-1.5 rounded-full border border-white/10">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.path;
            const Icon = item.icon;
            
            return (
              <Link key={item.path} href={item.path} className="relative">
                <div
                  className={`flex items-center gap-2 px-5 py-2 rounded-full cursor-pointer transition-colors z-10 relative ${
                    isActive 
                      ? "text-black font-bold" 
                      : "text-gray-300 hover:text-white font-medium"
                  }`}
                >
                  <Icon size={16} className={isActive ? "text-black" : "text-gray-400"} />
                  <span className="text-sm">{item.name}</span>
                </div>
                {isActive && (
                  <motion.div
                    layoutId="activeNavBubble"
                    className="absolute inset-0 bg-gradient-to-r from-[#C9A227] to-[#e6ca6e] rounded-full shadow-[0_0_15px_rgba(201,162,39,0.5)] z-0"
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  />
                )}
              </Link>
            );
          })}
        </nav>

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
