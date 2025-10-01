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
          primary: 'var(--core-color-brand-primary)',
          secondary: 'var(--core-color-brand-secondary)',
          inverse: 'var(--core-color-brand-inverse)',
        },
        surface: {
          background: 'var(--core-color-surface-background)',
          canvas: 'var(--core-color-surface-canvas)',
          subtle: 'var(--core-color-surface-subtle)',
        },
        text: {
          primary: 'var(--core-color-text-primary)',
          muted: 'var(--core-color-text-muted)',
          disabled: 'var(--core-color-text-disabled)',
        },
        data: {
          positive: 'var(--core-color-data-positive)',
          warning: 'var(--core-color-data-warning)',
          critical: 'var(--core-color-data-critical)',
          info: 'var(--core-color-data-info)',
        },
        persona: {
          buyer: 'var(--persona-color-buyer-accent)',
          seller: 'var(--persona-color-seller-accent)',
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
        100: 'var(--shadow-100)',
        200: 'var(--shadow-200)',
        300: 'var(--shadow-300)',
      },
    },
  },
  plugins: [],
}
