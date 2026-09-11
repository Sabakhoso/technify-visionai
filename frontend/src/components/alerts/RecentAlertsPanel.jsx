import React from "react";
import AlertItem from "./AlertItem.jsx";
import { recentAlerts } from "../../data/mockData.js";

export default function RecentAlertsPanel() {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5 h-full">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-base font-semibold text-gray-900">Recent Alerts</h2>
        <button type="button" className="text-sm text-brand-blue font-medium hover:underline">
          View All
        </button>
      </div>

      <div>
        {recentAlerts.map((alert) => (
          <AlertItem key={alert.id} alert={alert} />
        ))}
      </div>
    </div>
  );
}
