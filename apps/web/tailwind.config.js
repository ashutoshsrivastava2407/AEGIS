/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        aegis: {
          bg: "#0B0B0F",
          surface1: "#111116",
          surface2: "#16161C",
          surface3: "#1B1B22",
          border: "rgba(255, 255, 255, 0.08)",
          borderSubtle: "rgba(255, 255, 255, 0.04)",
          borderStrong: "rgba(255, 255, 255, 0.16)",
          primary: "#7C6FF2",
          primaryHover: "#9186FF",
          primarySoft: "rgba(124, 111, 242, 0.12)",
          success: "#35C98A",
          warning: "#E6A84A",
          critical: "#EF6262",
          info: "#5B9CF6",
        },
      },
      borderRadius: {
        controls: "6px",
        cards: "8px",
        panels: "10px",
        dialogs: "12px",
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
