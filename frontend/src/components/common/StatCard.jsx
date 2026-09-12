import React from "react";

export default function StatCard({ label, value, sub, icon: Icon, bg, iconColor }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5 flex items-start gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${bg}`}>
        <Icon className={`w-6 h-6 ${iconColor}`} strokeWidth={2} />
      </div>
      <div className="min-w-0">
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold text-gray-900 leading-tight mt-0.5">{value}</p>
        <div className="flex items-center gap-1.5 text-xs mt-1">
          {sub.map((s, i) => (
            <span key={i} className={s.color}>
              {s.text}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
