import './globals.css';
import Link from 'next/link';

export const metadata = {
  title: 'Cricklytics V2.0 - AI Cricket Scouting Platform',
  description: 'Enterprise AI Scouting & Tactical Match Intelligence Platform',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <head>
        <script src="https://cdn.tailwindcss.com"></script>
      </head>
      <body className="bg-[#050505] text-[#E2E8F0] font-sans min-h-screen flex flex-col selection:bg-[#C9A227] selection:text-black">
        {/* Navigation Header */}
        <header className="fixed top-0 left-0 w-full z-50 px-8 py-4 bg-black/40 backdrop-blur-xl border-b border-white/10 shadow-2xl">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-2xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-[#C9A227]">
                CRICKLYTICS
              </span>
              <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest border border-white/10 px-2 py-0.5 rounded-full">
                V2.0
              </span>
            </Link>

            <nav className="flex items-center gap-4 text-sm font-bold">
              <Link href="/" className="px-4 py-2 text-gray-300 hover:text-white transition-colors">
                Home
              </Link>
              <Link href="/tactics" className="px-4 py-2 text-[#C9A227] hover:text-yellow-300 transition-colors">
                Tactics & Simulator
              </Link>
              <Link href="/live" className="px-5 py-2 bg-red-500/20 text-red-400 border border-red-500/40 rounded-full hover:bg-red-500/30 transition-all text-xs font-black uppercase tracking-wider flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" /> Live Matches
              </Link>
            </nav>
          </div>
        </header>

        <main className="flex-1 pt-20">{children}</main>

        <footer className="border-t border-white/10 py-8 text-center text-xs text-gray-500">
          Cricklytics V2.0 • Enterprise AI Cricket Scouting Platform • Built with Next.js & FastAPI
        </footer>
      </body>
    </html>
  );
}
