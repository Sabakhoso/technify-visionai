import { useEffect } from "react";

/**
 * Calls onOutsideClick when a mousedown happens outside the given ref.
 * Used to close dropdown/menu panels (notifications, admin menu).
 */
export function useClickOutside(ref, onOutsideClick) {
  useEffect(() => {
    function handleClick(event) {
      if (ref.current && !ref.current.contains(event.target)) {
        onOutsideClick();
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [ref, onOutsideClick]);
}
