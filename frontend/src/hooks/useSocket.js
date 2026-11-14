import { useEffect, useRef } from "react";

const rawWsUrl = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000/ws";
const WS_BASE_URL = rawWsUrl.replace(/\/+$/, "");

/**
 * Generic reconnecting WebSocket subscriber for any backend channel
 * (e.g. "alerts", "cameras", "live_events"). onMessage must be stable (useCallback)
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
      const cleanChannel = channel ? channel.replace(/^\/+/, "") : "";
      const path = cleanChannel ? `${WS_BASE_URL}/${cleanChannel}` : WS_BASE_URL;
      const url = token
        ? `${path}?token=${encodeURIComponent(token)}`
        : path;

      try {
        socket = new WebSocket(url);
      } catch {
        // Handle initial socket creation failure silently
        if (!cancelled) reconnectTimer = setTimeout(connect, 5000);
        return;
      }

      socket.onmessage = (event) => {
        try {
          onMessageRef.current(JSON.parse(event.data));
        } catch {
          // Ignore malformed frames
        }
      };

      socket.onclose = () => {
        if (cancelled) return;
        reconnectTimer = setTimeout(connect, 5000);
      };

      socket.onerror = () => {
        try {
          socket.close();
        } catch {}
      };
    };

    connect();

    return () => {
      cancelled = true;
      clearTimeout(reconnectTimer);
      try {
        socket?.close();
      } catch {}
    };
  }, [channel]);
}
