import api from "./api.js";

/**
 * GET /organizations
 * Response: array of { id, name, slug, is_active, plan, timezone, settings, created_at }
 */
export async function getOrganizations() {
  const { data } = await api.get("/organizations");
  return data;
}

/** PATCH /organizations/:id — accepts any of { name, timezone, settings } */
export async function updateOrganization(organizationId, payload) {
  const { data } = await api.patch(`/organizations/${organizationId}`, payload);
  return data;
}