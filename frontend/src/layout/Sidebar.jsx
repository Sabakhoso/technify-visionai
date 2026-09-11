import React from "react";
import { ShieldCheck } from "lucide-react";
import { NAV_ITEMS } from "../utils/constants.js";
import SidebarItem from "../components/sidebar/SidebarItem.jsx";
import CommandCenterCard from "../components/sidebar/CommandCenterCard.jsx";

export default function Sidebar() {
  return (
    <aside className="w-[280px] shrink-0 h-screen sticky top-0 bg-navy flex flex-col">
      <div className="px-6 py-6">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg bg-brand-blue/20 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-brand-blue" strokeWidth={2.2} />
          </div>
          <span className="text-lg font-bold text-white">
            Technify <span className="text-brand-blue">VisionAI</span>
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-2 leading-snug">
          AI-Powered Video Security &amp; Intelligence Platform
        </p>
      </div>

      <nav className="flex-1 overflow-y-auto scrollbar-thin px-3 space-y-1">
        {NAV_ITEMS.map((item) => (
          <SidebarItem key={item.key} item={item} />
        ))}
      </nav>

      <div className="py-4">
        <CommandCenterCard />
        <p className="text-center text-[11px] text-slate-500 mt-4">
          © 2026 Technify. All rights reserved.
        </p>
      </div>
    </aside>
  );
}
