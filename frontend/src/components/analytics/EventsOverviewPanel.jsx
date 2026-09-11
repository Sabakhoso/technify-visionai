import React from "react";
import { ChevronRight } from "lucide-react";
import Dropdown from "../common/Dropdown.jsx";
import EventStatCard from "./EventStatCard.jsx";
import { eventsOverview } from "../../data/mockData.js";

const LABEL_COLORS = {
  all: "text-brand-blue",
  critical: "text-severity-critical",
  high: "text-severity-high",
  medium: "text-amber-600",
  low: "text-gray-500",
};

export default function EventsOverviewPanel() {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-gray-900">Events Overview</h2>
        <Dropdown label="Today" />
      </div>

      <div className="grid grid-cols-5 gap-3 flex-1">
        {eventsOverview.map((e) => (
          <EventStatCard
            key={e.id}
            label={e.label}
            value={e.value}
            color={e.color}
            data={e.data}
            labelColor={LABEL_COLORS[e.id]}
          />
        ))}
      </div>

      <button
        type="button"
        className="mt-4 w-full flex items-center justify-center gap-1.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg py-2.5 hover:bg-gray-50 transition-colors"
      >
        View Full Analytics
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
}
