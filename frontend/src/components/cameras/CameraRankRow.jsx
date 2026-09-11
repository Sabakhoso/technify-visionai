import React from "react";
import ProgressBar from "../common/ProgressBar.jsx";

export default function CameraRankRow({ camera }) {
  return (
    <div className="flex items-center gap-3 py-2.5">
      <div className="w-32 shrink-0">
        <p className="text-sm font-semibold text-gray-900 leading-tight">{camera.id}</p>
        <p className="text-xs text-gray-500">{camera.name}</p>
      </div>
      <div className="flex-1">
        <ProgressBar value={camera.events} max={camera.max} />
      </div>
      <span className="text-sm font-semibold text-gray-700 w-6 text-right">{camera.events}</span>
    </div>
  );
}
