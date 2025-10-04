export const color = {
  core: {
    brand: {
      primary: '#1D4ED8',
      secondary: '#7C3AED',
      inverse: '#F8FAFC',
    },
    surface: {
      background: '#F5F7FB',
      canvas: '#FFFFFF',
      subtle: '#F1F5F9',
      elevated: '#FFFFFF',
    },
    text: {
      primary: '#111827',
      muted: '#4B5563',
      disabled: '#9CA3AF',
    },
    border: {
      default: '#D1D5DB',
      focus: '#2563EB',
    },
    data: {
      positive: '#16A34A',
      warning: '#F59E0B',
      critical: '#DC2626',
      info: '#0EA5E9',
    },
  },
  persona: {
    buyer: {
      accent: '#0F766E',
    },
    seller: {
      accent: '#F97316',
    },
  },
  status: {
    draft: '#9CA3AF',
    sourcing: '#0EA5E9',
    negotiating: '#7C3AED',
    approving: '#F59E0B',
    contracted: '#16A34A',
    provisioning: '#1D4ED8',
    atRisk: '#DC2626',
    blocked: '#B91C1C',
  },
}

// Dark mode palette with the same shape as `color`
export const colorDark: typeof color = {
  core: {
    brand: {
      primary: '#3B82F6', // slightly brighter in dark
      secondary: '#A78BFA',
      inverse: '#0B1220',
    },
    surface: {
      background: '#000000',
      canvas: '#0F0F0F',
      subtle: '#1A1A1A',
      elevated: '#141414',
    },
    text: {
      primary: '#FAFAFA',
      muted: '#A1A1AA',
      disabled: '#3F3F46',
    },
    border: {
      default: '#262626',
      focus: '#2563EB',
    },
    data: {
      positive: '#22C55E',
      warning: '#F59E0B',
      critical: '#EF4444',
      info: '#06B6D4',
    },
  },
  persona: {
    buyer: {
      accent: '#2DD4BF',
    },
    seller: {
      accent: '#FB923C',
    },
  },
  status: {
    draft: '#9CA3AF',
    sourcing: '#38BDF8',
    negotiating: '#A78BFA',
    approving: '#F59E0B',
    contracted: '#22C55E',
    provisioning: '#60A5FA',
    atRisk: '#F87171',
    blocked: '#F87171',
  },
}

export const typography = {
  font: {
    base: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    numeric: '"IBM Plex Mono", "SFMono-Regular", monospace',
  },
  sizeScale: [12, 14, 16, 18, 20, 24, 30, 36, 48] as const,
  weight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.2,
    standard: 1.4,
    relaxed: 1.6,
  },
  letterSpacing: {
    allcaps: '0.08em',
  },
}

export const space = {
  scale: [4, 8, 12, 16, 24, 32, 40, 48, 64] as const,
  inlineGutter: 24,
  blockSection: 32,
}

export const grid = {
  columns: {
    desktop: 12,
    tablet: 8,
    mobile: 4,
  },
  gap: {
    desktop: 24,
    tablet: 16,
    mobile: 12,
  },
  maxWidth: 1320,
}

export const radius = {
  sm: 6,
  md: 10,
  lg: 16,
  pill: 999,
}

export const shadow = {
  none: 'none',
  level100: '0 2px 6px rgba(15, 23, 42, 0.08)',
  level200: '0 8px 20px rgba(15, 23, 42, 0.12)',
  level300: '0 16px 32px rgba(15, 23, 42, 0.16)',
}

export const breakpoint = {
  xs: 0,
  sm: 480,
  md: 768,
  lg: 1024,
  xl: 1440,
}

export const motion = {
  duration: {
    fast: '150ms',
    base: '200ms',
  },
  easing: {
    default: 'ease-out',
    overlay: 'ease',
  },
}
