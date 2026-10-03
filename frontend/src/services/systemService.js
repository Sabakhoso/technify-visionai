import api from "./api.js";

/**
 * GET /system/status
 * Response: {
 *   api: "running",
 *   environment: string,
 *   database: "connected"|"disconnected",
 *   cameras: { total, online, offline },
 *   organizations: number
 * }
 */
export async function getSystemStatus() {
  const { data } = await api.get("/system/status");
  return data;
}