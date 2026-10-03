import React from "react";
import { ChevronRight } from "lucide-react";
import Dropdown from "../common/Dropdown.jsx";
import CameraRankRow from "./CameraRankRow.jsx";
import { useAnalytics } from "../../hooks/useAnalytics.js";
import { toDisplayTopCamera } from "../../utils/dashboardAdapters.js";

export default function TopCamerasPanel() {
  const { data, status } = useAnalytics("today");
  const topCameras = data?.top_cameras || [];
  const maxEvents = topCameras.reduce((max, c) => Math.max(max, c.events), 0);

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5 h-full flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-base font-semibold text-gray-900">Top Cameras by Events</h2>
        <Dropdown label="Today" />
      </div>

      <div className="flex-1 divide-y divide-gray-100">
        {status === "loading" && (
          <p className="text-sm text-gray-400 py-6 text-center">Loading…</p>
        )}
        {status === "error" && (
          <p className="text-sm text-red-500 py-6 text-center">Could not load cameras.</p>
        )}
        {status === "ready" && topCameras.length === 0 && (
          <p className="text-sm text-gray-400 py-6 text-center">No events yet.</p>
        )}
        {topCameras.map((camera) => (
          <CameraRankRow key={camera.camera_id} camera={toDisplayTopCamera(camera, maxEvents)} />
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