import { useCallback, useEffect, useState } from "react";
import { getEvents, updateEventStatus } from "../services/eventsService.js";
import { useSocket } from "./useSocket.js";

const PAGE_SIZE = 15;

/**
 * Real, filterable, paginated event log. Fetches from the backend on
 * every filter/page change, and splices newly detected events into
 * page 1 live via the "events" WebSocket channel.
 *
 * `filters` must be a stable object (useMemo in the caller) or this
 * will refetch every render.
 */
export function useEvents(filters) {
  const [events, setEvents] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");

    getEvents({ ...filters, page, page_size: PAGE_SIZE })
      .then((data) => {
        if (cancelled) return;
        setEvents(data.items);
        setTotal(data.total);
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
  }, [filters, page]);

  const handleSocketMessage = useCallback(
    (payload) => {
      if (payload.type !== "event_created") return;
      setEvents((prev) => (page === 1 ? [payload.event, ...prev].slice(0, PAGE_SIZE) : prev));
      setTotal((prev) => prev + 1);
    },
    [page]
  );

  useSocket("events", handleSocketMessage);

  const setEventStatus = useCallback((eventId, nextStatus) => {
    setEvents((prev) =>
      prev.map((event) => (event.id === eventId ? { ...event, status: nextStatus } : event))
    );
    updateEventStatus(eventId, nextStatus).catch(() => {
      // Backend rejected it — a later refetch (filter/page change) will correct the UI
    });
  }, []);

  return {
    events,
    total,
    page,
    setPage,
    pageCount: Math.max(1, Math.ceil(total / PAGE_SIZE)),
    status,
    error,
    setEventStatus,
  };
}