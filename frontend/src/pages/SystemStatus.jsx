import React from "react";
import { RefreshCcw, Server, Database, Video, Building2 } from "lucide-react";
import { useSystemStatus } from "../hooks/useSystemStatus.js";

export default function SystemStatus() {
  const { data, status, error, lastChecked, refresh } = useSystemStatus();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-gray-900">System Status</h1>
        <div className="flex items-center gap-3">
          {lastChecked && (
            <span className="text-xs text-gray-400">Last checked {lastChecked.toLocaleTimeString()}</span>
          )}
          <button
            type="button"
            onClick={refresh}
            className="flex items-center gap-1.5 text-sm text-gray-600 border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-50"
          >
            <RefreshCcw className={`w-4 h-4 ${status === "loading" ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </div>

      {status === "error" && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-card p-6 text-center">
          <p className="text-sm text-red-500 font-medium">Couldn't reach the backend at all.</p>
          <p className="text-xs text-gray-400 mt-1">
            {error?.message || "The API server may be down or unreachable."}
          </p>
        </div>
      )}

      {data && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatusCard
            icon={Server}
            label="API"
            value={data.api === "running" ? "Running" : "Down"}
            healthy={data.api === "running"}
          />
          <StatusCard
            icon={Database}
            label="Database"
            value={data.database === "connected" ? "Connected" : "Disconnected"}
            healthy={data.database === "connected"}
          />
          <StatusCard
            icon={Video}
            label="Cameras Online"
            value={`${data.cameras.online} / ${data.cameras.total}`}
            healthy={data.cameras.total === 0 || data.cameras.online > 0}
          />
          <StatusCard icon={Building2} label="Organizations" value={data.organizations} healthy />
        </div>
      )}

      {data && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5">
          <h2 className="text-base font-semibold text-gray-900 mb-4">Camera Fleet</h2>
          <div className="flex items-center gap-6 text-sm">
            <div>
              <p className="text-2xl font-bold text-gray-900">{data.cameras.total}</p>
              <p className="text-gray-400">Total</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{data.cameras.online}</p>
              <p className="text-gray-400">Online</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-400">{data.cameras.offline}</p>
              <p className="text-gray-400">Offline</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatusCard({ icon: Icon, label, value, healthy }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-4">
      <div className="flex items-center justify-between mb-2">
        <Icon className="w-5 h-5 text-gray-400" />
        <span className={`w-2 h-2 rounded-full ${healthy ? "bg-green-500" : "bg-red-500"}`} />
      </div>
      <p className="text-xl font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-400 mt-0.5">{label}</p>
    </div>
  );
}