import { type ReactNode, type HTMLAttributes } from 'react'
import { Box } from '@chakra-ui/react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
}

export function Card({
  children,
  padding = 'md',
  hover = false,
  className,
  ...props
}: CardProps) {
  const paddingMap = padding === 'none' ? 0 : padding === 'sm' ? 4 : padding === 'lg' ? 8 : 6

  return (
    <Box
      bg="var(--core-color-surface-canvas)"
      borderWidth="1px"
      borderColor="var(--core-color-border-default)"
      rounded="0"
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
