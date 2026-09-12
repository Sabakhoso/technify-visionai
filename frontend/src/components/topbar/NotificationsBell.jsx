import React, { useRef, useState } from "react";
import { Bell } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useNotifications } from "../../hooks/useNotifications.js";
import { useClickOutside } from "../../hooks/useClickOutside.js";
import { SEVERITY_STYLES } from "../../utils/constants.js";

export default function NotificationsBell() {
  const { alerts, unreadCount, status, dismiss } = useNotifications();
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);
  const navigate = useNavigate();

  useClickOutside(containerRef, () => setOpen(false));

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="relative text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white"
      >
        <Bell className="w-5 h-5" strokeWidth={2} />
        {unreadCount > 0 && (
          <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-red-500 text-white text-[10px] font-semibold flex items-center justify-center">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-navy-light border border-gray-100 dark:border-white/10 rounded-xl shadow-card z-50 overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100 dark:border-white/10 flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-900 dark:text-white">Notifications</span>
            <span className="text-xs text-gray-400">{unreadCount} unread</span>
          </div>

          <div className="max-h-80 overflow-y-auto">
            {status === "loading" && (
              <p className="px-4 py-6 text-sm text-gray-400 text-center">Loading…</p>
            )}
            {status === "error" && (
              <p className="px-4 py-6 text-sm text-red-500 text-center">Couldn't load alerts.</p>
            )}
            {status === "ready" && alerts.length === 0 && (
              <p className="px-4 py-6 text-sm text-gray-400 text-center">You're all caught up.</p>
            )}
            {alerts.map((alert) => (
              <button
                key={alert.id}
                type="button"
                onClick={() => {
                  dismiss(alert.id);
                  setOpen(false);
                  navigate("/events");
                }}
                className="w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-white/5 border-b border-gray-50 dark:border-white/5 flex items-start gap-3"
              >
                <span
                  className={`text-[10px] font-semibold px-2 py-0.5 rounded-full mt-0.5 ${
                    SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.Low
                  }`}
                >
                  {alert.severity}
                </span>
                <span className="flex-1">
                  <span className="block text-sm text-gray-900 dark:text-white">{alert.title}</span>
                  <span className="block text-xs text-gray-400 mt-0.5">
                    {alert.camera_id} • {alert.location}
                  </span>
                </span>
              </button>
            ))}
          </div>

          <button
            type="button"
            onClick={() => {
              setOpen(false);
              navigate("/events");
            }}
            className="w-full text-center text-sm text-brand-blue py-2.5 border-t border-gray-100 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/5"
          >
            View all
          </button>
        </div>
      )}
    </div>
  );
}
