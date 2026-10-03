import React from "react";
import AlertItem from "./AlertItem.jsx";
import { useNotifications } from "../../hooks/useNotifications.js";
import { toDisplayAlert } from "../../utils/dashboardAdapters.js";

export default function RecentAlertsPanel() {
  const { alerts, status } = useNotifications();

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5 h-full">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-base font-semibold text-gray-900">Recent Alerts</h2>
        <button type="button" className="text-sm text-brand-blue font-medium hover:underline">
          View All
        </button>
      </div>

      <div>
        {status === "loading" && (
          <p className="text-sm text-gray-400 py-6 text-center">Loading alerts…</p>
        )}
        {status === "error" && (
          <p className="text-sm text-red-500 py-6 text-center">Could not load alerts.</p>
        )}
        {status === "ready" && alerts.length === 0 && (
          <p className="text-sm text-gray-400 py-6 text-center">No active alerts.</p>
        )}
        {alerts.slice(0, 5).map((alert) => (
          <AlertItem key={alert.id} alert={toDisplayAlert(alert)} />
        ))}
      </div>
    </div>
  );
}