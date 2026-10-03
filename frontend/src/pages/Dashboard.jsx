import React, { useMemo } from "react";
import { Video, ShieldCheck, Users, Car, Database } from "lucide-react";
import StatCard from "../components/common/StatCard.jsx";
import LiveViewPanel from "../components/liveview/LiveViewPanel.jsx";
import RecentAlertsPanel from "../components/alerts/RecentAlertsPanel.jsx";
import EventsOverviewPanel from "../components/analytics/EventsOverviewPanel.jsx";
import TopCamerasPanel from "../components/cameras/TopCamerasPanel.jsx";
import SystemStatusPanel from "../components/system/SystemStatusPanel.jsx";
import { useCameras } from "../hooks/useCameras.js";
import { useAnalytics } from "../hooks/useAnalytics.js";
import { useSystemStatus } from "../hooks/useSystemStatus.js";
import { formatNumber } from "../utils/formatters.js";

export default function Dashboard() {
  const { cameras, status: camerasStatus } = useCameras();
  const { data: analytics, status: analyticsStatus } = useAnalytics("today");
  const { data: system, status: systemStatus } = useSystemStatus();

  const onlineCount = useMemo(
    () => cameras.filter((c) => c.status === "online").length,
    [cameras]
  );

  const statCards = [
    {
      id: "cameras",
      label: "Total Cameras",
      value: camerasStatus === "ready" ? formatNumber(cameras.length) : "—",
      sub: [
        { text: "Online", color: "text-gray-500" },
        {
          text: camerasStatus === "ready" ? formatNumber(onlineCount) : "—",
          color: "text-brand-blue font-semibold",
        },
      ],
      icon: Video,
      bg: "bg-brand-blue-light",
      iconColor: "text-brand-blue",
    },
    {
      id: "events",
      label: "Active Events",
      value: analyticsStatus === "ready" ? formatNumber(analytics.summary.total_events) : "—",
      sub: [
        { text: "Critical", color: "text-gray-500" },
        {
          text: analyticsStatus === "ready" ? formatNumber(analytics.summary.critical_events) : "—",
          color: "text-severity-critical font-semibold",
        },
      ],
      icon: ShieldCheck,
      bg: "bg-brand-green-light",
      iconColor: "text-brand-green",
    },
    {
      id: "people",
      label: "People Detected",
      value: analyticsStatus === "ready" ? formatNumber(analytics.summary.total_people) : "—",
      sub: [{ text: "Today", color: "text-brand-orange font-medium" }],
      icon: Users,
      bg: "bg-brand-orange-light",
      iconColor: "text-brand-orange",
    },
    {
      id: "vehicles",
      label: "Vehicles Detected",
      value: analyticsStatus === "ready" ? formatNumber(analytics.summary.total_vehicles) : "—",
      sub: [{ text: "Today", color: "text-brand-purple font-medium" }],
      icon: Car,
      bg: "bg-brand-purple-light",
      iconColor: "text-brand-purple",
    },
    {
      id: "storage",
      label: "Storage Used",
      value: systemStatus === "ready" ? `${system.storage.used_tb} TB` : "—",
      sub: [
        {
          text: systemStatus === "ready" ? `of ${system.storage.total_tb} TB` : "",
          color: "text-gray-500",
        },
      ],
      icon: Database,
      bg: "bg-brand-cyan-light",
      iconColor: "text-brand-cyan",
    },
  ];

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