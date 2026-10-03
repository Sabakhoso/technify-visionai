import { useEffect, useState } from "react";
import { getAnalyticsOverview } from "../services/analyticsService.js";

export function useAnalytics(range) {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");

    getAnalyticsOverview(range)
      .then((result) => {
        if (cancelled) return;
        setData(result);
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
  }, [range]);

  return { data, status, error };
}