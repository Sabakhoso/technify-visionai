import React from "react";
import { Cpu, HardDrive, Wifi, Camera, Database } from "lucide-react";

const ICONS = {
  cpu: Cpu,
  storage: HardDrive,
  network: Wifi,
  camera: Camera,
  database: Database,
};

export default function SystemStatusRow({ item }) {
  const Icon = ICONS[item.icon] || Cpu;

  return (
    <div className="flex items-center justify-between py-2.5">
      <div className="flex items-center gap-2.5">
        <Icon className="w-4 h-4 text-brand-blue" strokeWidth={2} />
        <span className="text-sm text-gray-700">{item.label}</span>
      </div>
      <span
        className={`text-xs font-medium px-2 py-1 rounded-md ${
          item.highlight
            ? "bg-brand-green-light text-brand-green"
            : "bg-brand-green-light text-brand-green"
        }`}
      >
        {item.status}
      </span>
    </div>
  );
}
