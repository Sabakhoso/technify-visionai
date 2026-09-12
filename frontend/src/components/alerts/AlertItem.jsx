import React from "react";
import { Footprints, UserRoundCheck, ShoppingBag, Users, CarFront } from "lucide-react";
import Badge from "../common/Badge.jsx";

const ICONS = {
  intrusion: { icon: Footprints, bg: "bg-red-50", color: "text-red-500" },
  zone: { icon: UserRoundCheck, bg: "bg-orange-50", color: "text-orange-500" },
  object: { icon: ShoppingBag, bg: "bg-amber-50", color: "text-amber-500" },
  crowd: { icon: Users, bg: "bg-orange-50", color: "text-orange-500" },
  vehicle: { icon: CarFront, bg: "bg-blue-50", color: "text-blue-500" },
};

export default function AlertItem({ alert }) {
  const conf = ICONS[alert.icon] || ICONS.intrusion;
  const Icon = conf.icon;

  return (
    <div className="flex items-center gap-3 py-3 first:pt-0 last:pb-0 border-b border-gray-100 last:border-0">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${conf.bg}`}>
        <Icon className={`w-5 h-5 ${conf.color}`} strokeWidth={2} />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-semibold text-gray-900 truncate">{alert.title}</p>
          <span className="text-xs text-gray-400 shrink-0">{alert.time}</span>
        </div>
        <p className="text-xs text-gray-500 mt-0.5">
          {alert.camera} <span className="text-gray-300">•</span> {alert.location}
        </p>
        <div className="mt-1.5">
          <Badge label={alert.severity} />
        </div>
      </div>

      <img
        src={alert.thumb}
        alt={alert.title}
        className="w-14 h-10 rounded-md object-cover shrink-0"
      />
    </div>
  );
}
