import React, { useMemo, useState } from "react";
import { RefreshCcw } from "lucide-react";
import { useEvents } from "../hooks/useEvents.js";
import { useCameras } from "../hooks/useCameras.js";
import EventRow from "../components/events/EventRow.jsx";

const SEVERITIES = ["All", "Critical", "High", "Medium", "Low"];

export default function Events() {
  const [severity, setSeverity] = useState("All");
  const [cameraId, setCameraId] = useState("All");
  const { cameras } = useCameras();

  const filters = useMemo(
    () => ({
      severity: severity === "All" ? undefined : severity,
      camera_id: cameraId === "All" ? undefined : cameraId,
    }),
    [severity, cameraId]
  );

  const { events, total, page, setPage, pageCount, status, error, setEventStatus } = useEvents(filters);

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card">
      <div className="flex flex-wrap items-center justify-between gap-3 p-5 border-b border-gray-100">
        <h1 className="text-lg font-semibold text-gray-900">
          Events <span className="text-sm text-gray-400 font-normal">({total})</span>
        </h1>

        <div className="flex items-center gap-2">
          <select
            value={severity}
            onChange={(event) => {
              setSeverity(event.target.value);
              setPage(1);
            }}
            className="text-sm text-gray-600 border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-brand-blue/30"
          >
            {SEVERITIES.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>

          <select
            value={cameraId}
            onChange={(event) => {
              setCameraId(event.target.value);
              setPage(1);
            }}
            className="text-sm text-gray-600 border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-brand-blue/30"
          >
            <option value="All">All Cameras</option>
            {cameras.map((camera) => (
              <option key={camera.id} value={camera.id}>
                {camera.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {status === "loading" && (
        <div className="p-10 flex items-center justify-center">
          <RefreshCcw className="w-5 h-5 text-gray-400 animate-spin" />
        </div>
      )}

      {status === "error" && (
        <div className="p-10 text-center">
          <p className="text-sm text-red-500 font-medium">Couldn't load events from the backend.</p>
          <p className="text-xs text-gray-400 mt-1">
            {error?.message || "Check that the API server is running and reachable."}
          </p>
        </div>
      )}

      {status === "ready" && events.length === 0 && (
        <div className="p-10 text-center text-sm text-gray-400">No events match these filters.</div>
      )}

      {status === "ready" &&
        events.length > 0 &&
        events.map((event) => (
          <EventRow
            key={event.id}
            event={event}
            onAcknowledge={(id) => setEventStatus(id, "acknowledged")}
            onResolve={(id) => setEventStatus(id, "resolved")}
          />
        ))}

      {status === "ready" && pageCount > 1 && (
        <div className="flex items-center justify-between px-5 py-3 border-t border-gray-100">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage((prev) => prev - 1)}
            className="text-sm text-gray-600 disabled:text-gray-300 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-xs text-gray-400">
            Page {page} of {pageCount}
          </span>
          <button
            type="button"
            disabled={page >= pageCount}
            onClick={() => setPage((prev) => prev + 1)}
            className="text-sm text-gray-600 disabled:text-gray-300 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}