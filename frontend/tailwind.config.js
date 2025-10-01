/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#1D4ED8',
          secondary: '#7C3AED',
        },
        buyer: {
          accent: '#0F766E',
        },
        seller: {
          accent: '#F97316',
        },
      },
      fontFamily: {
        sans: ['"Inter"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', '"SFMono-Regular"', 'monospace'],
      },
      borderRadius: {
        sm: '6px',
        md: '10px',
        lg: '16px',
        pill: '999px',
      },
      boxShadow: {
        '100': '0 2px 6px rgba(15, 23, 42, 0.08)',
        '200': '0 8px 20px rgba(15, 23, 42, 0.12)',
        '300': '0 16px 32px rgba(15, 23, 42, 0.16)',
      },
    },
  },
  plugins: [],
}
