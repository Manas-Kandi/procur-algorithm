import { type ReactNode, type HTMLAttributes } from 'react'
import { Box } from '@chakra-ui/react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
  variant?: 'canvas' | 'subtle' | 'elevated'
  elevation?: 'none' | '100' | '200' | '300'
  rounded?: 'none' | 'sm' | 'md' | 'lg'
}

export function Card({
  children,
  padding = 'md',
  hover = false,
  variant = 'canvas',
  elevation = '100',
  rounded = 'md',
  className,
  ...props
}: CardProps) {
  const paddingMap = padding === 'none' ? 0 : padding === 'sm' ? 4 : padding === 'lg' ? 8 : 6
  const bgMap = {
    canvas: 'var(--core-color-surface-canvas)',
    subtle: 'var(--core-color-surface-subtle)',
    elevated: 'var(--core-color-surface-canvas)',
  } as const
  const radiusMap = {
    none: '0',
    sm: '6px',
    md: '10px',
    lg: '16px',
  } as const
  const shadowMap = {
    none: 'none',
    '100': 'var(--shadow-100)',
    '200': 'var(--shadow-200)',
    '300': 'var(--shadow-300)',
  } as const

  return (
    <Box
      bg={bgMap[variant]}
      borderWidth="1px"
      borderColor="var(--core-color-border-default)"
      borderRadius={radiusMap[rounded]}
      boxShadow={shadowMap[elevation]}
      p={paddingMap}
      transition="all 150ms"
      cursor={hover ? 'pointer' : undefined}
      _hover={hover ? { borderColor: 'var(--core-color-border-focus)' } : undefined}
      className={className}
      {...props}
    >
      {children}
    </Box>
  )
}
