import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      // Design tokens from CaseFlow spec Section 5.1
      fontSize: {
        xs: ["13px", { lineHeight: "1.4" }],
        sm: ["14px", { lineHeight: "1.5" }],
        base: ["15px", { lineHeight: "1.6" }],
        lg: ["18px", { lineHeight: "1.5" }],
        xl: ["22px", { lineHeight: "1.3" }],
      },
      fontWeight: {
        normal: "400",
        medium: "500",
        // 600/700 intentionally excluded — too heavy for dense dashboard
      },
      borderRadius: {
        md: "8px",
        lg: "12px",
      },
      borderWidth: {
        DEFAULT: "0.5px",
      },
      colors: {
        // Semantic colors — map to meaning, not decoration
        critical: {
          DEFAULT: "#DC2626",
          light: "#FEF2F2",
          border: "#FECACA",
        },
        info: {
          DEFAULT: "#2563EB",
          light: "#EFF6FF",
          border: "#BFDBFE",
        },
        warning: {
          DEFAULT: "#D97706",
          light: "#FFFBEB",
          border: "#FDE68A",
        },
        neutral: {
          50: "#FAFAFA",
          100: "#F4F4F5",
          200: "#E4E4E7",
          300: "#D4D4D8",
          400: "#A1A1AA",
          500: "#71717A",
          600: "#52525B",
          700: "#3F3F46",
          800: "#27272A",
          900: "#18181B",
        },
        // Weakness legend reuses same colors consistently
        weakness: {
          law: "#DC2626",      // red — same as critical
          facts: "#D97706",    // amber — same as warning
          data: "#2563EB",     // blue — same as info
          contradiction: "#7C3AED",
          procedure: "#059669",
        },
      },
      spacing: {
        // rem rhythm for vertical; px for internal gaps
        "4": "1rem",
        "6": "1.5rem",
        "8": "2rem",
      },
    },
  },
  plugins: [],
} satisfies Config;
