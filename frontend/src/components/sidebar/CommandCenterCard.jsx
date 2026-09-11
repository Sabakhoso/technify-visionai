import React from "react";
import { Radar } from "lucide-react";

export default function CommandCenterCard() {
  return (
    <div className="mx-2 rounded-xl bg-gradient-to-b from-navy-light to-navy border border-white/10 p-4 text-center">
      <div className="w-11 h-11 mx-auto rounded-full bg-brand-blue/20 flex items-center justify-center mb-3">
        <Radar className="w-6 h-6 text-brand-blue" strokeWidth={2} />
      </div>
      <p className="text-sm font-semibold text-white leading-tight">
        VisionAI <span className="text-brand-blue">Command Center</span>
      </p>
      <div className="flex items-center justify-center gap-1.5 mt-2 text-xs text-slate-400">
        <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
        All systems operational
      </div>
    </div>
  );
}
