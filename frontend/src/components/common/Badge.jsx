import React from "react";
import { SEVERITY_STYLES } from "../../utils/constants.js";

export default function Badge({ label }) {
  const cls = SEVERITY_STYLES[label] || "bg-gray-100 text-gray-600";
  return (
    <span className={`inline-block text-xs font-medium px-2 py-0.5 rounded-md ${cls}`}>
      {label}
    </span>
  );
}
