import { useEffect, useRef } from "react";

const rawWsUrl = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000/ws";
const WS_BASE_URL = rawWsUrl.replace(/\/+$/, "");

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

      try {
        socket = new WebSocket(url);
      } catch {
        if (!cancelled) reconnectTimer = setTimeout(connect, 5000);
        return;
      }

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          onMessageRef.current(payload);
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
  }, []);
}
