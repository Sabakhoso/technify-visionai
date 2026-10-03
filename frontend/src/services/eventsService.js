import api from "./api.js";

/**
 * GET /events
 * params: { severity, camera_id, from, to, page, page_size }
 * Response: { items: [...], total, page, page_size }
 * Each item: { id, title, severity, camera_id, location, thumbnail_url, occurred_at, status }
 */
export async function getEvents(params = {}) {
  const { data } = await api.get("/events", { params });
  return data;
}

/** PATCH /events/:id — status: "acknowledged" | "resolved" */
export async function updateEventStatus(eventId, status) {
  const { data } = await api.patch(`/events/${eventId}`, { status });
  return data;
}