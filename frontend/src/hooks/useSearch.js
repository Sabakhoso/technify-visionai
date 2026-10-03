import { useEffect, useState } from "react";
import { search } from "../services/searchService.js";

const EMPTY_RESULTS = { cameras: [], events: [], people: [] };

/**
 * Debounced real search against the backend — waits 350ms after the
 * query stops changing before firing the request, and ignores a
 * response if the query has already changed again ("cancelled").
 */
export function useSearch(query) {
  const [results, setResults] = useState(EMPTY_RESULTS);
  const [status, setStatus] = useState("idle"); // idle | loading | ready | error
  const [error, setError] = useState(null);

  useEffect(() => {
    const trimmed = query.trim();
    if (!trimmed) {
      setResults(EMPTY_RESULTS);
      setStatus("idle");
      return;
    }

    let cancelled = false;
    setStatus("loading");

    const timer = setTimeout(() => {
      search(trimmed)
        .then((data) => {
          if (cancelled) return;
          setResults({
            cameras: data.cameras || [],
            events: data.events || [],
            people: data.people || [],
          });
          setStatus("ready");
        })
        .catch((err) => {
          if (cancelled) return;
          setError(err);
          setStatus("error");
        });
    }, 350);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [query]);

  return { results, status, error };
}