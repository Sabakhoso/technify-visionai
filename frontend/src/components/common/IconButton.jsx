import React from "react";

export default function IconButton({ icon: Icon, onClick, active = false, className = "" }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-8 h-8 flex items-center justify-center rounded-lg transition-colors ${
        active ? "bg-gray-900 text-white" : "text-gray-500 hover:bg-gray-100"
      } ${className}`}
    >
      <Icon className="w-4 h-4" strokeWidth={2} />
    </button>
  );
}
