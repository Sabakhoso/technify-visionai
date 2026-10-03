import api from "./api.js";

/**
 * GET /system/status
 * Response:
 * {
 *   ai_engine: "operational" | "degraded" | "down",
 *   network:   "operational" | "degraded" | "down",
 *   database:  "operational" | "degraded" | "down",
 *   storage: { status: "operational" | "degraded" | "down", used_tb: number, total_tb: number }
 * }
 *
 * Backend should also push updates over the "system" WebSocket channel as:
 * { type: "system_status", data: { ...same shape... } }
 * so the dashboard updates live instead of only on page load.
 */
export async function getSystemStatus() {
  const { data } = await api.get("/system/status");
  return data;
}