import {
  createContext,
  type PropsWithChildren,
  useContext,
  useEffect,
} from 'react'
import {
  breakpoint,
  color,
  colorDark,
  grid,
  motion,
  radius,
  shadow,
  space,
  typography,
} from '../tokens'
import { useTheme } from 'next-themes'

export interface DesignTokens {
  color: typeof color
  typography: typeof typography
  space: typeof space
  grid: typeof grid
  radius: typeof radius
  shadow: typeof shadow
  breakpoint: typeof breakpoint
  motion: typeof motion
}

const tokenContext = createContext<DesignTokens>({
  color,
  typography,
  space,
  grid,
  radius,
  shadow,
  breakpoint,
  motion,
})

function getCssVariableMap(active: typeof color): Array<[string, string]> {
  return [
    ['--core-color-brand-primary', active.core.brand.primary],
    ['--core-color-brand-secondary', active.core.brand.secondary],
    ['--core-color-brand-inverse', active.core.brand.inverse],
    ['--core-color-surface-background', active.core.surface.background],
    ['--core-color-surface-canvas', active.core.surface.canvas],
    ['--core-color-surface-subtle', active.core.surface.subtle],
    ['--core-color-text-primary', active.core.text.primary],
    ['--core-color-text-muted', active.core.text.muted],
    ['--core-color-text-disabled', active.core.text.disabled],
    ['--core-color-border-default', active.core.border.default],
    ['--core-color-border-focus', active.core.border.focus],
    ['--persona-color-buyer-accent', active.persona.buyer.accent],
    ['--persona-color-seller-accent', active.persona.seller.accent],
    ['--shadow-100', shadow.level100],
    ['--shadow-200', shadow.level200],
    ['--shadow-300', shadow.level300],
    ['--radius-sm', `${radius.sm}px`],
    ['--radius-md', `${radius.md}px`],
    ['--radius-lg', `${radius.lg}px`],
    ['--radius-pill', `${radius.pill}px`],
    ['--font-family-base', typography.font.base],
    ['--font-family-numeric', typography.font.numeric],
    ['--motion-duration-fast', motion.duration.fast],
    ['--motion-duration-base', motion.duration.base],
    ['--motion-easing-default', motion.easing.default],
    ['--motion-easing-overlay', motion.easing.overlay],
  ]
}

export function ThemeProvider({ children }: PropsWithChildren): JSX.Element {
  const { resolvedTheme } = useTheme()

  useEffect(() => {
    const active = resolvedTheme === 'dark' ? colorDark : color
    const root = document.documentElement
    const map = getCssVariableMap(active)
    map.forEach(([name, value]) => {
      root.style.setProperty(name, value)
    })
  }, [resolvedTheme])

  return (
    <tokenContext.Provider
      value={{
        color,
        typography,
        space,
        grid,
        radius,
        shadow,
        breakpoint,
        motion,
      }}
    >
      {children}
    </tokenContext.Provider>
  )
}

export function useTokens(): DesignTokens {
  return useContext(tokenContext)
}
