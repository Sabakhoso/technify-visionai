import React from "react";
import { Check, CheckCheck } from "lucide-react";
import { SEVERITY_STYLES } from "../../utils/constants.js";
import { formatDateTime } from "../../utils/formatters.js";

export default function EventRow({ event, onAcknowledge, onResolve }) {
  return (
    <div className="flex items-center gap-4 px-5 py-3 border-b border-gray-50 last:border-b-0">
      <div className="w-20 h-14 rounded-lg overflow-hidden bg-gray-900 shrink-0">
        {event.thumbnail_url ? (
          <img src={event.thumbnail_url} alt={event.title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-[10px] text-gray-500 text-center px-1">
            No snapshot
          </div>
        )}
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">{event.title}</p>
        <p className="text-xs text-gray-400 mt-0.5">
          {event.camera_id} • {event.location} • {formatDateTime(event.occurred_at)}
        </p>
      </div>

      <span
        className={`text-[11px] font-semibold px-2.5 py-1 rounded-full shrink-0 ${
          SEVERITY_STYLES[event.severity] || SEVERITY_STYLES.Low
        }`}
      >
        {event.severity}
      </span>

      <span className="text-xs text-gray-500 w-24 text-center shrink-0 capitalize">{event.status}</span>

      <div className="flex items-center gap-2 shrink-0">
        {event.status === "new" && (
          <button
            type="button"
            onClick={() => onAcknowledge(event.id)}
            className="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50"
            title="Acknowledge"
          >
            <Check className="w-4 h-4" />
          </button>
        )}
        {event.status !== "resolved" && (
          <button
            type="button"
            onClick={() => onResolve(event.id)}
            className="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50"
            title="Resolve"
          >
            <CheckCheck className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}