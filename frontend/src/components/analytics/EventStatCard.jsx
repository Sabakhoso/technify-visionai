import React from "react";
import Sparkline from "../common/Sparkline.jsx";

export default function EventStatCard({ label, value, color, data, labelColor }) {
  return (
    <div className="rounded-lg border border-gray-100 p-3.5">
      <p className={`text-xs font-medium mb-1 ${labelColor}`}>{label}</p>
      <p className="text-xl font-bold text-gray-900 mb-2">{value}</p>
      <Sparkline data={data} color={color} />
    </div>
  );
}
