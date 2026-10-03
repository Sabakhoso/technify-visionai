import React from "react";
import { Routes, Route } from "react-router-dom";
import DashboardLayout from "../layout/DashboardLayout.jsx";
import Dashboard from "../pages/Dashboard.jsx";
import LiveView from "../pages/LiveView.jsx";
import Events from "../pages/Events.jsx";
import Analytics from "../pages/Analytics.jsx";
import Cameras from "../pages/Cameras.jsx";
import Settings from "../pages/Settings.jsx";
import SystemStatus from "../pages/SystemStatus.jsx";

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/live-view" element={<LiveView />} />
        <Route path="/events" element={<Events />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/cameras" element={<Cameras />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/system-status" element={<SystemStatus />} />
      </Route>
    </Routes>
  );
}