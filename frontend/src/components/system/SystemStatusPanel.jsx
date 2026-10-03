import React from "react";
import { ChevronRight } from "lucide-react";
import SystemStatusRow from "./SystemStatusRow.jsx";
import { useSystemStatus } from "../../hooks/useSystemStatus.js";
import { useCameras } from "../../hooks/useCameras.js";

const STATUS_LABEL = {
  operational: "Operational",
  degraded: "Degraded",
  down: "Down",
};

export default function SystemStatusPanel() {
  const { data, status } = useSystemStatus();
  const { cameras } = useCameras();
  const onlineCount = cameras.filter((c) => c.status === "online").length;

  const rows = data
    ? [
        {
          id: "ai-engine",
          label: "AI Engine",
          status: STATUS_LABEL[data.ai_engine] || data.ai_engine,
          icon: "cpu",
        },
        {
          id: "storage",
          label: "Storage",
          status: STATUS_LABEL[data.storage?.status] || data.storage?.status,
          icon: "storage",
        },
        {
          id: "network",
          label: "Network",
          status: STATUS_LABEL[data.network] || data.network,
          icon: "network",
        },
        {
          id: "cameras",
          label: "Cameras",
          status: `${onlineCount} / ${cameras.length} Online`,
          icon: "camera",
          highlight: true,
        },
        {
          id: "database",
          label: "Database",
          status: STATUS_LABEL[data.database] || data.database,
          icon: "database",
        },
      ]
    : [];

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5 h-full flex flex-col">
      <h2 className="text-base font-semibold text-gray-900 mb-2">System Status</h2>

      <div className="flex-1 divide-y divide-gray-100">
        {status === "loading" && (
          <p className="text-sm text-gray-400 py-6 text-center">Loading…</p>
        )}
        {status === "error" && (
          <p className="text-sm text-red-500 py-6 text-center">Could not load system status.</p>
        )}
        {rows.map((item) => (
          <SystemStatusRow key={item.id} item={item} />
        ))}
      </div>

      <button
        type="button"
        className="mt-4 w-full flex items-center justify-center gap-1.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg py-2.5 hover:bg-gray-50 transition-colors"
      >
        View System Health
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
}