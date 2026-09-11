import React from "react";
import { NavLink } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import clsx from "clsx";

export default function SidebarItem({ item }) {
  const { label, icon: Icon, path, expandable } = item;

  return (
    <NavLink
      to={path}
      end={path === "/"}
      className={({ isActive }) =>
        clsx(
          "flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors group",
          isActive
            ? "bg-brand-blue text-white"
            : "text-slate-300 hover:bg-white/5 hover:text-white"
        )
      }
    >
      {({ isActive }) => (
        <>
          <span className="flex items-center gap-3">
            <Icon
              className={clsx("w-[18px] h-[18px]", isActive ? "text-white" : "text-slate-400 group-hover:text-white")}
              strokeWidth={2}
            />
            {label}
          </span>
          {expandable && (
            <ChevronRight
              className={clsx("w-4 h-4", isActive ? "text-white" : "text-slate-500")}
            />
          )}
        </>
      )}
    </NavLink>
  );
}
