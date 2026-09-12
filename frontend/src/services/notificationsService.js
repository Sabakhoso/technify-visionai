import api from "./api.js";

/**
 * GET /alerts?status=unread
 * Expected response: array of
 * { id, title, severity: "Critical"|"High"|"Medium"|"Low", camera_id, location, created_at }
 */
export async function getAlerts({ status } = {}) {
  const { data } = await api.get("/alerts", { params: status ? { status } : {} });
  return data;
}

/** PATCH /alerts/:id — marks a single alert as read */
export async function markAlertRead(alertId) {
  const { data } = await api.patch(`/alerts/${alertId}`, { status: "read" });
  return data;
}
