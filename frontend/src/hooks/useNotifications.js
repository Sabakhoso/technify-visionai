import { useCallback, useEffect, useState } from "react";
import { getAlerts, markAlertRead } from "../services/notificationsService.js";
import { useSocket } from "./useSocket.js";

/**
 * Real unread alerts: fetched on mount, then pushed live over the
 * "alerts" WebSocket channel as the backend's detection pipeline
 * creates them. No simulated counters.
 */
export function useNotifications() {
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getAlerts({ status: "unread" })
      .then((data) => {
        if (cancelled) return;
        setAlerts(data);
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
    if (payload.type !== "alert_created") return;
    setAlerts((prev) => [payload.alert, ...prev]);
  }, []);

  useSocket("alerts", handleSocketMessage);

  const dismiss = useCallback((alertId) => {
    setAlerts((prev) => prev.filter((alert) => alert.id !== alertId));
    markAlertRead(alertId).catch(() => {
      // Leave it dismissed locally even if the request fails; it will
      // reappear on the next fetch if it's genuinely still unread.
    });
  }, []);

  return { alerts, unreadCount: alerts.length, status, error, dismiss };
}
