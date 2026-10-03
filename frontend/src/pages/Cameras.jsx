import React, { useState } from "react";
import { Plus, Pencil, Trash2, RefreshCcw, VideoOff } from "lucide-react";
import { useCameras } from "../hooks/useCameras.js";
import CameraFormModal from "../components/cameras/CameraFormModal.jsx";

export default function Cameras() {
  const { cameras, status, error, addCamera, editCamera, removeCamera } = useCameras();
  const [formTarget, setFormTarget] = useState(null); // null = closed, {} = add, camera object = edit
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (camera) => {
    if (!window.confirm(`Remove ${camera.name} (${camera.id})? This cannot be undone.`)) return;
    setDeletingId(camera.id);
    try {
      await removeCamera(camera.id);
    } catch {
      window.alert("Couldn't remove this camera. Check the backend and try again.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-card">
      <div className="flex items-center justify-between p-5 border-b border-gray-100">
        <h1 className="text-lg font-semibold text-gray-900">
          Cameras <span className="text-sm text-gray-400 font-normal">({cameras.length})</span>
        </h1>
        <button
          type="button"
          onClick={() => setFormTarget({})}
          className="flex items-center gap-1.5 text-sm font-medium text-white bg-brand-blue px-3.5 py-2 rounded-lg hover:bg-brand-blue/90"
        >
          <Plus className="w-4 h-4" />
          Add Camera
        </button>
      </div>

      {status === "loading" && (
        <div className="p-10 flex items-center justify-center">
          <RefreshCcw className="w-5 h-5 text-gray-400 animate-spin" />
        </div>
      )}

      {status === "error" && (
        <div className="p-10 text-center">
          <p className="text-sm text-red-500 font-medium">Couldn't load cameras from the backend.</p>
          <p className="text-xs text-gray-400 mt-1">
            {error?.message || "Check that the API server is running and reachable."}
          </p>
        </div>
      )}

      {status === "ready" && cameras.length === 0 && (
        <div className="p-10 flex flex-col items-center justify-center gap-2 text-gray-400">
          <VideoOff className="w-6 h-6" />
          <span className="text-sm">No cameras registered yet.</span>
        </div>
      )}

      {status === "ready" &&
        cameras.map((camera) => (
          <div key={camera.id} className="flex items-center gap-4 px-5 py-3 border-b border-gray-50 last:border-b-0">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900">
                {camera.id} <span className="text-gray-400">•</span> {camera.name}
              </p>
              <p className="text-xs text-gray-400 mt-0.5">{camera.location}</p>
            </div>

            <span
              className={`text-[11px] font-semibold px-2.5 py-1 rounded-full shrink-0 ${
                camera.status === "online" ? "bg-green-50 text-green-600" : "bg-gray-100 text-gray-500"
              }`}
            >
              {camera.status === "online" ? "Online" : "Offline"}
            </span>

            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={() => setFormTarget(camera)}
                className="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50"
                title="Edit"
              >
                <Pencil className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => handleDelete(camera)}
                disabled={deletingId === camera.id}
                className="w-8 h-8 flex items-center justify-center rounded-lg border border-gray-200 text-red-500 hover:bg-red-50 disabled:opacity-50"
                title="Remove"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}

      {formTarget !== null && (
        <CameraFormModal
          camera={formTarget.id ? formTarget : null}
          onClose={() => setFormTarget(null)}
          onSubmit={(payload) => (formTarget.id ? editCamera(formTarget.id, payload) : addCamera(payload))}
        />
      )}
    </div>
  );
}