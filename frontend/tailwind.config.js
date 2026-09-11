/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#0B1739",
          light: "#101d45",
          active: "#1e40af",
        },
        brand: {
          blue: "#2563eb",
          "blue-light": "#eff6ff",
          green: "#16a34a",
          "green-light": "#f0fdf4",
          purple: "#7c3aed",
          "purple-light": "#f5f3ff",
          orange: "#ea580c",
          "orange-light": "#fff7ed",
          cyan: "#0891b2",
          "cyan-light": "#ecfeff",
        },
        severity: {
          critical: "#dc2626",
          "critical-bg": "#fee2e2",
          high: "#ea580c",
          "high-bg": "#ffedd5",
          medium: "#ca8a04",
          "medium-bg": "#fef9c3",
          low: "#6b7280",
          "low-bg": "#f3f4f6",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "sans-serif",
        ],
      },
      boxShadow: {
        card: "0 1px 3px rgba(16, 24, 40, 0.06), 0 1px 2px rgba(16, 24, 40, 0.04)",
      },
      borderRadius: {
        xl: "12px",
      },
    },
  },
  plugins: [],
};
