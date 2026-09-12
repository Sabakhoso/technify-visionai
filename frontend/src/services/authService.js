import api from "./api.js";

/** GET /auth/me — the logged-in user's profile */
export async function getCurrentUser() {
  const { data } = await api.get("/auth/me");
  return data;
}

/** Clears the session and sends the user to login. */
export function logout() {
  localStorage.removeItem("access_token");
  window.location.assign("/login");
}
