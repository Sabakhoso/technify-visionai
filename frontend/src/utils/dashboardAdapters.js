import { formatTime } from "./formatters.js";

const ALERT_ICON_RULES = [
  { icon: "intrusion", match: /intrusion|breach|trespass/i },
  { icon: "zone", match: /restricted|zone|unauthorized/i },
  { icon: "object", match: /object|left behind|package/i },
  { icon: "crowd", match: /crowd|gathering/i },
  { icon: "vehicle", match: /vehicle|car|truck/i },
];

function iconForAlertTitle(title = "") {
  const rule = ALERT_ICON_RULES.find((r) => r.match.test(title));
  return rule ? rule.icon : "intrusion";
}

/** Backend alert ({id,title,severity,camera_id,location,created_at,thumbnail_url?})
 *  -> the shape AlertItem.jsx renders. */
export function toDisplayAlert(alert) {
  return {
    id: alert.id,
    title: alert.title,
    camera: alert.camera_id,
    location: alert.location,
    time: alert.created_at ? formatTime(new Date(alert.created_at)) : "—",
    severity: alert.severity,
    icon: iconForAlertTitle(alert.title),
    thumb: alert.thumbnail_url || null,
  };
}

/** Backend top_cameras item ({camera_id,name,events}) -> CameraRankRow shape. */
export function toDisplayTopCamera(item, maxEvents) {
  return {
    id: item.camera_id,
    name: item.name,
    events: item.events,
    max: Math.max(maxEvents, 1),
  };
}

const SEVERITY_META = {
  Critical: { id: "critical", color: "#dc2626", labelColor: "text-severity-critical" },
  High: { id: "high", color: "#ea580c", labelColor: "text-severity-high" },
  Medium: { id: "medium", color: "#ca8a04", labelColor: "text-amber-600" },
  Low: { id: "low", color: "#16a34a", labelColor: "text-gray-500" },
};

/**
 * analytics overview response -> the 5 mini cards EventsOverviewPanel renders.
 * "All Events" is derived (summed) from the real per-severity data —
 * nothing here is fabricated.
 */
export function buildEventsOverviewCards(analytics) {
  if (!analytics) return [];

  const breakdown = analytics.severity_breakdown || [];
  const trendLength = breakdown.reduce((max, b) => Math.max(max, b.trend?.length || 0), 0);
  const allTrend = Array.from({ length: trendLength }, (_, i) =>
    breakdown.reduce((sum, b) => sum + (b.trend?.[i] || 0), 0)
  );

  const cards = [
    {
      id: "all",
      label: "All Events",
      value: analytics.summary?.total_events ?? 0,
      color: "#2563eb",
      data: allTrend,
      labelColor: "text-brand-blue",
    },
  ];

  breakdown.forEach((b) => {
    const meta = SEVERITY_META[b.severity] || {};
    cards.push({
      id: meta.id || (b.severity || "").toLowerCase(),
      label: b.severity,
      value: b.count,
      color: meta.color || "#6b7280",
      data: b.trend || [],
      labelColor: meta.labelColor || "text-gray-500",
    });
  });

  return cards;
}