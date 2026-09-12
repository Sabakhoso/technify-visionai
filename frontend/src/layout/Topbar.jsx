import React, { useState } from "react";
import { Search, Moon, Sun } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useTheme } from "../hooks/useTheme.js";
import NotificationsBell from "../components/topbar/NotificationsBell.jsx";
import AdminMenu from "../components/topbar/AdminMenu.jsx";

export default function Topbar() {
  const { isDark, toggleTheme } = useTheme();
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    navigate(`/search?q=${encodeURIComponent(trimmed)}`);
  };

  return (
    <header className="h-[76px] shrink-0 flex items-center justify-between gap-6 px-8 border-b border-gray-100 dark:border-white/10 bg-white dark:bg-navy-light">
      <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
        <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search cameras, events, people..."
          className="w-full bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg pl-10 pr-4 py-2.5 text-sm text-gray-700 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-blue/30 focus:border-brand-blue"
        />
      </form>

      <div className="flex items-center gap-5">
        <NotificationsBell />

        <button
          type="button"
          onClick={toggleTheme}
          className="text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white"
          aria-label="Toggle dark mode"
        >
          {isDark ? <Sun className="w-5 h-5" strokeWidth={2} /> : <Moon className="w-5 h-5" strokeWidth={2} />}
        </button>

        <AdminMenu />
      </div>
    </header>
  );
}
