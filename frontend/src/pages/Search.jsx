import React, { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Search as SearchIcon, RefreshCcw, Video, ListChecks, Users } from "lucide-react";
import { useSearch } from "../hooks/useSearch.js";
import { SEVERITY_STYLES } from "../utils/constants.js";
import { formatDateTime } from "../utils/formatters.js";

const TABS = ["All", "Cameras", "Events", "People"];

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [tab, setTab] = useState("All");
  const navigate = useNavigate();

  useEffect(() => {
    setQuery(searchParams.get("q") || "");
  }, [searchParams]);

  const { results, status, error } = useSearch(query);
  const totalCount = results.cameras.length + results.events.length + results.people.length;

  const handleSubmit = (event) => {
    event.preventDefault();
    setSearchParams(query ? { q: query } : {});
  };

  return (
    <div className="space-y-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-xl border border-gray-100 shadow-card p-4 flex items-center gap-3"
      >
        <SearchIcon className="w-4 h-4 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search cameras, events, people..."
          className="flex-1 text-sm text-gray-700 placeholder-gray-400 focus:outline-none"
          autoFocus
        />
        {status === "loading" && <RefreshCcw className="w-4 h-4 text-gray-400 animate-spin" />}
      </form>

      <div className="bg-white rounded-xl border border-gray-100 shadow-card">
        <div className="flex items-center gap-1 px-5 pt-4">
          {TABS.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => setTab(option)}
              className={`text-sm font-medium px-3 py-1.5 rounded-lg ${
                tab === option ? "bg-gray-900 text-white" : "text-gray-500 hover:bg-gray-50"
              }`}
            >
              {option}
            </button>
          ))}
        </div>

        <div className="p-5">
          {status === "idle" && (
            <p className="text-sm text-gray-400 text-center py-10">Type something to search.</p>
          )}

          {status === "error" && (
            <div className="text-center py-10">
              <p className="text-sm text-red-500 font-medium">Search failed.</p>
              <p className="text-xs text-gray-400 mt-1">
                {error?.message || "Check that the API server is reachable."}
              </p>
            </div>
          )}

          {status === "ready" && totalCount === 0 && (
            <p className="text-sm text-gray-400 text-center py-10">No results for "{query}".</p>
          )}

          {status === "ready" && totalCount > 0 && (
            <div className="space-y-6">
              {(tab === "All" || tab === "Cameras") && results.cameras.length > 0 && (
                <ResultSection
                  icon={Video}
                  title="Cameras"
                  items={results.cameras.map((camera) => ({
                    id: camera.id,
                    primary: camera.name,
                    secondary: `${camera.id} • ${camera.location}`,
                    badge: camera.status,
                    onClick: () => navigate("/live-view"),
                  }))}
                />
              )}

              {(tab === "All" || tab === "Events") && results.events.length > 0 && (
                <ResultSection
                  icon={ListChecks}
                  title="Events"
                  items={results.events.map((eventItem) => ({
                    id: eventItem.id,
                    primary: eventItem.title,
                    secondary: `${eventItem.camera_id} • ${eventItem.location} • ${formatDateTime(
                      eventItem.occurred_at
                    )}`,
                    badge: eventItem.severity,
                    badgeClass: SEVERITY_STYLES[eventItem.severity],
                    onClick: () => navigate("/events"),
                  }))}
                />
              )}

              {(tab === "All" || tab === "People") && results.people.length > 0 && (
                <ResultSection
                  icon={Users}
                  title="People"
                  items={results.people.map((person) => ({
                    id: person.id,
                    primary: person.label || `Person ${person.id}`,
                    secondary: `${person.camera_id} • ${person.location} • ${formatDateTime(person.seen_at)}`,
                    onClick: () => navigate("/events"),
                  }))}
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ResultSection({ icon: Icon, title, items }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2 text-gray-500">
        <Icon className="w-4 h-4" />
        <span className="text-xs font-semibold uppercase tracking-wide">{title}</span>
      </div>
      <div className="border border-gray-100 rounded-lg divide-y divide-gray-50">
        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={item.onClick}
            className="w-full flex items-center justify-between gap-3 px-4 py-3 text-left hover:bg-gray-50"
          >
            <span>
              <span className="block text-sm font-medium text-gray-900">{item.primary}</span>
              <span className="block text-xs text-gray-400 mt-0.5">{item.secondary}</span>
            </span>
            {item.badge && (
              <span
                className={`text-[11px] font-semibold px-2 py-1 rounded-full shrink-0 ${
                  item.badgeClass || "bg-gray-100 text-gray-600"
                }`}
              >
                {item.badge}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}