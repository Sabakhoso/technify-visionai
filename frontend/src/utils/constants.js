import {
  LayoutDashboard,
  Video,
  ListChecks,
  Search,
  BarChart3,
  FileText,
  Camera,
  Map,
  Users,
  Settings,
  Activity,
} from "lucide-react";

export const NAV_ITEMS = [
  { key: "dashboard", label: "Dashboard", icon: LayoutDashboard, path: "/", expandable: false },
  { key: "live-view", label: "Live View", icon: Video, path: "/live-view", expandable: false },
  { key: "events", label: "Events", icon: ListChecks, path: "/events", expandable: true },
  { key: "search", label: "Search", icon: Search, path: "/search", expandable: true },
  { key: "analytics", label: "Analytics", icon: BarChart3, path: "/analytics", expandable: true },
  { key: "reports", label: "Reports", icon: FileText, path: "/reports", expandable: true },
  { key: "cameras", label: "Cameras", icon: Camera, path: "/cameras", expandable: true },
  { key: "map-view", label: "Map View", icon: Map, path: "/map-view", expandable: true },
  { key: "users-roles", label: "Users & Roles", icon: Users, path: "/users-roles", expandable: false },
  { key: "settings", label: "Settings", icon: Settings, path: "/settings", expandable: true },
  { key: "system-status", label: "System Status", icon: Activity, path: "/system-status", expandable: false },
];

export const SEVERITY_STYLES = {
  Critical: "bg-severity-critical-bg text-severity-critical",
  High: "bg-severity-high-bg text-severity-high",
  Medium: "bg-severity-medium-bg text-severity-medium",
  Low: "bg-severity-low-bg text-severity-low",
};
