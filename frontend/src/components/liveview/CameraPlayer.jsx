import React, { useEffect, useRef, useState } from "react";
import Hls from "hls.js";
import { VideoOff, Loader2, AlertTriangle } from "lucide-react";

/**
 * Plays a real HLS stream (from an RTSP-to-HLS gateway like MediaMTX or
 * go2rtc sitting in front of the camera). Falls back to native HLS on
 * Safari/iOS, uses hls.js everywhere else. No image/gif placeholders.
 */
export default function CameraPlayer({ streamUrl, cameraName, status }) {
  const videoRef = useRef(null);
  const hlsRef = useRef(null);
  const [playerState, setPlayerState] = useState("loading"); // loading | playing | error | offline

  useEffect(() => {
    if (status === "offline" || !streamUrl) {
      setPlayerState("offline");
      return;
    }

    const video = videoRef.current;
    if (!video) return;

    setPlayerState("loading");

    // Safari / iOS: native HLS support, no hls.js needed
    if (video.canPlayType("application/vnd.apple.mpegurl")) {
      const onLoaded = () => setPlayerState("playing");
      const onError = () => setPlayerState("error");
      video.src = streamUrl;
      video.addEventListener("loadedmetadata", onLoaded);
      video.addEventListener("error", onError);
      video.play().catch(() => {});
      return () => {
        video.removeEventListener("loadedmetadata", onLoaded);
        video.removeEventListener("error", onError);
      };
    }

    if (Hls.isSupported()) {
      const hls = new Hls({
        liveSyncDuration: 2,
        liveMaxLatencyDuration: 6,
      });
      hlsRef.current = hls;

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        setPlayerState("playing");
        video.play().catch(() => {});
      });

      hls.on(Hls.Events.ERROR, (_event, data) => {
        if (data.fatal) setPlayerState("error");
      });

      hls.loadSource(streamUrl);
      hls.attachMedia(video);

      return () => {
        hls.destroy();
        hlsRef.current = null;
      };
    }

    setPlayerState("error");
    return undefined;
  }, [streamUrl, status]);

  if (playerState === "offline") {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900 text-gray-500 gap-2">
        <VideoOff className="w-6 h-6" />
        <span className="text-xs">{cameraName} is offline</span>
      </div>
    );
  }

  if (playerState === "error") {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900 text-red-400 gap-2">
        <AlertTriangle className="w-6 h-6" />
        <span className="text-xs">Stream unavailable</span>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full bg-gray-900">
      {playerState === "loading" && (
        <div className="absolute inset-0 flex items-center justify-center">
          <Loader2 className="w-6 h-6 text-gray-400 animate-spin" />
        </div>
      )}
      <video
        ref={videoRef}
        className="w-full h-full object-cover"
        muted
        autoPlay
        playsInline
      />
    </div>
  );
}
