import React, { useState } from "react";
import { RefreshCcw } from "lucide-react";
import { useAnalytics } from "../hooks/useAnalytics.js";
import DetectionsTrendChart from "../components/analytics/DetectionsTrendChart.jsx";
import SeverityBreakdownChart from "../components/analytics/SeverityBreakdownChart.jsx";
import CameraRankRow from "../components/cameras/CameraRankRow.jsx";
import { formatNumber } from "../utils/formatters.js";

const RANGES = [
  { key: "today", label: "Today" },
  { key: "7d", label: "7 Days" },
  { key: "30d", label: "30 Days" },
];

export default function Analytics() {
  const [range, setRange] = useState("7d");
  const { data, status, error } = useAnalytics(range);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-gray-900">Analytics</h1>
        <div className="flex items-center gap-1 bg-white border border-gray-200 rounded-lg p-1">
          {RANGES.map((option) => (
            <button
              key={option.key}
              type="button"
              onClick={() => setRange(option.key)}
              className={`text-sm px-3 py-1.5 rounded-md ${
                range === option.key ? "bg-gray-900 text-white" : "text-gray-500 hover:bg-gray-50"
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {status === "loading" && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-card p-10 flex items-center justify-center">
          <RefreshCcw className="w-5 h-5 text-gray-400 animate-spin" />
        </div>
      )}

      {status === "error" && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-card p-10 text-center">
          <p className="text-sm text-red-500 font-medium">Couldn't load analytics from the backend.</p>
          <p className="text-xs text-gray-400 mt-1">
            {error?.message || "Check that the API server is running and reachable."}
          </p>
        </div>
      )}

      {status === "ready" && data && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <SummaryCard label="Total Events" value={formatNumber(data.summary.total_events)} />
            <SummaryCard label="People Detected" value={formatNumber(data.summary.total_people)} />
            <SummaryCard label="Vehicles Detected" value={formatNumber(data.summary.total_vehicles)} />
            <SummaryCard
              label="Critical Events"
              value={formatNumber(data.summary.critical_events)}
              accent="text-severity-critical"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-white rounded-xl border border-gray-100 shadow-card p-5">
              <h2 className="text-base font-semibold text-gray-900 mb-4">Detections Over Time</h2>
              {data.detections_trend.length > 0 ? (
                <DetectionsTrendChart data={data.detections_trend} />
              ) : (
                <p className="text-sm text-gray-400 text-center py-10">No detection data for this range.</p>
              )}
            </div>

            <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5">
              <h2 className="text-base font-semibold text-gray-900 mb-4">Events by Severity</h2>
              {data.severity_breakdown.length > 0 ? (
                <SeverityBreakdownChart data={data.severity_breakdown} />
              ) : (
                <p className="text-sm text-gray-400 text-center py-10">No events for this range.</p>
              )}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5">
            <h2 className="text-base font-semibold text-gray-900 mb-2">Top Cameras by Events</h2>
            {data.top_cameras.length > 0 ? (
              <div className="divide-y divide-gray-100">
                {data.top_cameras.map((camera) => (
                  <CameraRankRow
                    key={camera.camera_id}
                    camera={{
                      id: camera.camera_id,
                      name: camera.name,
                      events: camera.events,
                      max: data.top_cameras[0].events,
                    }}
                  />
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-400 text-center py-10">No camera activity for this range.</p>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function SummaryCard({ label, value, accent = "text-gray-900" }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-4">
      <p className="text-xs text-gray-500">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${accent}`}>{value}</p>
    </div>
  );
}