import { useEffect, useRef } from "react";

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000/ws";

/**
 * Generic reconnecting WebSocket subscriber for any backend channel
 * (e.g. "alerts", "cameras"). onMessage must be stable (useCallback)
 * on the caller's side or this reconnects every render.
 */
export function useSocket(channel, onMessage) {
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    let socket;
    let reconnectTimer;
    let cancelled = false;

    const connect = () => {
      const token = localStorage.getItem("access_token");
      const url = token
        ? `${WS_BASE_URL}/${channel}?token=${encodeURIComponent(token)}`
        : `${WS_BASE_URL}/${channel}`;

      socket = new WebSocket(url);

      socket.onmessage = (event) => {
        try {
          onMessageRef.current(JSON.parse(event.data));
        } catch {
          // Ignore malformed frames
        }
      };

      socket.onclose = () => {
        if (cancelled) return;
        reconnectTimer = setTimeout(connect, 3000);
      };

      socket.onerror = () => socket.close();
    };

    connect();

    return () => {
      cancelled = true;
      clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [channel]);
}
