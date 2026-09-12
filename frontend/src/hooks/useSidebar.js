import { useState } from "react";

export function useSidebar() {
  const [expandedKey, setExpandedKey] = useState(null);

  const toggleExpanded = (key) => {
    setExpandedKey((prev) => (prev === key ? null : key));
  };

  return { expandedKey, toggleExpanded };
}
