import React, { useRef, useState } from "react";
import { ChevronDown, Settings } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useClickOutside } from "../../hooks/useClickOutside.js";
import UserAvatar from "../common/UserAvatar.jsx";

export default function AdminMenu() {
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);
  const navigate = useNavigate();

  useClickOutside(containerRef, () => setOpen(false));

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex items-center gap-2.5 pl-4 border-l border-gray-200 dark:border-white/10"
      >
        <UserAvatar name="Admin" photoUrl={null} size={36} />
        <span className="text-left">
          <span className="block text-sm font-semibold text-gray-900 dark:text-white leading-none">Admin</span>
          <span className="block text-xs text-gray-500 dark:text-gray-400 mt-0.5">Super Admin</span>
        </span>
        <ChevronDown className="w-4 h-4 text-gray-400" />
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-navy-light border border-gray-100 dark:border-white/10 rounded-xl shadow-card z-50 overflow-hidden">
          <button
            type="button"
            onClick={() => {
              setOpen(false);
              navigate("/settings");
            }}
            className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-white/5"
          >
            <Settings className="w-4 h-4" /> Settings
          </button>
        </div>
      )}
    </div>
  );
}