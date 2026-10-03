import { useCallback, useEffect, useState } from "react";
import { getSystemStatus } from "../services/systemService.js";

const POLL_INTERVAL_MS = 15000;

export function useSystemStatus() {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);

  const fetchStatus = useCallback(() => {
    return getSystemStatus()
      .then((result) => {
        setData(result);
        setStatus("ready");
        setLastChecked(new Date());
      })
      .catch((err) => {
        setError(err);
        setStatus("error");
        setLastChecked(new Date());
      });
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  return { data, status, error, lastChecked, refresh: fetchStatus };
}