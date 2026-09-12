import React from "react";
import { Grid2X2, Grid3X3, Maximize2 } from "lucide-react";
import Dropdown from "../common/Dropdown.jsx";
import IconButton from "../common/IconButton.jsx";
import CameraFeedCard from "./CameraFeedCard.jsx";
import { liveCameras } from "../../data/mockData.js";

export default function LiveViewPanel() {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-gray-900">Live View</h2>
        <div className="flex items-center gap-2">
          <Dropdown label="All Cameras" />
          <IconButton icon={Grid2X2} active />
          <IconButton icon={Grid3X3} />
          <IconButton icon={Maximize2} />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {liveCameras.map((camera) => (
          <CameraFeedCard key={camera.id} camera={camera} />
        ))}
      </div>
    </div>
  );
}
