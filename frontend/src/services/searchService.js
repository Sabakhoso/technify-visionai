import api from "./api.js";

/**
 * GET /search?q=<query>
 * Response: {
 *   cameras: [{ id, name, location, status }],
 *   events: [{ id, title, severity, camera_id, location, occurred_at, thumbnail_url }],
 *   people: [{ id, label, camera_id, location, seen_at, thumbnail_url }]
 * }
 */
export async function search(query) {
  const { data } = await api.get("/search", { params: { q: query } });
  return data;
}