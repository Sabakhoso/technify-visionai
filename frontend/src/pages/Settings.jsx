import React, { useEffect, useState } from "react";
import { RefreshCcw, Check } from "lucide-react";
import { useOrganization } from "../hooks/useOrganization.js";

const TIMEZONES = [
  "UTC",
  "Asia/Karachi",
  "America/New_York",
  "America/Los_Angeles",
  "Europe/London",
  "Asia/Dubai",
  "Asia/Kolkata",
];

const NOTIFICATION_KEYS = [
  { key: "notify_email", label: "Email notifications" },
  { key: "notify_sms", label: "SMS notifications" },
  { key: "notify_whatsapp", label: "WhatsApp notifications" },
];

export default function Settings() {
  const { organization, status, error, saving, save } = useOrganization();
  const [name, setName] = useState("");
  const [timezone, setTimezone] = useState("UTC");
  const [notifications, setNotifications] = useState({});
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!organization) return;
    setName(organization.name);
    setTimezone(organization.timezone);
    setNotifications({
      notify_email: organization.settings?.notify_email ?? true,
      notify_sms: organization.settings?.notify_sms ?? false,
      notify_whatsapp: organization.settings?.notify_whatsapp ?? false,
    });
  }, [organization]);

  const toggleNotification = (key) => {
    setNotifications((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaved(false);
    await save({
      name,
      timezone,
      settings: { ...organization.settings, ...notifications },
    });
    setSaved(true);
  };

  if (status === "loading") {
    return (
      <div className="bg-white rounded-xl border border-gray-100 shadow-card p-10 flex items-center justify-center">
        <RefreshCcw className="w-5 h-5 text-gray-400 animate-spin" />
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="bg-white rounded-xl border border-gray-100 shadow-card p-10 text-center">
        <p className="text-sm text-red-500 font-medium">Couldn't load settings from the backend.</p>
        <p className="text-xs text-gray-400 mt-1">
          {error?.message || "Check that the API server is running and reachable."}
        </p>
      </div>
    );
  }

  if (!organization) {
    return (
      <div className="bg-white rounded-xl border border-gray-100 shadow-card p-10 text-center text-sm text-gray-400">
        No organization found yet — add a camera first, which creates a default one.
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5">
        <h1 className="text-lg font-semibold text-gray-900 mb-1">Organization</h1>
        <p className="text-sm text-gray-400 mb-4">
          Plan: <span className="font-medium text-gray-600 capitalize">{organization.plan}</span>
        </p>

        <div className="space-y-4 max-w-sm">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Organization Name</label>
            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
              className="w-full text-sm text-gray-700 border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-blue/30"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1">Timezone</label>
            <select
              value={timezone}
              onChange={(event) => setTimezone(event.target.value)}
              className="w-full text-sm text-gray-700 border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-blue/30"
            >
              {TIMEZONES.map((tz) => (
                <option key={tz} value={tz}>
                  {tz}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-card p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-4">Notification Preferences</h2>
        <div className="space-y-3 max-w-sm">
          {NOTIFICATION_KEYS.map(({ key, label }) => (
            <label key={key} className="flex items-center justify-between text-sm text-gray-700">
              {label}
              <input
                type="checkbox"
                checked={Boolean(notifications[key])}
                onChange={() => toggleNotification(key)}
                className="w-4 h-4 accent-brand-blue"
              />
            </label>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={saving}
          className="bg-brand-blue text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-brand-blue/90 disabled:opacity-50"
        >
          {saving ? "Saving…" : "Save Changes"}
        </button>
        {saved && !saving && (
          <span className="flex items-center gap-1.5 text-sm text-green-600">
            <Check className="w-4 h-4" /> Saved
          </span>
        )}
      </div>
    </form>
  );
}