import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary:   "#060a13",
          secondary: "#0c1220",
          tertiary:  "#141c30",
          card:      "#0f1929",
        },
        accent: {
          blue:   "#2e6cf6",
          green:  "#00d4aa",
          red:    "#ff4757",
          amber:  "#ffb830",
          cyan:   "#00e5ff",
          purple: "#a855f7",
        },
        border: {
          DEFAULT: "#1e2d4a",
          bright:  "#2e4a7a",
        },
        text: {
          primary:   "#e8edf5",
          secondary: "#8899bb",
          muted:     "#4a5a7a",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
