// Centralized design tokens for Chakra-based system
// Brand colors, fonts, radii, spacing, and shadows

// Brand palette tuned for dark + light modes.
// 500/600 are the primary/hover levels to use for CTAs and highlights.
export const brand = {
  50: '#eff6ff',
  100: '#dbeafe',
  200: '#bfdbfe',
  300: '#93c5fd',
  400: '#60a5fa',
  500: '#3b82f6', // primary
  600: '#2563eb', // hover/active
  700: '#1d4ed8',
  800: '#1e40af',
  900: '#1e3a8a',
}

export const fonts = {
  body: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif',
  heading: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif',
  mono: 'IBM Plex Mono, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, Courier New, monospace',
}

export const radii = {
  none: '0px',
  sm: '6px',
  md: '10px',
  lg: '16px',
}

export const spacing = {
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
  16: '64px',
  20: '80px',
  24: '96px',
}

// Shadows map to existing CSS variable shadows used across the app so dark mode remains coherent.
export const shadows = {
  none: 'none',
  100: 'var(--shadow-100)',
  200: 'var(--shadow-200)',
  300: 'var(--shadow-300)',
}

// Aggregate export for convenience when wiring into ChakraProvider later.
export const appSystemTokens = {
  colors: { brand },
  fonts,
  radii,
  spacing,
  shadows,
}
