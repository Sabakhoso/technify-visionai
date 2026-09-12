import { useEffect, useRef } from "react";

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000/ws";

/**
 * Opens a live WebSocket to the backend's camera channel and forwards
 * every parsed message to onMessage. Reconnects automatically with
 * backoff if the connection drops (network blip, backend restart, etc).
 *
 * Expected server message shape:
 * { type: "camera_status", camera_id: string, status: "online"|"offline", stream_url?: string }
 *
 * onMessage MUST be wrapped in useCallback by the caller, or this will
 * reconnect on every render.
 */
export function useCameraSocket(onMessage) {
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    let socket;
    let reconnectTimer;
    let cancelled = false;

    const connect = () => {
      const token = localStorage.getItem("access_token");
      const url = token
        ? `${WS_BASE_URL}/cameras?token=${encodeURIComponent(token)}`
        : `${WS_BASE_URL}/cameras`;

      socket = new WebSocket(url);

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          onMessageRef.current(payload);
        } catch {
          // Ignore malformed frames rather than crashing the UI
        }
      };

      socket.onclose = () => {
        if (cancelled) return;
        // Backend restarted or network dropped — retry in 3s
        reconnectTimer = setTimeout(connect, 3000);
      };

      socket.onerror = () => {
        socket.close();
      };
    };

    connect();

    return () => {
      cancelled = true;
      clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, []);
}
