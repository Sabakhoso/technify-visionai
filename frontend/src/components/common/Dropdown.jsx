import React from "react";
import { ChevronDown } from "lucide-react";

export default function Dropdown({ label }) {
  return (
    <button
      type="button"
      className="flex items-center gap-1.5 text-sm text-gray-600 border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-50 transition-colors"
    >
      {label}
      <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
    </button>
  );
}
