import React from "react";
import { ChevronRight } from "lucide-react";
import Dropdown from "../common/Dropdown.jsx";
import EventStatCard from "./EventStatCard.jsx";
import { useAnalytics } from "../../hooks/useAnalytics.js";
import { buildEventsOverviewCards } from "../../utils/dashboardAdapters.js";

export default function EventsOverviewPanel() {
  const { data, status } = useAnalytics("today");
  const cards = buildEventsOverviewCards(data);

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-gray-900">Events Overview</h2>
        <Dropdown label="Today" />
      </div>

      {status === "loading" && (
        <p className="text-sm text-gray-400 flex-1 flex items-center justify-center">Loading…</p>
      )}
      {status === "error" && (
        <p className="text-sm text-red-500 flex-1 flex items-center justify-center">
          Could not load analytics.
        </p>
      )}
      {status === "ready" && (
        <div className="grid grid-cols-5 gap-3 flex-1">
          {cards.map((e) => (
            <EventStatCard
              key={e.id}
              label={e.label}
              value={e.value}
              color={e.color}
              data={e.data}
              labelColor={e.labelColor}
            />
          ))}
        </div>
      )}

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