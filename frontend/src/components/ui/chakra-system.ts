import { createSystem, defaultConfig } from '@chakra-ui/react'

// Centralized app tokens + semantic tokens for a modern dark theme
export const system = createSystem(defaultConfig, {
  theme: {
    tokens: {
      fonts: {
        body: { value: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif' },
        heading: { value: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif' },
        mono: { value: 'IBM Plex Mono, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, Courier New, monospace' },
      },
      radii: {
        sm: { value: '4px' },
        md: { value: '8px' },
        lg: { value: '12px' },
      },
      shadows: {
        100: { value: '0 1px 2px rgba(0,0,0,0.06)' },
        200: { value: '0 2px 6px rgba(0,0,0,0.08)' },
        300: { value: '0 6px 18px rgba(0,0,0,0.12)' },
      },
    },
    semanticTokens: {
      colors: {
        // Core app background/text/border
        bg: { value: { base: 'gray.50', _dark: '#0B0E12' } },
        'bg.panel': { value: { base: 'white', _dark: '#10151B' } },
        'bg.subtle': { value: { base: 'gray.50', _dark: '#0E141A' } },
        fg: { value: { base: 'gray.900', _dark: '#FAFAFA' } },
        'fg.muted': { value: { base: 'gray.600', _dark: '#A1B0BE' } },
        border: { value: { base: 'gray.200', _dark: '#1E2936' } },

        // Focus rings and brand-ish accents
        'blue.focusRing': { value: { base: 'blue.500', _dark: 'blue.400' } },
        'teal.solid': { value: { base: 'teal.500', _dark: 'teal.400' } },
        'teal.subtle': { value: { base: 'teal.50', _dark: '#0B2B2B' } },

        // Brand accents (used subtly across the app)
        'brand.solid': { value: { base: 'blue.600', _dark: '#2EC4B6' } },
        'brand.subtle': { value: { base: 'blue.50', _dark: '#0F2324' } },
        'brand.emphasized': { value: { base: 'blue.300', _dark: '#1E4E6A' } },
        'brand.fg': { value: { base: 'blue.700', _dark: '#7FE6DE' } },

        // Severity palettes for SmartAlert
        'red.subtle': { value: { base: 'red.50', _dark: 'red.900' } },
        'red.emphasized': { value: { base: 'red.200', _dark: 'red.700' } },
        'red.fg': { value: { base: 'red.700', _dark: 'red.200' } },
        'yellow.subtle': { value: { base: 'yellow.50', _dark: 'yellow.900' } },
        'yellow.emphasized': { value: { base: 'yellow.200', _dark: 'yellow.700' } },
        'yellow.fg': { value: { base: 'yellow.800', _dark: 'yellow.200' } },
        'green.subtle': { value: { base: 'green.50', _dark: 'green.900' } },
        'green.emphasized': { value: { base: 'green.200', _dark: 'green.700' } },
        'green.fg': { value: { base: 'green.700', _dark: 'green.200' } },
        'blue.subtle': { value: { base: 'blue.50', _dark: '#0B2447' } },
        'blue.emphasized': { value: { base: 'blue.200', _dark: '#233554' } },
        'blue.fg': { value: { base: 'blue.700', _dark: 'blue.200' } },
      },
    },
    layerStyles: {
      card: {
        value: {
          bg: { base: 'white', _dark: '#10151B' },
          borderWidth: '1px',
          borderColor: { base: 'gray.200', _dark: '#1E2936' },
          borderRadius: 'lg',
          boxShadow: '200',
          transitionProperty: 'transform, box-shadow',
          transitionDuration: '150ms',
          transitionTimingFunction: 'ease',
          _before: {
            content: '""',
            position: 'absolute',
            inset: 0,
            pointerEvents: 'none',
            borderRadius: 'inherit',
            bg: { base: 'transparent', _dark: 'linear-gradient(180deg, rgba(255,255,255,0.02), rgba(0,0,0,0))' },
          },
          position: 'relative',
          _hover: {
            boxShadow: '300',
            transform: 'translateY(-1px)',
          },
        },
      },
    },
  },
})
