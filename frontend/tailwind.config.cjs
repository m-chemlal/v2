/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0b1220",
        panel: "#131b2c",
        accent: "#3b82f6",
        accentMuted: "#1f2937",
        success: "#10b981",
        warning: "#f59e0b",
        danger: "#ef4444"
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
