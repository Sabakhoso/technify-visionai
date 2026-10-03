import api from "./api.js";

/**
 * GET /analytics/overview?range=today|7d|30d
 * Response: {
 *   summary: { total_events, total_people, total_vehicles, critical_events },
 *   detections_trend: [{ date, people, vehicles }],
 *   severity_breakdown: [{ severity, count }],
 *   top_cameras: [{ camera_id, name, events }]
 * }
 */
export async function getAnalyticsOverview(range) {
  const { data } = await api.get("/analytics/overview", { params: { range } });
  return data;
}