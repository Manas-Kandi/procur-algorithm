import {
  createContext,
  type PropsWithChildren,
  useContext,
  useLayoutEffect,
} from 'react'
import {
  breakpoint,
  color,
  grid,
  motion,
  radius,
  shadow,
  space,
  typography,
} from '../tokens'

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

const CSS_VARIABLE_MAP: Array<[string, string]> = [
  ['--core-color-brand-primary', color.core.brand.primary],
  ['--core-color-brand-secondary', color.core.brand.secondary],
  ['--core-color-brand-inverse', color.core.brand.inverse],
  ['--core-color-surface-background', color.core.surface.background],
  ['--core-color-surface-canvas', color.core.surface.canvas],
  ['--core-color-surface-subtle', color.core.surface.subtle],
  ['--core-color-text-primary', color.core.text.primary],
  ['--core-color-text-muted', color.core.text.muted],
  ['--core-color-text-disabled', color.core.text.disabled],
  ['--core-color-border-default', color.core.border.default],
  ['--core-color-border-focus', color.core.border.focus],
  ['--persona-color-buyer-accent', color.persona.buyer.accent],
  ['--persona-color-seller-accent', color.persona.seller.accent],
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

export function ThemeProvider({ children }: PropsWithChildren): JSX.Element {
  useLayoutEffect(() => {
    const root = document.documentElement
    CSS_VARIABLE_MAP.forEach(([name, value]) => {
      root.style.setProperty(name, value)
    })
  }, [])

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
