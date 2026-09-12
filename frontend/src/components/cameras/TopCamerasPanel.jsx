import React from "react";
import { ChevronRight } from "lucide-react";
import Dropdown from "../common/Dropdown.jsx";
import CameraRankRow from "./CameraRankRow.jsx";
import { topCameras } from "../../data/mockData.js";

export default function TopCamerasPanel() {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5 h-full flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-base font-semibold text-gray-900">Top Cameras by Events</h2>
        <Dropdown label="Today" />
      </div>

      <div className="flex-1 divide-y divide-gray-100">
        {topCameras.map((camera) => (
          <CameraRankRow key={camera.id} camera={camera} />
        ))}
      </div>

      <button
        type="button"
        className="mt-4 w-full flex items-center justify-center gap-1.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg py-2.5 hover:bg-gray-50 transition-colors"
      >
        View All Cameras
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
}
