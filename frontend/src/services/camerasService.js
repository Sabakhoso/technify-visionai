import api from "./api.js";

/**
 * GET /cameras
 * Expected response: array of
 * {
 *   id: string,            e.g. "CAM-017"
 *   name: string,           e.g. "Main Gate"
 *   location: string,       e.g. "Perimeter"
 *   status: "online" | "offline",
 *   stream_url: string      HLS (.m3u8) or native browser-playable URL, null if offline
 * }
 */
export async function getCameras() {
  const { data } = await api.get("/cameras");
  return data;
}

/**
 * GET /cameras/:id
 * Same shape as a single item above.
 */
export async function getCamera(cameraId) {
  const { data } = await api.get(`/cameras/${cameraId}`);
  return data;
}
/** POST /cameras — registers a new camera; backend should validate/connect the RTSP source */
export async function createCamera(payload) {
  const { data } = await api.post("/cameras", payload);
  return data;
}

/** PUT /cameras/:id */
export async function updateCamera(cameraId, payload) {
  const { data } = await api.put(`/cameras/${cameraId}`, payload);
  return data;
}

/** DELETE /cameras/:id */
export async function deleteCamera(cameraId) {
  await api.delete(`/cameras/${cameraId}`);
}