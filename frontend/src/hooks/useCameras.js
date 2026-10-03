import { useCallback, useEffect, useState } from "react";
import { getCameras, createCamera, updateCamera, deleteCamera } from "../services/camerasService.js";
import { useCameraSocket } from "./useCameraSocket.js";

/**
 * Fetches the real camera list from the backend on mount, then keeps it
 * live-updated via WebSocket (status flips, stream URL changes) without
 * re-polling. No mock data, no setInterval simulation.
 */
export function useCameras() {
  const [cameras, setCameras] = useState([]);
  const [status, setStatus] = useState("loading"); // "loading" | "ready" | "error"
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");

    getCameras()
      .then((data) => {
        if (cancelled) return;
        setCameras(data);
        setStatus("ready");
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err);
        setStatus("error");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const handleSocketMessage = useCallback((payload) => {
    if (payload.type !== "camera_status") return;
    setCameras((prev) =>
      prev.map((camera) =>
        camera.id === payload.camera_id
          ? {
              ...camera,
              status: payload.status,
              stream_url: payload.stream_url ?? camera.stream_url,
            }
          : camera
      )
    );
  }, []);

  useCameraSocket(handleSocketMessage);

  const addCamera = useCallback(async (payload) => {
  const created = await createCamera(payload);
  setCameras((prev) => [...prev, created]);
  return created;
}, []);

const editCamera = useCallback(async (cameraId, payload) => {
  const updated = await updateCamera(cameraId, payload);
  setCameras((prev) => prev.map((camera) => (camera.id === cameraId ? updated : camera)));
  return updated;
}, []);

const removeCamera = useCallback(async (cameraId) => {
  await deleteCamera(cameraId);
  setCameras((prev) => prev.filter((camera) => camera.id !== cameraId));
}, []);

return { cameras, status, error, addCamera, editCamera, removeCamera };
}
