import { useCallback, useEffect, useState } from "react";
import { getOrganizations, updateOrganization } from "../services/organizationsService.js";

/**
 * There's no login right now, so there's no "current org" from a session —
 * this uses the first organization the backend returns, matching the same
 * fallback the Cameras endpoint uses when it creates a default org.
 */
export function useOrganization() {
  const [organization, setOrganization] = useState(null);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getOrganizations()
      .then((data) => {
        if (cancelled) return;
        setOrganization(data[0] || null);
        setStatus("ready");
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err);
        setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const save = useCallback(
    async (payload) => {
      if (!organization) return;
      setSaving(true);
      try {
        const updated = await updateOrganization(organization.id, payload);
        setOrganization(updated);
        return updated;
      } finally {
        setSaving(false);
      }
    },
    [organization]
  );

  return { organization, status, error, saving, save };
}