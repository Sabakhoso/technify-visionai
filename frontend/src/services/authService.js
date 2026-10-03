import { supabase } from "../lib/supabaseClient.js";
import api from "./api.js";

/** GET /auth/me — verifies the current Supabase token against the backend */
export async function getCurrentUser() {
  const { data } = await api.get("/auth/me");
  return data; // { authenticated, user_id, email, role, app_role, organization_id }
}

/** Signs out of Supabase and clears the session everywhere. */
export async function logout() {
  await supabase.auth.signOut();
  window.location.assign("/login");
}
/** POST /auth/register — public: creates a new organization + its first admin user */
export async function register(payload) {
  const { data } = await api.post("/auth/register", payload);
  return data;
}