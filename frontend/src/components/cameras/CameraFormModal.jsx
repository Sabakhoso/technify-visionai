import React, { useState } from "react";
import Modal from "../common/Modal.jsx";

export default function CameraFormModal({ camera, onClose, onSubmit }) {
  const isEdit = Boolean(camera);
  const [name, setName] = useState(camera?.name || "");
  const [location, setLocation] = useState(camera?.location || "");
  const [rtspUrl, setRtspUrl] = useState(camera?.rtsp_url || "0");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await onSubmit({ name, location, rtsp_url: rtspUrl, status: "online" });
      onClose();
    } catch (err) {
      setError(err?.response?.data?.detail || "Couldn't save this camera.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal title={isEdit ? "Edit Camera" : "Add Camera"} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Camera Name</label>
          <input
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="e.g. Office Entrance"
            required
            className="w-full text-sm text-gray-700 border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-blue/30"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Location</label>
          <input
            type="text"
            value={location}
            onChange={(event) => setLocation(event.target.value)}
            placeholder="e.g. Ground Floor"
            required
            className="w-full text-sm text-gray-700 border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-blue/30"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Camera Source (Webcam or RTSP Stream)</label>
          <input
            type="text"
            value={rtspUrl}
            onChange={(event) => setRtspUrl(event.target.value)}
            placeholder="0 (for built-in webcam) or rtsp://..."
            required
            className="w-full text-sm text-gray-700 border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-blue/30"
          />
          <p className="text-[11px] text-gray-400 mt-1">
            Tip: Enter <strong>0</strong> to connect to your built-in webcam, or enter an RTSP / HTTP camera feed URL.
          </p>
        </div>

        {error && <p className="text-xs text-red-500">{error}</p>}

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="text-sm text-gray-600 px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className="text-sm text-white bg-brand-blue px-4 py-2 rounded-lg hover:bg-brand-blue/90 disabled:opacity-50"
          >
            {saving ? "Saving…" : isEdit ? "Save Changes" : "Add Camera"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
