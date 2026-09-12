import React from "react";
import { ChevronRight } from "lucide-react";
import SystemStatusRow from "./SystemStatusRow.jsx";
import { systemStatus } from "../../data/mockData.js";

export default function SystemStatusPanel() {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5 h-full flex flex-col">
      <h2 className="text-base font-semibold text-gray-900 mb-2">System Status</h2>

      <div className="flex-1 divide-y divide-gray-100">
        {systemStatus.map((item) => (
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
