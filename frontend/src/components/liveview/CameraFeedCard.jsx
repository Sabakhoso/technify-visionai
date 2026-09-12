import React from "react";
import { Maximize2 } from "lucide-react";
import CameraPlayer from "./CameraPlayer.jsx";

export default function CameraFeedCard({ camera }) {
  const isLive = camera.status === "online";

  const handleFullscreen = (event) => {
    const tile = event.currentTarget.closest("[data-camera-tile]");
    if (!tile) return;
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      tile.requestFullscreen?.();
    }
  };

  return (
    <div data-camera-tile className="relative rounded-xl overflow-hidden bg-gray-900 aspect-video group">
      <CameraPlayer streamUrl={camera.stream_url} cameraName={camera.name} status={camera.status} />

      <div className="absolute top-0 left-0 right-0 flex items-center justify-between px-3 py-2.5 bg-gradient-to-b from-black/60 to-transparent pointer-events-none">
        <span className="text-white text-xs font-medium">
          {camera.id} <span className="text-white/60">•</span> {camera.name}
        </span>
        {isLive && (
          <span className="flex items-center gap-1.5 text-white text-xs font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 live-dot" />
            LIVE
          </span>
        )}
      </div>

      <button
        type="button"
        onClick={handleFullscreen}
        className="absolute bottom-2.5 right-2.5 w-7 h-7 rounded-md bg-black/40 flex items-center justify-center text-white/90 opacity-0 group-hover:opacity-100 transition-opacity"
      >
        <Maximize2 className="w-4 h-4" />
      </button>
    </div>
  );
}
