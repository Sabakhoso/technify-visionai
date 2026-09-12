import React, { useMemo, useState } from "react";
import { Grid2X2, Grid3X3, RefreshCcw, VideoOff } from "lucide-react";
import { useCameras } from "../hooks/useCameras.js";
import CameraFeedCard from "../components/liveview/CameraFeedCard.jsx";
import IconButton from "../components/common/IconButton.jsx";

export default function LiveView() {
  const { cameras, status, error } = useCameras();
  const [layout, setLayout] = useState("grid-2");
  const [locationFilter, setLocationFilter] = useState("All Cameras");

  const locations = useMemo(() => {
    const unique = new Set(cameras.map((camera) => camera.location).filter(Boolean));
    return ["All Cameras", ...Array.from(unique)];
  }, [cameras]);

  const visibleCameras = useMemo(() => {
    if (locationFilter === "All Cameras") return cameras;
    return cameras.filter((camera) => camera.location === locationFilter);
  }, [cameras, locationFilter]);

  if (status === "loading") {
    return (
      <div className="bg-white rounded-xl border border-gray-100 shadow-card p-8 flex items-center justify-center h-64">
        <RefreshCcw className="w-5 h-5 text-gray-400 animate-spin" />
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="bg-white rounded-xl border border-gray-100 shadow-card p-8 text-center">
        <p className="text-sm text-red-500 font-medium">Couldn't load cameras from the backend.</p>
        <p className="text-xs text-gray-400 mt-1">
          {error?.message || "Check that the API server is running and reachable."}
        </p>
      </div>
    );
  }

  if (cameras.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-100 shadow-card p-8 flex flex-col items-center justify-center h-64 gap-2 text-gray-400">
        <VideoOff className="w-6 h-6" />
        <span className="text-sm">No cameras registered yet.</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-lg font-semibold text-gray-900">
          Live View <span className="text-sm text-gray-400 font-normal">({visibleCameras.length} cameras)</span>
        </h1>
        <div className="flex items-center gap-2">
          <select
            value={locationFilter}
            onChange={(event) => setLocationFilter(event.target.value)}
            className="text-sm text-gray-600 border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-blue/30"
          >
            {locations.map((location) => (
              <option key={location} value={location}>
                {location}
              </option>
            ))}
          </select>
          <IconButton icon={Grid2X2} active={layout === "grid-2"} onClick={() => setLayout("grid-2")} />
          <IconButton icon={Grid3X3} active={layout === "grid-3"} onClick={() => setLayout("grid-3")} />
        </div>
      </div>

      <div className={`grid gap-4 ${layout === "grid-3" ? "grid-cols-3" : "grid-cols-2"}`}>
        {visibleCameras.map((camera) => (
          <CameraFeedCard key={camera.id} camera={camera} />
        ))}
      </div>
    </div>
  );
}
