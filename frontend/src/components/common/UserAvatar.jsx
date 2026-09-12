import React from "react";

/** Renders the user's real photo if one exists, otherwise their initials. */
export default function UserAvatar({ name, photoUrl, size = 36 }) {
  if (photoUrl) {
    return (
      <img
        src={photoUrl}
        alt={name || "User"}
        className="rounded-full object-cover"
        style={{ width: size, height: size }}
      />
    );
  }

  const initials = (name || "")
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");

  return (
    <div
      className="rounded-full bg-brand-blue text-white flex items-center justify-center font-semibold text-sm shrink-0"
      style={{ width: size, height: size }}
    >
      {initials || "?"}
    </div>
  );
}
