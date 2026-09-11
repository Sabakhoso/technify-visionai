import React from "react";
import { Routes, Route } from "react-router-dom";
import DashboardLayout from "../layout/DashboardLayout.jsx";
import Dashboard from "../pages/Dashboard.jsx";
import LiveView from "../pages/LiveView.jsx";
import Events from "../pages/Events.jsx";
import Search from "../pages/Search.jsx";
import Analytics from "../pages/Analytics.jsx";
import Reports from "../pages/Reports.jsx";
import Cameras from "../pages/Cameras.jsx";
import MapView from "../pages/MapView.jsx";
import UsersRoles from "../pages/UsersRoles.jsx";
import Settings from "../pages/Settings.jsx";
import SystemStatus from "../pages/SystemStatus.jsx";

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/live-view" element={<LiveView />} />
        <Route path="/events" element={<Events />} />
        <Route path="/search" element={<Search />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/cameras" element={<Cameras />} />
        <Route path="/map-view" element={<MapView />} />
        <Route path="/users-roles" element={<UsersRoles />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/system-status" element={<SystemStatus />} />
      </Route>
    </Routes>
  );
}
