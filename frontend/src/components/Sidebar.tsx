"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { Home, PlayCircle, Trophy, BarChart2, Video } from "lucide-react";

const NAV_ITEMS = [
  { name: "Home", path: "/", icon: Home },
  { name: "Test Cricket", path: "/test-cricket", icon: Video },
  { name: "Live Scores", path: "/live-scores", icon: PlayCircle },
  { name: "Player Analysis", path: "/player-analysis", icon: BarChart2 },
  { name: "Team Analysis", path: "/team-analysis", icon: Trophy },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-screen fixed left-0 top-0 bg-white/5 backdrop-blur-2xl border-r border-white/10 p-6 flex flex-col z-50">
      <div className="mb-10">
        <h1 className="text-2xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-[#C9A227]">
          CRICKLYTICS
        </h1>
        <p className="text-xs text-gray-400 tracking-widest mt-1">V2.0</p>
      </div>

      <nav className="flex-1 space-y-2">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.path;
          const Icon = item.icon;
          
          return (
            <Link key={item.path} href={item.path}>
              <motion.div
                whileHover={{ x: 5, backgroundColor: "rgba(255,255,255,0.1)" }}
                whileTap={{ scale: 0.95 }}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-colors ${
                  isActive 
                    ? "bg-white/10 text-[#C9A227] border border-white/10 shadow-[0_0_15px_rgba(201,162,39,0.3)]" 
                    : "text-gray-300 hover:text-white"
                }`}
              >
                <Icon size={18} className={isActive ? "text-[#C9A227]" : "text-gray-400"} />
                <span className="font-medium">{item.name}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute left-0 w-1 h-8 bg-[#C9A227] rounded-r-full"
                  />
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto">
        <div className="p-4 bg-gradient-to-br from-[#0B3D2E] to-black border border-white/10 rounded-2xl">
          <h3 className="text-sm font-bold text-white mb-1">Go Premium</h3>
          <p className="text-xs text-gray-400 mb-3">Unlock advanced ML predictors and AI scouting.</p>
          <button className="w-full py-2 bg-[#C9A227] hover:bg-[#a6821e] text-black font-bold rounded-lg text-sm transition-colors shadow-[0_0_15px_rgba(201,162,39,0.5)]">
            Upgrade
          </button>
        </div>
      </div>
    </aside>
  );
}
