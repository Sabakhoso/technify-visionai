import React from "react";
import StatCard from "../components/common/StatCard.jsx";
import LiveViewPanel from "../components/liveview/LiveViewPanel.jsx";
import RecentAlertsPanel from "../components/alerts/RecentAlertsPanel.jsx";
import EventsOverviewPanel from "../components/analytics/EventsOverviewPanel.jsx";
import TopCamerasPanel from "../components/cameras/TopCamerasPanel.jsx";
import SystemStatusPanel from "../components/system/SystemStatusPanel.jsx";
import { statCards } from "../data/mockData.js";

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Top stat row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {statCards.map((card) => (
          <StatCard key={card.id} {...card} />
        ))}
      </div>

      {/* Live View + Recent Alerts */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 items-start">
        <div className="xl:col-span-2">
          <LiveViewPanel />
        </div>
        <div>
          <RecentAlertsPanel />
        </div>
      </div>

      {/* Events Overview + Top Cameras + System Status */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 items-stretch">
        <EventsOverviewPanel />
        <TopCamerasPanel />
        <SystemStatusPanel />
      </div>
    </div>
  );
}
